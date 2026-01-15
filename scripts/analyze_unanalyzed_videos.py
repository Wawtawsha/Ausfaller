"""
Analyze videos that have been downloaded but not yet analyzed.

Queries Supabase for posts with local_file_path but no analysis,
sends them to Gemini, and updates Supabase with results.
"""
import asyncio
import json
import logging
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from supabase import create_client

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('analyze_unanalyzed.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


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


async def run_analysis(
    niche_mode: str = None,
    limit: int = None,
    delay: float = 2.0,
    dry_run: bool = False
):
    """Run Gemini analysis on unanalyzed videos."""
    from src.analyzer.gemini import GeminiAnalyzer

    # Connect to Supabase
    client = create_client(settings.supabase_url, settings.supabase_key)

    # Get unanalyzed videos
    logger.info(f"Querying unanalyzed videos (niche_mode={niche_mode})...")
    videos = get_unanalyzed_videos(client, niche_mode, limit or 10000)

    if limit:
        videos = videos[:limit]

    total = len(videos)
    logger.info(f"Found {total} unanalyzed videos")

    if total == 0:
        logger.info("Nothing to analyze!")
        return

    if dry_run:
        logger.info("DRY RUN - would analyze these videos:")
        for v in videos[:10]:
            logger.info(f"  {v['platform']}/{v['platform_id']} - {v['local_file_path']}")
        if total > 10:
            logger.info(f"  ... and {total - 10} more")
        return

    # Initialize analyzer
    # Use the niche_mode from the video, or default to data_engineering
    default_mode = niche_mode or "data_engineering"
    analyzer = GeminiAnalyzer(niche_mode=default_mode)

    logger.info(f"Starting analysis of {total} videos")
    logger.info(f"Default niche mode: {default_mode}")
    logger.info(f"Delay between requests: {delay}s (~{60/delay:.0f} RPM)")
    logger.info(f"Estimated time: ~{total * delay / 3600:.1f} hours")

    analyzed = 0
    failed = 0
    missing = 0

    for i, video in enumerate(videos):
        file_path = Path(video['local_file_path'])

        # Check if file exists
        if not file_path.exists():
            logger.warning(f"[{i+1}/{total}] File missing: {file_path}")
            missing += 1
            continue

        logger.info(f"[{i+1}/{total}] Analyzing: {video['author_username']} - {file_path.name}")

        try:
            # Use video's niche_mode if available
            video_niche = video.get('niche_mode') or default_mode
            if video_niche != analyzer.niche_mode:
                analyzer = GeminiAnalyzer(niche_mode=video_niche)

            # Run Gemini analysis
            analysis = await analyzer.analyze_video(file_path)

            if analysis.success:
                analysis_data = analysis.to_dict()

                # Update Supabase
                client.table('posts').update({
                    'analysis': analysis_data,
                    'analyzed_at': datetime.now(timezone.utc).isoformat()
                }).eq('id', video['id']).execute()

                # Log key metrics based on niche
                if video_niche == 'data_engineering':
                    edu = analysis_data.get('educational', {})
                    logger.info(
                        f"  ✓ Clarity: {edu.get('explanation_clarity', 0)}/10, "
                        f"Depth: {edu.get('technical_depth', 0)}/10, "
                        f"Value: {edu.get('educational_value', 0)}/10"
                    )
                else:
                    hook = analysis_data.get('hook', {})
                    trends = analysis_data.get('trends', {})
                    logger.info(
                        f"  ✓ Hook: {hook.get('hook_strength', 0)}/10, "
                        f"Viral: {trends.get('viral_potential_score', 0)}/10"
                    )

                analyzed += 1
            else:
                logger.error(f"  ✗ Analysis failed: {analysis.error}")
                failed += 1

        except Exception as e:
            logger.error(f"  ✗ Error: {e}")
            failed += 1

        # Rate limiting
        if i < total - 1:
            await asyncio.sleep(delay)

        # Progress update every 50 items
        if (i + 1) % 50 == 0:
            logger.info(f"Progress: {i+1}/{total} ({analyzed} OK, {failed} failed, {missing} missing)")

    # Final summary
    logger.info("=" * 60)
    logger.info("Analysis complete!")
    logger.info(f"  Total queried: {total}")
    logger.info(f"  Analyzed: {analyzed}")
    logger.info(f"  Failed: {failed}")
    logger.info(f"  Missing files: {missing}")
    logger.info("=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Analyze unanalyzed videos with Gemini')
    parser.add_argument('--niche', type=str, choices=['entertainment', 'data_engineering'],
                        help='Filter by niche mode')
    parser.add_argument('--limit', type=int, help='Limit number of videos to analyze')
    parser.add_argument('--delay', type=float, default=2.0,
                        help='Delay between requests in seconds (default: 2.0)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be analyzed without actually doing it')
    args = parser.parse_args()

    # Check for Gemini API key
    if not settings.gemini_api_key:
        logger.error("GEMINI_API_KEY not set in .env file")
        sys.exit(1)

    asyncio.run(run_analysis(
        niche_mode=args.niche,
        limit=args.limit,
        delay=args.delay,
        dry_run=args.dry_run
    ))


if __name__ == "__main__":
    main()
