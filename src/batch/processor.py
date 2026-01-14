"""
Batch processor for large-scale content collection and analysis.

Supports collecting from multiple sources and analyzing with Gemini Batch API
for 50% cost savings on token usage.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional
from enum import Enum

from config.settings import settings

logger = logging.getLogger(__name__)


class ContentSource(str, Enum):
    YOUTUBE_SHORTS = "youtube_shorts"
    TIKTOK = "tiktok"
    SUBSTACK = "substack"


class BatchStatus(str, Enum):
    COLLECTING = "collecting"
    DOWNLOADING = "downloading"
    ANALYZING = "analyzing"
    STORING = "storing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class CollectionConfig:
    """Configuration for batch collection."""
    source: ContentSource
    queries: list[str]  # Search queries or hashtags
    count_per_query: int = 50


@dataclass
class BatchJob:
    """Tracks a batch processing job."""
    batch_id: str
    status: BatchStatus
    configs: list[CollectionConfig]

    # Progress tracking
    total_to_collect: int = 0
    collected: int = 0
    downloaded: int = 0
    analyzed: int = 0
    stored: int = 0
    failed: int = 0

    # Results by source
    items_by_source: dict = field(default_factory=dict)

    # Timing
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    # Error tracking
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "batch_id": self.batch_id,
            "status": self.status.value,
            "progress": {
                "total_to_collect": self.total_to_collect,
                "collected": self.collected,
                "downloaded": self.downloaded,
                "analyzed": self.analyzed,
                "stored": self.stored,
                "failed": self.failed,
            },
            "items_by_source": self.items_by_source,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "errors": self.errors[-10:],  # Last 10 errors
        }


class BatchProcessor:
    """
    Orchestrates large-scale batch collection and analysis.

    Workflow:
    1. Collect - Gather URLs from YouTube Shorts, TikTok, Substack
    2. Download - Download all media files
    3. Analyze - Submit to Gemini (standard or batch API)
    4. Store - Save results to Supabase
    """

    def __init__(self):
        self.jobs: dict[str, BatchJob] = {}
        self.output_dir = Path(settings.cache_dir) / "batch"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def collect_youtube_shorts(
        self,
        queries: list[str],
        count_per_query: int = 50,
    ) -> list[dict]:
        """Collect YouTube Shorts URLs for given search queries."""
        from src.extractor.youtube_shorts import YouTubeShortsExtractor

        if not settings.youtube_api_key:
            logger.warning("YouTube API key not configured, skipping YouTube Shorts")
            return []

        extractor = YouTubeShortsExtractor(api_key=settings.youtube_api_key)
        all_videos = []

        for query in queries:
            try:
                logger.info(f"Collecting YouTube Shorts for: {query}")
                result = await extractor.search_shorts(
                    query=query,
                    count=count_per_query,
                )

                if result.success:
                    for video in result.videos:
                        all_videos.append({
                            "source": ContentSource.YOUTUBE_SHORTS.value,
                            "url": video.video_url,
                            "video_id": video.video_id,
                            "author": video.author_username,
                            "title": video.caption,
                            "views": video.views,
                            "likes": video.likes,
                            "query": query,
                        })
                    logger.info(f"Found {len(result.videos)} shorts for '{query}'")
                else:
                    logger.warning(f"YouTube search failed for '{query}': {result.error}")

            except Exception as e:
                logger.error(f"Error collecting YouTube Shorts for '{query}': {e}")

        return all_videos

    async def collect_tiktok(
        self,
        hashtags: list[str],
        count_per_hashtag: int = 50,
    ) -> list[dict]:
        """Collect TikTok URLs for given hashtags."""
        from src.extractor.hashtag import HashtagExtractor, Platform

        extractor = HashtagExtractor()
        all_videos = []

        for hashtag in hashtags:
            try:
                logger.info(f"Collecting TikTok for: #{hashtag}")
                result = await extractor.extract_hashtag(
                    platform=Platform.TIKTOK,
                    hashtag=hashtag,
                    count=count_per_hashtag,
                )

                if result.success:
                    for video in result.videos:
                        all_videos.append({
                            "source": ContentSource.TIKTOK.value,
                            "url": video.video_url,
                            "video_id": video.video_id,
                            "author": video.author_username,
                            "title": video.caption,
                            "views": video.views,
                            "likes": video.likes,
                            "hashtag": hashtag,
                        })
                    logger.info(f"Found {len(result.videos)} TikToks for #{hashtag}")
                else:
                    logger.warning(f"TikTok extraction failed for #{hashtag}: {result.error}")

            except Exception as e:
                logger.error(f"Error collecting TikTok for #{hashtag}: {e}")

        return all_videos

    async def collect_substack(
        self,
        publications: list[str],
        count_per_pub: int = 20,
    ) -> list[dict]:
        """Collect Substack articles with embedded videos."""
        from src.extractor.substack import SubstackExtractor

        extractor = SubstackExtractor()
        all_items = []

        for publication in publications:
            try:
                logger.info(f"Collecting Substack: {publication}")
                posts, result = await extractor.extract_publication(
                    publication_name=publication,
                    count=count_per_pub,
                )

                if result.success:
                    for post in posts:
                        # Add article itself
                        all_items.append({
                            "source": ContentSource.SUBSTACK.value,
                            "url": post.url,
                            "video_id": post.id,
                            "author": post.author,
                            "title": post.title,
                            "content_type": "article",
                            "publication": publication,
                        })

                        # Add embedded videos
                        for video in post.embedded_videos:
                            all_items.append({
                                "source": f"substack_embed_{video.platform}",
                                "url": video.url,
                                "video_id": video.video_id,
                                "author": post.author,
                                "title": f"{post.title} (embedded)",
                                "content_type": "video",
                                "publication": publication,
                            })
                    logger.info(f"Found {len(posts)} posts from {publication}")
                else:
                    logger.warning(f"Substack extraction failed for {publication}: {result.error}")

            except Exception as e:
                logger.error(f"Error collecting Substack {publication}: {e}")

        return all_items

    async def collect_all(
        self,
        youtube_queries: list[str] = None,
        tiktok_hashtags: list[str] = None,
        substack_pubs: list[str] = None,
        count_per_source: int = 50,
    ) -> dict:
        """
        Collect content from all configured sources.

        Returns dict with items grouped by source.
        """
        results = {
            "youtube_shorts": [],
            "tiktok": [],
            "substack": [],
            "total": 0,
        }

        tasks = []

        if youtube_queries:
            tasks.append(("youtube_shorts", self.collect_youtube_shorts(
                queries=youtube_queries,
                count_per_query=count_per_source,
            )))

        if tiktok_hashtags:
            tasks.append(("tiktok", self.collect_tiktok(
                hashtags=tiktok_hashtags,
                count_per_hashtag=count_per_source,
            )))

        if substack_pubs:
            tasks.append(("substack", self.collect_substack(
                publications=substack_pubs,
                count_per_pub=count_per_source,
            )))

        # Run collection in parallel
        if tasks:
            task_results = await asyncio.gather(
                *[t[1] for t in tasks],
                return_exceptions=True,
            )

            for (source, _), result in zip(tasks, task_results):
                if isinstance(result, Exception):
                    logger.error(f"Collection failed for {source}: {result}")
                else:
                    results[source] = result
                    results["total"] += len(result)

        return results

    async def download_batch(
        self,
        items: list[dict],
        max_concurrent: int = 5,
    ) -> list[dict]:
        """
        Download all video items.

        Returns items with file_path added for successful downloads.
        """
        from src.downloader.video import VideoDownloader

        downloader = VideoDownloader()
        semaphore = asyncio.Semaphore(max_concurrent)

        async def download_one(item: dict) -> dict:
            async with semaphore:
                if item.get("content_type") == "article":
                    # Skip articles, they don't need downloading
                    item["file_path"] = None
                    item["download_success"] = True
                    return item

                try:
                    result = await downloader.download(
                        url=item["url"],
                        video_id=item.get("video_id", ""),
                        platform=item["source"],
                    )

                    item["file_path"] = str(result.file_path) if result.file_path else None
                    item["download_success"] = result.success
                    item["file_size"] = result.file_size_bytes
                    item["duration"] = result.duration_seconds

                    if result.metadata:
                        item["metadata"] = result.metadata

                except Exception as e:
                    logger.error(f"Download failed for {item['url']}: {e}")
                    item["file_path"] = None
                    item["download_success"] = False
                    item["download_error"] = str(e)

                return item

        # Download all in parallel with semaphore
        results = await asyncio.gather(
            *[download_one(item) for item in items],
            return_exceptions=True,
        )

        # Filter out exceptions
        downloaded = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Download task failed: {result}")
            else:
                downloaded.append(result)

        success_count = sum(1 for item in downloaded if item.get("download_success"))
        logger.info(f"Downloaded {success_count}/{len(items)} items")

        return downloaded

    def save_collection(self, batch_id: str, items: list[dict]) -> Path:
        """Save collected items to JSON for batch processing."""
        output_file = self.output_dir / f"{batch_id}_collection.json"

        with open(output_file, "w") as f:
            json.dump({
                "batch_id": batch_id,
                "collected_at": datetime.utcnow().isoformat(),
                "total_items": len(items),
                "items": items,
            }, f, indent=2)

        logger.info(f"Saved collection to {output_file}")
        return output_file

    def load_collection(self, batch_id: str) -> list[dict]:
        """Load previously saved collection."""
        input_file = self.output_dir / f"{batch_id}_collection.json"

        if not input_file.exists():
            raise FileNotFoundError(f"Collection not found: {input_file}")

        with open(input_file) as f:
            data = json.load(f)

        return data.get("items", [])

    def get_batch_stats(self, items: list[dict]) -> dict:
        """Get statistics about collected items."""
        by_source = {}
        for item in items:
            source = item.get("source", "unknown")
            if source not in by_source:
                by_source[source] = {
                    "count": 0,
                    "total_views": 0,
                    "total_likes": 0,
                }
            by_source[source]["count"] += 1
            by_source[source]["total_views"] += item.get("views", 0) or 0
            by_source[source]["total_likes"] += item.get("likes", 0) or 0

        return {
            "total_items": len(items),
            "by_source": by_source,
            "estimated_download_size_gb": len(items) * 6 / 1024,  # ~6MB avg per video
            "estimated_analysis_cost_standard": len(items) * 0.00144,
            "estimated_analysis_cost_batch": len(items) * 0.00072,  # 50% off
        }
