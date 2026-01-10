import asyncio
import re
from datetime import datetime
from typing import Optional
import logging

from TikTokApi import TikTokApi
from playwright.async_api import async_playwright

from .base import BaseScraper, PostData, ScraperResult, Platform, ContentType
from config.settings import settings

logger = logging.getLogger(__name__)


class TikTokScraper(BaseScraper):
    """TikTok scraper using TikTokApi with Playwright fallback."""

    platform = Platform.TIKTOK

    def __init__(self):
        self._api: Optional[TikTokApi] = None
        self._playwright = None
        self._browser = None

    async def _get_api(self) -> TikTokApi:
        """Get or create TikTokApi instance."""
        if self._api is None:
            self._api = TikTokApi()
            # TikTokApi needs to create sessions with playwright
            await self._api.create_sessions(
                num_sessions=1,
                sleep_after=3,
                headless=True,
                ms_tokens=[settings.tiktok_ms_token] if settings.tiktok_ms_token else None,
            )
        return self._api

    def _extract_hashtags(self, text: str) -> list[str]:
        """Extract hashtags from caption text."""
        if not text:
            return []
        return re.findall(r"#(\w+)", text)

    def _parse_video(self, video_data: dict) -> PostData:
        """Parse TikTok video data into PostData."""
        author = video_data.get("author", {})
        stats = video_data.get("stats", {})
        music = video_data.get("music", {})

        caption = video_data.get("desc", "")

        # Parse timestamp
        posted_at = None
        create_time = video_data.get("createTime")
        if create_time:
            try:
                posted_at = datetime.fromtimestamp(int(create_time))
            except (ValueError, TypeError):
                pass

        return PostData(
            platform=Platform.TIKTOK,
            platform_id=str(video_data.get("id", "")),
            content_type=ContentType.VIDEO,
            author_username=author.get("uniqueId", ""),
            author_followers=author.get("stats", {}).get("followerCount"),
            caption=caption,
            hashtags=self._extract_hashtags(caption),
            likes=stats.get("diggCount", 0),
            comments=stats.get("commentCount", 0),
            shares=stats.get("shareCount", 0),
            views=stats.get("playCount", 0),
            media_url=video_data.get("video", {}).get("playAddr"),
            thumbnail_url=video_data.get("video", {}).get("cover"),
            posted_at=posted_at,
            sound_name=music.get("title"),
            sound_author=music.get("authorName"),
        )

    async def get_hashtag_posts(
        self, hashtag: str, count: int = 30
    ) -> ScraperResult:
        """Get posts for a specific hashtag."""
        # Limit to avoid detection
        count = min(count, settings.max_posts_per_session)
        posts = []

        try:
            api = await self._get_api()

            # Remove # if present
            hashtag = hashtag.lstrip("#")

            tag = api.hashtag(name=hashtag)
            async for video in tag.videos(count=count):
                await self._random_delay()
                try:
                    post = self._parse_video(video.as_dict)
                    posts.append(post)
                    logger.debug(f"Scraped TikTok #{hashtag}: {post.platform_id}")
                except Exception as e:
                    logger.warning(f"Failed to parse video: {e}")
                    continue

            return ScraperResult(
                success=True,
                posts=posts,
                posts_requested=count,
                posts_retrieved=len(posts),
            )

        except Exception as e:
            logger.error(f"TikTok hashtag scrape failed: {e}")
            return ScraperResult(
                success=len(posts) > 0,
                posts=posts,
                error=str(e),
                posts_requested=count,
                posts_retrieved=len(posts),
            )

    async def get_user_posts(
        self, username: str, count: int = 30
    ) -> ScraperResult:
        """Get recent posts from a user."""
        count = min(count, settings.max_posts_per_session)
        posts = []

        try:
            api = await self._get_api()

            # Remove @ if present
            username = username.lstrip("@")

            user = api.user(username=username)
            async for video in user.videos(count=count):
                await self._random_delay()
                try:
                    post = self._parse_video(video.as_dict)
                    posts.append(post)
                    logger.debug(f"Scraped TikTok @{username}: {post.platform_id}")
                except Exception as e:
                    logger.warning(f"Failed to parse video: {e}")
                    continue

            return ScraperResult(
                success=True,
                posts=posts,
                posts_requested=count,
                posts_retrieved=len(posts),
            )

        except Exception as e:
            logger.error(f"TikTok user scrape failed: {e}")
            return ScraperResult(
                success=len(posts) > 0,
                posts=posts,
                error=str(e),
                posts_requested=count,
                posts_retrieved=len(posts),
            )

    async def get_trending(self, count: int = 30) -> ScraperResult:
        """Get trending videos from TikTok."""
        count = min(count, settings.max_posts_per_session)
        posts = []

        try:
            api = await self._get_api()

            async for video in api.trending.videos(count=count):
                await self._random_delay()
                try:
                    post = self._parse_video(video.as_dict)
                    posts.append(post)
                    logger.debug(f"Scraped TikTok trending: {post.platform_id}")
                except Exception as e:
                    logger.warning(f"Failed to parse video: {e}")
                    continue

            return ScraperResult(
                success=True,
                posts=posts,
                posts_requested=count,
                posts_retrieved=len(posts),
            )

        except Exception as e:
            logger.error(f"TikTok trending scrape failed: {e}")
            return ScraperResult(
                success=len(posts) > 0,
                posts=posts,
                error=str(e),
                posts_requested=count,
                posts_retrieved=len(posts),
            )

    async def get_sound_posts(
        self, sound_id: str, count: int = 30
    ) -> ScraperResult:
        """Get posts using a specific sound/music."""
        count = min(count, settings.max_posts_per_session)
        posts = []

        try:
            api = await self._get_api()

            sound = api.sound(id=sound_id)
            async for video in sound.videos(count=count):
                await self._random_delay()
                try:
                    post = self._parse_video(video.as_dict)
                    posts.append(post)
                    logger.debug(f"Scraped TikTok sound {sound_id}: {post.platform_id}")
                except Exception as e:
                    logger.warning(f"Failed to parse video: {e}")
                    continue

            return ScraperResult(
                success=True,
                posts=posts,
                posts_requested=count,
                posts_retrieved=len(posts),
            )

        except Exception as e:
            logger.error(f"TikTok sound scrape failed: {e}")
            return ScraperResult(
                success=len(posts) > 0,
                posts=posts,
                error=str(e),
                posts_requested=count,
                posts_retrieved=len(posts),
            )

    async def close(self) -> None:
        """Cleanup TikTokApi sessions."""
        if self._api:
            await self._api.close_sessions()
            self._api = None
