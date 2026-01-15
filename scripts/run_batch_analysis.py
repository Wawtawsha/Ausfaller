"""
Run Gemini batch analysis on all downloaded videos from collection batches.

Uses data_engineering niche mode with full analytical standards:
- EducationalAnalysis (clarity, depth, practical applicability, teaching techniques)
- DataEngineeringContext (Microsoft stack, cloud platform, data layer, architecture)
- TechnicalSpecs and BrandSafety metrics
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

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_analysis_run.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Directories
VIDEO_DIR = Path(r'C:\Users\steph\.social-scraper\cache\videos')
BATCH_DIR = Path(r'C:\Users\steph\.social-scraper\cache\batch')
OUTPUT_DIR = BATCH_DIR

# Collection files
COLLECTION_FILES = [
    '96f478e3-7ede-45f3-9ee5-0ed30c9fe5a1_collection.json',  # Batch 1
    '610f8ea3-c317-4555-ad58-f44bd5634ec4_collection.json',  # Batch 2
    'bd1cc487-61cd-4997-a77e-31bcd7304dad_collection.json',  # Batch 3
]


def build_video_items():
    """Build list of all downloaded videos with metadata."""
    items = []

    # Load all collection files and merge
    for filename in COLLECTION_FILES:
        collection_file = BATCH_DIR / filename
        if collection_file.exists():
            with open(collection_file) as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data['items'])} items from {filename}")
                items.extend(data['items'])

    logger.info(f"Total items from collections: {len(items)}")

    # Get all video files
    video_files = list(VIDEO_DIR.glob('*.mp4'))
    logger.info(f"Found {len(video_files)} video files")

    # Build index by video ID
    file_index = {}
    for f in video_files:
        # Parse filename: tiktok_VIDEOID_TIMESTAMP.mp4 or youtube_shorts_VIDEOID_TIMESTAMP.mp4
        parts = f.stem.split('_')
        if f.stem.startswith('tiktok_') and len(parts) >= 3:
            vid = parts[1]  # Video ID
            file_index[vid] = f
        elif f.stem.startswith('youtube_shorts_') and len(parts) >= 4:
            vid = parts[2]  # Video ID
            file_index[vid] = f

    logger.info(f"Indexed {len(file_index)} video files by ID")

    matched_items = []
    for item in items:
        video_id = item.get('video_id', '')

        if video_id and video_id in file_index:
            item['file_path'] = str(file_index[video_id])
            item['download_success'] = True
            matched_items.append(item)

    logger.info(f"Matched {len(matched_items)} items with video files")
    return matched_items


async def run_analysis(limit: int = None, delay: float = 2.0, store_to_db: bool = True):
    """Run batch analysis on all videos."""
    from src.analyzer.gemini import GeminiAnalyzer
    from supabase import create_client

    # Build items list
    items = build_video_items()

    if limit:
        items = items[:limit]
        logger.info(f"Limited to {limit} items")

    if not items:
        logger.error("No items to analyze!")
        return

    # Initialize analyzer with data_engineering mode
    analyzer = GeminiAnalyzer(niche_mode="data_engineering")

    # Initialize Supabase client if storing
    db_client = None
    if store_to_db:
        db_client = create_client(settings.supabase_url, settings.supabase_key)

    # Generate batch ID for this run
    batch_id = f"combined_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    results_file = OUTPUT_DIR / f"{batch_id}_results.jsonl"

    total = len(items)
    logger.info(f"Starting analysis of {total} videos")
    logger.info(f"Batch ID: {batch_id}")
    logger.info(f"Niche mode: data_engineering")
    logger.info(f"Store to database: {store_to_db}")
    logger.info(f"Estimated time: ~{total * delay / 3600:.1f} hours at {60/delay:.0f} RPM")

    analyzed = 0
    failed = 0
    stored = 0

    for i, item in enumerate(items):
        file_path = Path(item['file_path'])

        if not file_path.exists():
            logger.warning(f"[{i+1}/{total}] File not found: {file_path}")
            failed += 1
            continue

        logger.info(f"[{i+1}/{total}] Analyzing: {item.get('author', 'unknown')} - {file_path.name}")

        try:
            # Run Gemini analysis
            analysis = await analyzer.analyze_video(file_path)

            if analysis.success:
                analysis_data = analysis.to_dict()

                # Save to JSONL results file
                item['analysis'] = analysis_data
                item['analyzed_at'] = datetime.now(timezone.utc).isoformat()

                with open(results_file, 'a') as f:
                    f.write(json.dumps(item) + '\n')

                # Log key metrics
                edu = analysis_data.get('educational', {})
                de = analysis_data.get('data_engineering', {})
                logger.info(
                    f"  OK Clarity: {edu.get('explanation_clarity', 0)}/10, "
                    f"Depth: {edu.get('technical_depth', 0)}/10, "
                    f"Value: {edu.get('educational_value', 0)}/10 "
                    f"| MS Stack: {de.get('microsoft_stack', False)}"
                )

                # Store to Supabase
                if db_client:
                    try:
                        from src.extractor import Platform

                        platform_map = {
                            'tiktok': 'tiktok',
                            'youtube_shorts': 'youtube_shorts',
                        }
                        platform = platform_map.get(item.get('source'), 'tiktok')

                        post_data = {
                            'platform': platform,
                            'platform_id': item.get('video_id', ''),
                            'video_url': item.get('url', ''),
                            'author_username': item.get('author', ''),
                            'local_file_path': str(file_path),
                            'analysis': analysis_data,
                            'analyzed_at': datetime.now(timezone.utc).isoformat(),
                            'niche': 'data_engineering',
                        }

                        db_client.table('posts').upsert(
                            post_data,
                            on_conflict='platform,platform_id'
                        ).execute()
                        stored += 1

                    except Exception as e:
                        logger.warning(f"  DB store failed: {e}")

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
            logger.info(f"Progress: {i+1}/{total} ({analyzed} analyzed, {failed} failed, {stored} stored)")

    # Final summary
    logger.info("=" * 60)
    logger.info(f"Analysis complete!")
    logger.info(f"  Total: {total}")
    logger.info(f"  Analyzed: {analyzed}")
    logger.info(f"  Failed: {failed}")
    logger.info(f"  Stored to DB: {stored}")
    logger.info(f"  Results file: {results_file}")
    logger.info("=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Run Gemini batch analysis on videos')
    parser.add_argument('--limit', type=int, help='Limit number of videos to analyze')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between requests (seconds)')
    parser.add_argument('--no-store', action='store_true', help='Skip storing to database')
    args = parser.parse_args()

    # Check for Gemini API key
    if not settings.gemini_api_key:
        logger.error("GEMINI_API_KEY not set in .env file")
        sys.exit(1)

    logger.info(f"Gemini model: {settings.gemini_model}")
    logger.info(f"Niche mode: data_engineering")

    asyncio.run(run_analysis(
        limit=args.limit,
        delay=args.delay,
        store_to_db=not args.no_store
    ))


if __name__ == "__main__":
    main()
