"""
Backfill engagement metrics for existing posts using yt-dlp.

Fetches view_count, like_count, comment_count, repost_count from TikTok
without downloading videos.

Usage:
    python scripts/backfill_engagement.py [--limit 50] [--delay 2]
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase import create_client
from config.settings import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def fetch_engagement(url: str) -> dict | None:
    """Fetch engagement metrics and posting date using yt-dlp without downloading."""
    try:
        import yt_dlp
        from datetime import datetime

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if info:
                result = {
                    'views': info.get('view_count', 0) or 0,
                    'likes': info.get('like_count', 0) or 0,
                    'comments': info.get('comment_count', 0) or 0,
                    'shares': info.get('repost_count', 0) or 0,
                }
                # Extract upload timestamp for time-weighted metrics
                if info.get('timestamp'):
                    result['posted_at'] = datetime.utcfromtimestamp(info['timestamp']).isoformat()
                return result
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")

    return None


async def backfill(limit: int = 50, delay: float = 2.0, missing_date_only: bool = False):
    """Backfill engagement for posts missing data."""

    client = create_client(settings.supabase_url, settings.supabase_key)

    # Get posts missing posted_at (primary) or engagement data
    if missing_date_only:
        result = client.table("posts").select(
            "id, video_url, views, likes, comments, shares, posted_at"
        ).is_("posted_at", "null").limit(limit).execute()
    else:
        result = client.table("posts").select(
            "id, video_url, views, likes, comments, shares, posted_at"
        ).eq("views", 0).eq("comments", 0).limit(limit).execute()

    posts = result.data
    logger.info(f"Found {len(posts)} posts to backfill")

    updated = 0
    failed = 0

    for i, post in enumerate(posts):
        logger.info(f"[{i+1}/{len(posts)}] Fetching: {post['video_url'][:60]}...")

        engagement = fetch_engagement(post['video_url'])

        if engagement and (engagement['views'] > 0 or engagement['comments'] > 0 or engagement.get('posted_at')):
            try:
                client.table("posts").update(engagement).eq("id", post['id']).execute()
                posted = engagement.get('posted_at', 'N/A')[:10] if engagement.get('posted_at') else 'N/A'
                logger.info(f"  Updated: {engagement['views']:,} views, {engagement['likes']:,} likes, posted: {posted}")
                updated += 1
            except Exception as e:
                logger.error(f"  Failed to update: {e}")
                failed += 1
        else:
            logger.warning(f"  No engagement data (may be blocked)")
            failed += 1

        # Rate limit
        if i < len(posts) - 1:
            await asyncio.sleep(delay)

    logger.info(f"\nBackfill complete: {updated} updated, {failed} failed")
    return updated, failed


def main():
    parser = argparse.ArgumentParser(description='Backfill engagement metrics')
    parser.add_argument('--limit', type=int, default=50, help='Max posts to process')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between requests (seconds)')
    parser.add_argument('--missing-date', action='store_true', help='Only backfill posts missing posted_at')
    args = parser.parse_args()

    asyncio.run(backfill(limit=args.limit, delay=args.delay, missing_date_only=args.missing_date))


if __name__ == "__main__":
    main()
