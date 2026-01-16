"""
Analyze videos using Gemini 2.5 Flash with multi-video requests.

Sends up to 10 videos per request to reduce file processing overhead.
"""
import asyncio
import logging
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from supabase import create_client
from google import genai
from google.genai import types

# Set up logging with UTF-8 encoding for Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analyze_multivideo.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Gemini 2.5 Flash model
MODEL = "gemini-2.5-flash"

# Load prompt
_PROMPTS_DIR = Path(__file__).parent.parent / "config" / "prompts"
EDUCATIONAL_PROMPT = (_PROMPTS_DIR / "educational.txt").read_text(encoding="utf-8")

# Multi-video prompt wrapper
MULTI_VIDEO_PROMPT = """You are analyzing {count} videos. Analyze each video SEPARATELY and return a JSON array with {count} objects.

Each object in the array should follow this exact structure for the corresponding video:
{base_prompt}

IMPORTANT:
- Return a JSON array with exactly {count} objects
- The first object is for Video 1, second for Video 2, etc.
- Each object should have the complete analysis structure
- Return ONLY the JSON array, no other text

Videos are provided in order: Video 1, Video 2, ... Video {count}
"""


@dataclass
class BatchResult:
    video_id: str
    db_id: str
    success: bool
    analysis: dict = None
    error: str = None


def get_unanalyzed_videos(client, niche_mode: str = None, limit: int = 1000) -> list[dict]:
    """Query Supabase for videos that need analysis."""
    query = (
        client.table('posts')
        .select('id, platform, platform_id, video_url, author_username, local_file_path, niche_mode')
        .is_('analysis', 'null')
        .not_.is_('local_file_path', 'null')
        .order('scraped_at', desc=True)
        .limit(limit)
    )

    if niche_mode:
        query = query.eq('niche_mode', niche_mode)

    result = query.execute()
    return result.data if result.data else []


def chunk_list(lst: list, chunk_size: int) -> list[list]:
    """Split a list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


async def analyze_video_batch(
    gemini_client,
    videos: list[dict],
    batch_num: int,
    total_batches: int
) -> list[BatchResult]:
    """Analyze a batch of up to 10 videos in a single request."""

    results = []
    valid_videos = []

    # Filter to videos that exist
    for video in videos:
        file_path = Path(video['local_file_path'])
        if not file_path.exists():
            logger.warning(f"File missing: {file_path.name}")
            results.append(BatchResult(
                video_id=video['platform_id'],
                db_id=video['id'],
                success=False,
                error="File missing"
            ))
        else:
            valid_videos.append(video)

    if not valid_videos:
        return results

    logger.info(f"[Batch {batch_num}/{total_batches}] Analyzing {len(valid_videos)} videos in single request")

    try:
        # Upload all video files
        uploaded_files = []
        for video in valid_videos:
            file_path = Path(video['local_file_path'])
            logger.info(f"  Uploading: {file_path.name}")
            video_file = gemini_client.files.upload(file=file_path)
            uploaded_files.append(video_file)

        # Wait for all files to be ready
        logger.info(f"  Waiting for {len(uploaded_files)} files to process...")
        max_wait = 180  # 3 minutes for batch
        wait_interval = 5
        waited = 0

        while waited < max_wait:
            all_ready = True
            for i, vf in enumerate(uploaded_files):
                if vf.state.name != "ACTIVE":
                    uploaded_files[i] = gemini_client.files.get(name=vf.name)
                    if uploaded_files[i].state.name != "ACTIVE":
                        all_ready = False

            if all_ready:
                break

            logger.info(f"  Waiting... ({waited}s)")
            time.sleep(wait_interval)
            waited += wait_interval

        # Check if all files are ready
        ready_count = sum(1 for vf in uploaded_files if vf.state.name == "ACTIVE")
        if ready_count < len(uploaded_files):
            logger.warning(f"  Only {ready_count}/{len(uploaded_files)} files ready after {max_wait}s")

        logger.info(f"  All {len(uploaded_files)} files ready, sending to Gemini 2.5 Flash...")

        # Build multi-video prompt
        prompt = MULTI_VIDEO_PROMPT.format(
            count=len(valid_videos),
            base_prompt=EDUCATIONAL_PROMPT
        )

        # Build content parts: all videos first, then prompt
        parts = []
        for i, vf in enumerate(uploaded_files):
            if vf.state.name == "ACTIVE":
                parts.append(types.Part.from_uri(
                    file_uri=vf.uri,
                    mime_type=vf.mime_type,
                ))
        parts.append(types.Part.from_text(text=prompt))

        # Send request
        response = gemini_client.models.generate_content(
            model=MODEL,
            contents=[
                types.Content(
                    role="user",
                    parts=parts,
                ),
            ],
        )

        # Clean up files
        for vf in uploaded_files:
            try:
                gemini_client.files.delete(name=vf.name)
            except:
                pass

        # Parse response
        response_text = response.text.strip()
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])

        try:
            analyses = json.loads(response_text)
            if not isinstance(analyses, list):
                analyses = [analyses]

            logger.info(f"  Got {len(analyses)} analyses from response")

            # Match analyses to videos
            for i, video in enumerate(valid_videos):
                if i < len(analyses):
                    results.append(BatchResult(
                        video_id=video['platform_id'],
                        db_id=video['id'],
                        success=True,
                        analysis=analyses[i]
                    ))
                else:
                    results.append(BatchResult(
                        video_id=video['platform_id'],
                        db_id=video['id'],
                        success=False,
                        error="No analysis returned for this video"
                    ))

        except json.JSONDecodeError as e:
            logger.error(f"  Failed to parse JSON: {e}")
            for video in valid_videos:
                results.append(BatchResult(
                    video_id=video['platform_id'],
                    db_id=video['id'],
                    success=False,
                    error=f"JSON parse error: {e}"
                ))

    except Exception as e:
        logger.error(f"  Batch failed: {e}")
        for video in valid_videos:
            results.append(BatchResult(
                video_id=video['platform_id'],
                db_id=video['id'],
                success=False,
                error=str(e)
            ))

    return results


async def run_analysis(
    niche_mode: str = None,
    limit: int = None,
    videos_per_batch: int = 10,
    workers: int = 5,
    dry_run: bool = False,
    loop_until_done: bool = False
):
    """Run Gemini 2.5 Flash multi-video analysis."""

    # Connect to Supabase
    supabase = create_client(settings.supabase_url, settings.supabase_key)

    # Initialize Gemini client
    gemini = genai.Client(api_key=settings.gemini_api_key)

    logger.info(f"Using Gemini 2.5 Flash: {MODEL}")
    logger.info(f"Videos per request: {videos_per_batch}")
    logger.info(f"Concurrent batches: {workers}")

    total_analyzed = 0
    total_failed = 0
    round_num = 0

    semaphore = asyncio.Semaphore(workers)

    while True:
        round_num += 1

        # Get unanalyzed videos
        logger.info(f"[Round {round_num}] Querying unanalyzed videos...")
        videos = get_unanalyzed_videos(supabase, niche_mode, limit or 1000)

        if limit:
            videos = videos[:limit]

        total = len(videos)
        logger.info(f"[Round {round_num}] Found {total} unanalyzed videos")

        if total == 0:
            if round_num == 1:
                logger.info("Nothing to analyze!")
            else:
                logger.info(f"All videos analyzed! Completed {round_num - 1} rounds.")
            break

        if dry_run:
            logger.info("DRY RUN - would analyze these videos:")
            for v in videos[:20]:
                logger.info(f"  {v['platform']}/{v['platform_id']}")
            if total > 20:
                logger.info(f"  ... and {total - 20} more")
            return

        # Split into batches of videos_per_batch
        batches = chunk_list(videos, videos_per_batch)
        total_batches = len(batches)

        logger.info(f"[Round {round_num}] Processing {total} videos in {total_batches} batches ({videos_per_batch} videos each)")
        logger.info(f"Estimated: {total_batches} API requests instead of {total} (10x reduction)")

        async def process_batch(batch, batch_num):
            async with semaphore:
                return await analyze_video_batch(gemini, batch, batch_num, total_batches)

        # Process all batches
        tasks = [process_batch(batch, i + 1) for i, batch in enumerate(batches)]
        all_results = await asyncio.gather(*tasks)

        # Flatten results and update database
        analyzed = 0
        failed = 0

        for batch_results in all_results:
            for result in batch_results:
                if result.success:
                    # Update Supabase
                    supabase.table('posts').update({
                        'analysis': result.analysis,
                        'analyzed_at': datetime.now(timezone.utc).isoformat()
                    }).eq('id', result.db_id).execute()

                    analyzed += 1

                    # Log summary
                    edu = result.analysis.get('educational', {})
                    logger.info(
                        f"  [OK] {result.video_id}: "
                        f"Clarity={edu.get('explanation_clarity', '?')}, "
                        f"Value={edu.get('educational_value', '?')}"
                    )
                else:
                    failed += 1
                    logger.warning(f"  [FAIL] {result.video_id}: {result.error}")

        total_analyzed += analyzed
        total_failed += failed

        logger.info(f"[Round {round_num}] Complete: {analyzed} analyzed, {failed} failed")
        logger.info(f"Cumulative: {total_analyzed} analyzed, {total_failed} failed")

        if not loop_until_done:
            break

        logger.info("Starting next round in 5 seconds...")
        await asyncio.sleep(5)

    # Final summary
    logger.info("=" * 60)
    logger.info("Multi-video analysis complete!")
    logger.info(f"  Rounds: {round_num}")
    logger.info(f"  Total analyzed: {total_analyzed}")
    logger.info(f"  Total failed: {total_failed}")
    logger.info("=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Analyze videos with Gemini 2.5 Flash (multi-video)')
    parser.add_argument('--niche', type=str, choices=['entertainment', 'data_engineering'],
                        help='Filter by niche mode')
    parser.add_argument('--limit', type=int, help='Limit number of videos')
    parser.add_argument('--batch-size', type=int, default=10,
                        help='Videos per request (max 10, default: 10)')
    parser.add_argument('--workers', type=int, default=5,
                        help='Concurrent batches (default: 5)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be analyzed')
    parser.add_argument('--loop', action='store_true',
                        help='Keep running until all done')
    args = parser.parse_args()

    if not settings.gemini_api_key:
        logger.error("GEMINI_API_KEY not set")
        sys.exit(1)

    batch_size = min(args.batch_size, 10)  # Cap at 10

    logger.info("=" * 60)
    logger.info("GEMINI 2.5 FLASH MULTI-VIDEO ANALYSIS")
    logger.info(f"Model: {MODEL}")
    logger.info(f"Videos per request: {batch_size}")
    logger.info(f"Concurrent batches: {args.workers}")
    logger.info("=" * 60)

    asyncio.run(run_analysis(
        niche_mode=args.niche,
        limit=args.limit,
        videos_per_batch=batch_size,
        workers=args.workers,
        dry_run=args.dry_run,
        loop_until_done=args.loop
    ))


if __name__ == "__main__":
    main()
