"""
Analyze videos that have been downloaded but not yet analyzed.

Queries Supabase for posts with local_file_path but no analysis,
sends them to Gemini in parallel, and updates Supabase with results.
"""
import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from supabase import create_client

# Set up logging with UTF-8 encoding for Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analyze_unanalyzed.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    video_id: str
    success: bool
    message: str


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


async def analyze_single_video(
    video: dict,
    client,
    default_mode: str,
    semaphore: asyncio.Semaphore,
    index: int,
    total: int
) -> AnalysisResult:
    """Analyze a single video with semaphore-controlled concurrency."""
    from src.analyzer.gemini import GeminiAnalyzer

    async with semaphore:
        file_path = Path(video['local_file_path'])
        video_id = video['id']

        # Check if file exists
        if not file_path.exists():
            logger.warning(f"[{index}/{total}] File missing: {file_path}")
            return AnalysisResult(video_id, False, "missing")

        logger.info(f"[{index}/{total}] Analyzing: {video['author_username']} - {file_path.name}")

        try:
            # Use video's niche_mode if available
            video_niche = video.get('niche_mode') or default_mode
            analyzer = GeminiAnalyzer(niche_mode=video_niche)

            # Run Gemini analysis
            analysis = await analyzer.analyze_video(file_path)

            if analysis.success:
                analysis_data = analysis.to_dict()

                # Update Supabase
                client.table('posts').update({
                    'analysis': analysis_data,
                    'analyzed_at': datetime.now(timezone.utc).isoformat()
                }).eq('id', video_id).execute()

                # Log key metrics based on niche
                if video_niche == 'data_engineering':
                    edu = analysis_data.get('educational', {})
                    logger.info(
                        f"  [OK] Clarity: {edu.get('explanation_clarity', 0)}/10, "
                        f"Depth: {edu.get('technical_depth', 0)}/10, "
                        f"Value: {edu.get('educational_value', 0)}/10"
                    )
                else:
                    hook = analysis_data.get('hook', {})
                    trends = analysis_data.get('trends', {})
                    logger.info(
                        f"  [OK] Hook: {hook.get('hook_strength', 0)}/10, "
                        f"Viral: {trends.get('viral_potential_score', 0)}/10"
                    )

                return AnalysisResult(video_id, True, "analyzed")
            else:
                logger.error(f"  [FAIL] Analysis failed: {analysis.error}")
                return AnalysisResult(video_id, False, "failed")

        except Exception as e:
            logger.error(f"  [FAIL] Error: {e}")
            return AnalysisResult(video_id, False, "error")


async def run_analysis(
    niche_mode: str = None,
    limit: int = None,
    workers: int = 10,
    dry_run: bool = False,
    loop_until_done: bool = False
):
    """Run Gemini analysis on unanalyzed videos with parallel processing."""

    # Connect to Supabase
    client = create_client(settings.supabase_url, settings.supabase_key)

    total_analyzed = 0
    total_failed = 0
    total_missing = 0
    batch_num = 0

    # Create semaphore for concurrency control
    semaphore = asyncio.Semaphore(workers)

    while True:
        batch_num += 1

        # Get unanalyzed videos
        logger.info(f"[Batch {batch_num}] Querying unanalyzed videos (niche_mode={niche_mode})...")
        videos = get_unanalyzed_videos(client, niche_mode, limit or 1000)

        if limit:
            videos = videos[:limit]

        total = len(videos)
        logger.info(f"[Batch {batch_num}] Found {total} unanalyzed videos")

        if total == 0:
            if batch_num == 1:
                logger.info("Nothing to analyze!")
            else:
                logger.info(f"All videos analyzed! Completed {batch_num - 1} batches.")
            break

        if dry_run:
            logger.info("DRY RUN - would analyze these videos:")
            for v in videos[:10]:
                logger.info(f"  {v['platform']}/{v['platform_id']} - {v['local_file_path']}")
            if total > 10:
                logger.info(f"  ... and {total - 10} more")
            return

        default_mode = niche_mode or "data_engineering"

        logger.info(f"[Batch {batch_num}] Starting PARALLEL analysis of {total} videos")
        logger.info(f"Workers: {workers} concurrent")
        logger.info(f"Default niche mode: {default_mode}")
        logger.info(f"Estimated time: ~{total * 20 / workers / 60:.1f} minutes (at ~20s/video)")

        # Create tasks for all videos
        tasks = [
            analyze_single_video(video, client, default_mode, semaphore, i + 1, total)
            for i, video in enumerate(videos)
        ]

        # Run all tasks concurrently (semaphore limits actual concurrency)
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Count results
        analyzed = sum(1 for r in results if isinstance(r, AnalysisResult) and r.success)
        failed = sum(1 for r in results if isinstance(r, AnalysisResult) and not r.success and r.message == "failed")
        missing = sum(1 for r in results if isinstance(r, AnalysisResult) and r.message == "missing")
        errors = sum(1 for r in results if isinstance(r, Exception))

        total_analyzed += analyzed
        total_failed += failed + errors
        total_missing += missing

        logger.info(f"[Batch {batch_num}] Complete: {analyzed} analyzed, {failed + errors} failed, {missing} missing")
        logger.info(f"Cumulative totals: {total_analyzed} analyzed, {total_failed} failed, {total_missing} missing")

        # If not looping, break after first batch
        if not loop_until_done:
            break

        # Small delay between batches
        logger.info("Starting next batch in 5 seconds...")
        await asyncio.sleep(5)

    # Final summary
    logger.info("=" * 60)
    logger.info("All analysis complete!")
    logger.info(f"  Batches processed: {batch_num}")
    logger.info(f"  Total analyzed: {total_analyzed}")
    logger.info(f"  Total failed: {total_failed}")
    logger.info(f"  Total missing files: {total_missing}")
    logger.info("=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Analyze unanalyzed videos with Gemini (parallel)')
    parser.add_argument('--niche', type=str, choices=['entertainment', 'data_engineering'],
                        help='Filter by niche mode')
    parser.add_argument('--limit', type=int, help='Limit number of videos to analyze')
    parser.add_argument('--workers', type=int, default=10,
                        help='Number of parallel workers (default: 10)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be analyzed without actually doing it')
    parser.add_argument('--loop', action='store_true',
                        help='Keep running until all videos are analyzed')
    args = parser.parse_args()

    # Check for Gemini API key
    if not settings.gemini_api_key:
        logger.error("GEMINI_API_KEY not set in .env file")
        sys.exit(1)

    logger.info(f"Starting parallel analysis with {args.workers} workers")

    asyncio.run(run_analysis(
        niche_mode=args.niche,
        limit=args.limit,
        workers=args.workers,
        dry_run=args.dry_run,
        loop_until_done=args.loop
    ))


if __name__ == "__main__":
    main()
