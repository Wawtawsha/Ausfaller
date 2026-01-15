#!/usr/bin/env python3
"""
Import cached videos from local .info.json files into Supabase.

This script scans the video cache directory for .info.json files,
checks which videos are missing from Supabase, and imports them.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase import create_client
from config.settings import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CACHE_DIR = Path.home() / ".social-scraper" / "cache" / "videos"

# Hashtags that indicate data engineering content
DATA_ENGINEERING_HASHTAGS = {
    'dataengineering', 'datascience', 'powerbi', 'microsoftfabric', 'fabric',
    'azuredatafactory', 'adf', 'databricks', 'sql', 'python', 'data',
    'analytics', 'businessintelligence', 'bi', 'etl', 'datawarehouse',
    'bigdata', 'machinelearning', 'ml', 'ai', 'azure', 'aws', 'gcp',
    'snowflake', 'dbt', 'airflow', 'spark', 'hadoop', 'tableau'
}


def determine_niche_mode(info: dict) -> str:
    """Determine niche_mode based on content metadata."""
    extractor = info.get('extractor', '').lower()

    # YouTube shorts are typically data engineering in this dataset
    if extractor == 'youtube':
        return 'data_engineering'

    # For TikTok, check hashtags in title/description
    title = (info.get('title') or '').lower()
    description = (info.get('description') or '').lower()
    content = title + ' ' + description

    # Check for data engineering hashtags
    for hashtag in DATA_ENGINEERING_HASHTAGS:
        if f'#{hashtag}' in content or hashtag in content:
            return 'data_engineering'

    # Default to entertainment for TikTok
    return 'entertainment'


def parse_info_json(info_path: Path) -> Optional[dict]:
    """Parse an info.json file and return post data for Supabase."""
    try:
        with open(info_path, 'r', encoding='utf-8') as f:
            info = json.load(f)
    except Exception as e:
        logger.error(f"Failed to parse {info_path}: {e}")
        return None

    extractor = info.get('extractor', '').lower()

    # Determine platform
    if 'tiktok' in extractor:
        platform = 'tiktok'
    elif 'youtube' in extractor:
        platform = 'youtube_shorts'
    else:
        platform = 'unknown'

    # Get the corresponding mp4 file
    mp4_path = info_path.with_suffix('.mp4')
    if not mp4_path.exists():
        # Try alternate naming pattern
        mp4_path = Path(str(info_path).replace('.info.json', '.mp4'))

    file_size = mp4_path.stat().st_size if mp4_path.exists() else None

    # Build post data
    data = {
        'platform': platform,
        'platform_id': str(info.get('id', '')),
        'video_url': info.get('webpage_url', ''),
        'author_username': info.get('uploader') or info.get('channel', ''),
        'caption': info.get('title') or info.get('description', ''),
        'views': info.get('view_count'),
        'likes': info.get('like_count'),
        'comments': info.get('comment_count'),
        'shares': info.get('repost_count'),
        'duration_seconds': info.get('duration'),
        'content_type': 'video',
        'scraped_at': datetime.utcnow().isoformat(),
        'niche_mode': determine_niche_mode(info),
    }

    if file_size:
        data['file_size_bytes'] = file_size
        data['local_file_path'] = str(mp4_path)

    # Parse upload timestamp
    if info.get('timestamp'):
        try:
            data['posted_at'] = datetime.utcfromtimestamp(info['timestamp']).isoformat()
        except:
            pass
    elif info.get('upload_date'):
        try:
            data['posted_at'] = datetime.strptime(info['upload_date'], '%Y%m%d').isoformat()
        except:
            pass

    return data


def get_existing_platform_ids(client, platform: str) -> set:
    """Get all existing platform_ids for a platform from Supabase."""
    all_ids = set()
    offset = 0
    batch_size = 1000

    while True:
        result = (
            client.table('posts')
            .select('platform_id')
            .eq('platform', platform)
            .range(offset, offset + batch_size - 1)
            .execute()
        )

        if not result.data:
            break

        for row in result.data:
            all_ids.add(row['platform_id'])

        if len(result.data) < batch_size:
            break

        offset += batch_size

    return all_ids


def main():
    if not CACHE_DIR.exists():
        logger.error(f"Cache directory not found: {CACHE_DIR}")
        return

    # Connect to Supabase
    client = create_client(settings.supabase_url, settings.supabase_key)

    # Get all info.json files
    info_files = list(CACHE_DIR.glob('*.info.json'))
    logger.info(f"Found {len(info_files)} info.json files")

    # Get existing platform_ids to avoid duplicates
    logger.info("Fetching existing posts from Supabase...")
    existing_tiktok = get_existing_platform_ids(client, 'tiktok')
    existing_youtube = get_existing_platform_ids(client, 'youtube_shorts')
    logger.info(f"Found {len(existing_tiktok)} existing TikTok posts")
    logger.info(f"Found {len(existing_youtube)} existing YouTube posts")

    # Parse and filter new posts (deduplicate by platform+platform_id)
    seen_ids = {}  # (platform, platform_id) -> post_data
    skipped = 0
    errors = 0
    duplicates = 0

    for info_path in info_files:
        post_data = parse_info_json(info_path)
        if not post_data:
            errors += 1
            continue

        platform_id = post_data['platform_id']
        platform = post_data['platform']
        key = (platform, platform_id)

        # Check if already exists in Supabase
        if platform == 'tiktok' and platform_id in existing_tiktok:
            skipped += 1
            continue
        elif platform == 'youtube_shorts' and platform_id in existing_youtube:
            skipped += 1
            continue

        # Check for local duplicates (keep the one with more metadata)
        if key in seen_ids:
            duplicates += 1
            # Keep the one with file_size_bytes if available
            if post_data.get('file_size_bytes') and not seen_ids[key].get('file_size_bytes'):
                seen_ids[key] = post_data
            continue

        seen_ids[key] = post_data

    new_posts = list(seen_ids.values())
    logger.info(f"Deduplicated: {duplicates} local duplicates removed")

    logger.info(f"Found {len(new_posts)} new posts to import")
    logger.info(f"Skipped {skipped} existing posts")
    logger.info(f"Errors: {errors}")

    if not new_posts:
        logger.info("No new posts to import")
        return

    # Import in batches
    batch_size = 100
    imported = 0
    failed = 0

    for i in range(0, len(new_posts), batch_size):
        batch = new_posts[i:i + batch_size]
        try:
            result = (
                client.table('posts')
                .upsert(batch, on_conflict='platform,platform_id')
                .execute()
            )
            imported += len(batch)
            logger.info(f"Imported batch {i // batch_size + 1}: {len(batch)} posts (total: {imported})")
        except Exception as e:
            logger.error(f"Failed to import batch: {e}")
            failed += len(batch)

    logger.info(f"Import complete: {imported} imported, {failed} failed")

    # Print niche_mode breakdown
    de_count = sum(1 for p in new_posts if p['niche_mode'] == 'data_engineering')
    ent_count = sum(1 for p in new_posts if p['niche_mode'] == 'entertainment')
    logger.info(f"Niche breakdown: {de_count} data_engineering, {ent_count} entertainment")


if __name__ == '__main__':
    main()
