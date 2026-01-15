"""
Run Gemini analysis on downloaded videos.

This script:
1. Fetches posts with downloaded videos that haven't been analyzed
2. Runs Gemini educational analysis on each video
3. Saves the analysis results back to the database
4. Updates dashboard metrics

Usage:
    python scripts/run_gemini_analysis.py --limit 10  # Test with 10 videos
    python scripts/run_gemini_analysis.py              # Run all
"""

import asyncio
import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from supabase import create_client
from src.analyzer.gemini import GeminiAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_analysis(limit: int = None, delay: float = 5.0):
    """Run Gemini analysis on unanalyzed videos."""

    # Initialize clients
    client = create_client(settings.supabase_url, settings.supabase_key)
    analyzer = GeminiAnalyzer(niche_mode="data_engineering")

    # Fetch posts with local files that haven't been analyzed
    query = client.table('posts').select(
        'id, platform, platform_id, video_url, author_username, local_file_path'
    ).eq('niche', 'data_engineering').not_.is_('local_file_path', 'null').is_('analysis', 'null')

    if limit:
        query = query.limit(limit)

    result = query.execute()
    posts = result.data

    # Filter to posts with existing files
    valid_posts = []
    for post in posts:
        path = Path(post['local_file_path'])
        if path.exists():
            valid_posts.append(post)
        else:
            logger.warning(f"File missing: {path}")

    total = len(valid_posts)
    logger.info(f"Found {total} videos to analyze")

    if total == 0:
        logger.info("No videos to analyze!")
        return

    # Track progress
    analyzed = 0
    failed = 0

    for i, post in enumerate(valid_posts):
        video_path = Path(post['local_file_path'])
        logger.info(f"[{i+1}/{total}] Analyzing: {post['author_username']} - {video_path.name}")

        try:
            # Run Gemini analysis
            analysis = await analyzer.analyze_video(video_path)

            if analysis.success:
                # Extract key metrics for database
                analysis_data = analysis.to_dict()

                # Update database with analysis
                update_result = client.table('posts').update({
                    'analysis': analysis_data,
                    'analyzed_at': datetime.now(timezone.utc).isoformat()
                }).eq('id', post['id']).execute()

                # Log key metrics
                edu = analysis_data.get('educational', {})
                logger.info(
                    f"  ✓ Clarity: {edu.get('explanation_clarity', 0)}/10, "
                    f"Depth: {edu.get('technical_depth', 0)}/10, "
                    f"Value: {edu.get('educational_value', 0)}/10"
                )
                analyzed += 1
            else:
                logger.error(f"  ✗ Analysis failed: {analysis.error}")
                failed += 1

        except Exception as e:
            logger.error(f"  ✗ Error: {e}")
            failed += 1

        # Rate limiting - don't delay after last item
        if i < total - 1:
            logger.info(f"  Waiting {delay}s for rate limit...")
            await asyncio.sleep(delay)

        # Progress update every 10 items
        if (i + 1) % 10 == 0:
            logger.info(f"Progress: {i+1}/{total} ({analyzed} analyzed, {failed} failed)")

    # Final summary
    logger.info("=" * 50)
    logger.info(f"Analysis complete!")
    logger.info(f"  Total: {total}")
    logger.info(f"  Analyzed: {analyzed}")
    logger.info(f"  Failed: {failed}")
    logger.info("=" * 50)


def main():
    parser = argparse.ArgumentParser(description='Run Gemini analysis on videos')
    parser.add_argument('--limit', type=int, help='Limit number of videos to analyze')
    parser.add_argument('--delay', type=float, default=5.0, help='Delay between requests (seconds)')
    args = parser.parse_args()

    # Check for Gemini API key
    if not settings.gemini_api_key:
        logger.error("GEMINI_API_KEY not set in .env file")
        sys.exit(1)

    logger.info(f"Gemini model: {settings.gemini_model}")
    logger.info(f"Niche mode: data_engineering")

    asyncio.run(run_analysis(limit=args.limit, delay=args.delay))


if __name__ == "__main__":
    main()
