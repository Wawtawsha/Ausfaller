"""
Scrape Substack publications for data engineering content.
Saves posts to JSON for Claude analysis.

Usage:
    python scripts/scrape_substack.py
    python scripts/scrape_substack.py --count 50
"""
import asyncio
import json
import logging
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extractor.substack import SubstackExtractor

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Data engineering Substack publications (expanded list)
DATA_ENGINEERING_PUBLICATIONS = [
    # Core data engineering (verified working)
    "dataengineeringweekly",
    "dataengineeringcentral",
    "moderndata101",
    "marvelousmlops",
    "benn",
    "seattledataguy",
    "ergestx",
    "thedataengineer",
    "dataqualitycamp",
    "startdataengineering",
    "learndataengineering",
    "datatalks",
    "clouddata",

    # Data/Analytics newsletters
    "thesequel",
    "groupbydata",
    "datafold",
    "getdbt",
    "airbyte",
    "tristan",  # Tristan Handy / dbt
    "annafelicity",
    "sarahsnewsletter",
    "mikeckennedy",
    "technically",
    "periscopedata",
    "maboroshi",

    # Tech/Engineering adjacent
    "bytebytego",
    "pragmaticengineer",
    "theengineeringmanager",
    "highgrowthengineering",
    "lethain",
    "lcamtuf",
    "changelog",
    "pointer",
    "tldr",

    # ML/AI + Data
    "deeplearningweekly",
    "thesequence",
    "lastweekinai",
    "importai",
    "machinelearnings",
    "gradientflow",
    "aisupremacy",

    # Cloud/Platform
    "clouddeveloper",
    "awsweekly",
    "gcpweekly",
    "azureweekly",
    "serverlessland",
    "cloudirregular",

    # Analytics/BI specific
    "amplitudenewsletter",
    "mixpanel",
    "analyticsengineering",
    "metricstack",
    "preql",
    "hyperquery",
    "mode",
    "census",
    "hightouch",

    # Data leadership/careers
    "lennysnewsletter",
    "eczachly",  # Zach Wilson
    "datawithchad",
    "ananelson",
    "davidsj",
    "mikekaminsky",
]

OUTPUT_DIR = Path(r'C:\Users\steph\.social-scraper\cache\substack')


async def scrape_all(count_per_pub: int = 30):
    """Scrape all data engineering Substacks."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    extractor = SubstackExtractor()
    all_posts = []
    successful_pubs = []
    failed_pubs = []

    for pub_name in DATA_ENGINEERING_PUBLICATIONS:
        logger.info(f"Scraping: {pub_name}.substack.com")

        try:
            posts, result = await extractor.extract_publication(pub_name, count_per_pub)

            if posts:
                for post in posts:
                    all_posts.append({
                        "publication": pub_name,
                        "publication_title": post.publication,
                        "title": post.title,
                        "url": post.url,
                        "author": post.author,
                        "published_at": post.published_at.isoformat() if post.published_at else None,
                        "description": post.description,
                        "content_html": post.content_html,
                        "embedded_videos": post.embedded_videos,
                        "scraped_at": datetime.utcnow().isoformat(),
                    })
                successful_pubs.append(f"{pub_name} ({len(posts)} posts)")
                logger.info(f"  Got {len(posts)} posts")
            else:
                failed_pubs.append(pub_name)
                logger.warning(f"  No posts found")

        except Exception as e:
            failed_pubs.append(f"{pub_name}: {e}")
            logger.error(f"  Failed: {e}")

        await asyncio.sleep(1)  # Rate limit

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = OUTPUT_DIR / f"substack_posts_{timestamp}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            "scraped_at": datetime.utcnow().isoformat(),
            "total_posts": len(all_posts),
            "successful_publications": successful_pubs,
            "failed_publications": failed_pubs,
            "posts": all_posts,
        }, f, indent=2, ensure_ascii=False)

    logger.info("=" * 60)
    logger.info(f"Scraping complete!")
    logger.info(f"  Total posts: {len(all_posts)}")
    logger.info(f"  Successful: {len(successful_pubs)} publications")
    logger.info(f"  Failed: {len(failed_pubs)} publications")
    logger.info(f"  Output: {output_file}")
    logger.info("=" * 60)

    return output_file


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Scrape data engineering Substacks')
    parser.add_argument('--count', type=int, default=30, help='Posts per publication')
    args = parser.parse_args()

    asyncio.run(scrape_all(args.count))


if __name__ == "__main__":
    main()
