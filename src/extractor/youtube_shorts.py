"""
YouTube Shorts extractor using YouTube Data API v3.

Extracts Shorts videos from search results or channel listings.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import httpx

from config.settings import settings
from src.extractor.hashtag import Platform, VideoInfo, ExtractionResult

logger = logging.getLogger(__name__)

# YouTube Data API v3 endpoints
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNELS_URL = "https://www.googleapis.com/youtube/v3/channels"


class YouTubeShortsExtractor:
    """Extract YouTube Shorts using the Data API v3."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.youtube_api_key
        if not self.api_key:
            raise ValueError("YouTube API key is required. Set YOUTUBE_API_KEY in .env")

    async def search_shorts(
        self,
        query: str,
        count: int = 30,
        order: str = "relevance"
    ) -> ExtractionResult:
        """
        Search for YouTube Shorts matching a query.

        Args:
            query: Search query (e.g., "microsoft fabric tutorial")
            count: Maximum number of results (API max is 50 per request)
            order: Sort order - "relevance", "date", "viewCount", "rating"

        Returns:
            ExtractionResult with list of VideoInfo objects
        """
        try:
            videos = []
            next_page_token = None
            remaining = min(count, 50)  # API max per request

            async with httpx.AsyncClient(timeout=30.0) as client:
                while remaining > 0:
                    params = {
                        "part": "snippet",
                        "q": query,
                        "type": "video",
                        "videoDuration": "short",  # Under 4 minutes (Shorts are under 60s)
                        "maxResults": min(remaining, 50),
                        "order": order,
                        "key": self.api_key,
                    }
                    if next_page_token:
                        params["pageToken"] = next_page_token

                    response = await client.get(YOUTUBE_SEARCH_URL, params=params)
                    response.raise_for_status()
                    data = response.json()

                    # Extract video IDs for detailed stats
                    video_ids = [item["id"]["videoId"] for item in data.get("items", [])]

                    if video_ids:
                        # Get detailed video statistics
                        stats = await self._get_video_stats(client, video_ids)

                        for item in data.get("items", []):
                            video_id = item["id"]["videoId"]
                            snippet = item["snippet"]
                            video_stats = stats.get(video_id, {})

                            # Filter for actual Shorts (under 60 seconds)
                            duration = video_stats.get("duration_seconds", 0)
                            if duration > 60:
                                continue

                            video_info = VideoInfo(
                                platform=Platform.YOUTUBE_SHORTS,
                                video_url=f"https://www.youtube.com/shorts/{video_id}",
                                video_id=video_id,
                                author_username=snippet.get("channelTitle", ""),
                                thumbnail_url=snippet.get("thumbnails", {}).get("high", {}).get("url"),
                                likes=video_stats.get("likes", 0),
                                comments=video_stats.get("comments", 0),
                                views=video_stats.get("views", 0),
                                caption=snippet.get("title", ""),
                                hashtags=self._extract_hashtags(snippet.get("description", "")),
                                extracted_at=datetime.utcnow(),
                            )
                            videos.append(video_info)

                    next_page_token = data.get("nextPageToken")
                    if not next_page_token:
                        break
                    remaining -= len(data.get("items", []))

            return ExtractionResult(
                success=True,
                videos=videos,
                videos_requested=count,
                videos_found=len(videos),
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"YouTube API error: {e.response.status_code} - {e.response.text}")
            return ExtractionResult(
                success=False,
                error=f"YouTube API error: {e.response.status_code}",
                videos_requested=count,
            )
        except Exception as e:
            logger.error(f"YouTube extraction failed: {e}")
            return ExtractionResult(
                success=False,
                error=str(e),
                videos_requested=count,
            )

    async def get_channel_shorts(
        self,
        channel_id: str,
        count: int = 30
    ) -> ExtractionResult:
        """
        Get Shorts from a specific YouTube channel.

        Args:
            channel_id: YouTube channel ID (starts with UC...)
            count: Maximum number of results

        Returns:
            ExtractionResult with list of VideoInfo objects
        """
        try:
            # Search within the channel for short videos
            async with httpx.AsyncClient(timeout=30.0) as client:
                params = {
                    "part": "snippet",
                    "channelId": channel_id,
                    "type": "video",
                    "videoDuration": "short",
                    "maxResults": min(count, 50),
                    "order": "date",
                    "key": self.api_key,
                }

                response = await client.get(YOUTUBE_SEARCH_URL, params=params)
                response.raise_for_status()
                data = response.json()

                video_ids = [item["id"]["videoId"] for item in data.get("items", [])]
                videos = []

                if video_ids:
                    stats = await self._get_video_stats(client, video_ids)

                    for item in data.get("items", []):
                        video_id = item["id"]["videoId"]
                        snippet = item["snippet"]
                        video_stats = stats.get(video_id, {})

                        # Filter for actual Shorts
                        duration = video_stats.get("duration_seconds", 0)
                        if duration > 60:
                            continue

                        video_info = VideoInfo(
                            platform=Platform.YOUTUBE_SHORTS,
                            video_url=f"https://www.youtube.com/shorts/{video_id}",
                            video_id=video_id,
                            author_username=snippet.get("channelTitle", ""),
                            thumbnail_url=snippet.get("thumbnails", {}).get("high", {}).get("url"),
                            likes=video_stats.get("likes", 0),
                            comments=video_stats.get("comments", 0),
                            views=video_stats.get("views", 0),
                            caption=snippet.get("title", ""),
                            hashtags=self._extract_hashtags(snippet.get("description", "")),
                            extracted_at=datetime.utcnow(),
                        )
                        videos.append(video_info)

                return ExtractionResult(
                    success=True,
                    videos=videos,
                    videos_requested=count,
                    videos_found=len(videos),
                )

        except Exception as e:
            logger.error(f"Channel shorts extraction failed: {e}")
            return ExtractionResult(
                success=False,
                error=str(e),
                videos_requested=count,
            )

    async def _get_video_stats(
        self,
        client: httpx.AsyncClient,
        video_ids: list[str]
    ) -> dict:
        """Get detailed statistics for a list of videos."""
        try:
            params = {
                "part": "statistics,contentDetails",
                "id": ",".join(video_ids),
                "key": self.api_key,
            }

            response = await client.get(YOUTUBE_VIDEOS_URL, params=params)
            response.raise_for_status()
            data = response.json()

            stats = {}
            for item in data.get("items", []):
                video_id = item["id"]
                statistics = item.get("statistics", {})
                content_details = item.get("contentDetails", {})

                # Parse duration (ISO 8601 format: PT1M30S)
                duration_str = content_details.get("duration", "PT0S")
                duration_seconds = self._parse_duration(duration_str)

                stats[video_id] = {
                    "views": int(statistics.get("viewCount", 0)),
                    "likes": int(statistics.get("likeCount", 0)),
                    "comments": int(statistics.get("commentCount", 0)),
                    "duration_seconds": duration_seconds,
                }

            return stats

        except Exception as e:
            logger.warning(f"Failed to get video stats: {e}")
            return {}

    def _parse_duration(self, duration: str) -> int:
        """Parse ISO 8601 duration to seconds."""
        import re
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if not match:
            return 0
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        return hours * 3600 + minutes * 60 + seconds

    def _extract_hashtags(self, text: str) -> list[str]:
        """Extract hashtags from text."""
        import re
        return re.findall(r'#(\w+)', text)
