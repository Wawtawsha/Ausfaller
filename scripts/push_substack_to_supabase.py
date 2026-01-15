"""
Push analyzed Substack posts to Supabase.

Reads the cached analysis chunks and source posts, then upserts to Supabase.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from supabase import create_client
from config.settings import settings


def load_source_posts(cache_dir: Path) -> dict:
    """Load source posts and index by position."""
    posts_files = sorted(cache_dir.glob("substack_posts_*.json"), reverse=True)
    if not posts_files:
        raise FileNotFoundError("No source posts file found")

    source_file = posts_files[0]  # Most recent
    print(f"Loading source posts from: {source_file.name}")

    with open(source_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Handle wrapper object structure
    if isinstance(data, dict) and 'posts' in data:
        posts = data['posts']
    else:
        posts = data

    # Index by position
    return {i: post for i, post in enumerate(posts)}


def load_analysis_chunks(analysis_dir: Path) -> dict:
    """Load all analysis chunks and index by post index."""
    analyses = {}

    chunk_files = sorted(analysis_dir.glob("analysis_chunk_*.json"))
    print(f"Found {len(chunk_files)} analysis chunks")

    for chunk_file in chunk_files:
        with open(chunk_file, 'r', encoding='utf-8') as f:
            chunk = json.load(f)

        for item in chunk:
            analyses[item['index']] = item

    return analyses


def main():
    # Setup paths
    cache_dir = Path.home() / ".social-scraper" / "cache" / "substack"
    analysis_dir = cache_dir / "analysis"

    # Load data
    print("Loading source posts...")
    source_posts = load_source_posts(cache_dir)
    print(f"Loaded {len(source_posts)} source posts")

    print("Loading analysis chunks...")
    analyses = load_analysis_chunks(analysis_dir)
    print(f"Loaded {len(analyses)} analyzed posts")

    # Connect to Supabase
    print(f"\nConnecting to Supabase...")
    client = create_client(settings.supabase_url, settings.supabase_key)

    # Prepare records
    records = []
    for idx in sorted(analyses.keys()):
        analysis_data = analyses[idx]
        source = source_posts.get(idx, {})

        # Build record matching posts table schema
        record = {
            "platform": "substack",
            "platform_id": f"substack_{idx}_{analysis_data.get('publication', 'unknown')}",
            "video_url": source.get("url", ""),
            "author_username": source.get("author", analysis_data.get("publication", "")),
            "caption": analysis_data.get("title", ""),
            "niche_mode": "data_engineering",
            "niche": "data_engineering",
            "analysis": analysis_data.get("analysis", {}),
            "scraped_at": source.get("scraped_at", datetime.now().isoformat()),
            "analyzed_at": datetime.now().isoformat(),
        }

        # Add summary to analysis if not already there
        if "summary" not in record["analysis"]:
            record["analysis"]["summary"] = analysis_data.get("summary", "")

        # Add publication to analysis
        record["analysis"]["publication"] = analysis_data.get("publication", "")
        record["analysis"]["title"] = analysis_data.get("title", "")

        records.append(record)

    # Batch upsert (Supabase handles batches up to 1000)
    print(f"\nUpserting {len(records)} records to Supabase...")

    batch_size = 100
    total_inserted = 0

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        try:
            result = client.table("posts").upsert(
                batch,
                on_conflict="platform,platform_id"
            ).execute()
            total_inserted += len(batch)
            print(f"  Batch {i//batch_size + 1}: {len(batch)} records")
        except Exception as e:
            print(f"  Error in batch {i//batch_size + 1}: {e}")

    print(f"\nDone! Inserted/updated {total_inserted} Substack posts to Supabase.")
    print("Posts are now viewable in the dashboard with niche_mode='data_engineering'")


if __name__ == "__main__":
    main()
