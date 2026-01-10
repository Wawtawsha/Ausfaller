import asyncio
import re
from datetime import datetime
from typing import Optional
from pathlib import Path
import logging

import instaloader
from instaloader import Hashtag, Profile, Post

from .base import BaseScraper, PostData, ScraperResult, Platform, ContentType
from config.settings import settings

logger = logging.getLogger(__name__)


class InstagramScraper(BaseScraper):
    """Instagram scraper using Instaloader for public data."""

    platform = Platform.INSTAGRAM

    def __init__(self):
        self._loader: Optional[instaloader.Instaloader] = None
        self._logged_in = False

    def _get_loader(self) -> instaloader.Instaloader:
        """Get or create Instaloader instance."""
        if self._loader is None:
            self._loader = instaloader.Instaloader(
                download_pictures=False,
                download_videos=False,
                download_video_thumbnails=False,
                download_geotags=False,
                download_comments=False,
                save_metadata=False,
                compress_json=False,
                quiet=True,
                user_agent=None,  # Uses default, rotate if needed
            )

            # Try to load saved session
            session_file = Path(settings.session_dir) / "instagram_session"
            if session_file.exists():
                try:
                    self._loader.load_session_from_file(
                        settings.instagram_username or "session",
                        str(session_file)
                    )
                    self._logged_in = True
                    logger.info("Loaded existing Instagram session")
                except Exception as e:
                    logger.warning(f"Failed to load session: {e}")

            # Try to login if credentials provided and not logged in
            if not self._logged_in and settings.instagram_username and settings.instagram_password:
                try:
                    self._loader.login(
                        settings.instagram_username,
                        settings.instagram_password
                    )
                    self._loader.save_session_to_file(str(session_file))
                    self._logged_in = True
                    logger.info("Instagram login successful")
                except Exception as e:
                    logger.warning(f"Instagram login failed: {e}")

        return self._loader

    def _extract_hashtags(self, caption: Optional[str]) -> list[str]:
        """Extract hashtags from caption text."""
        if not caption:
            return []
        return re.findall(r"#(\w+)", caption)

    def _determine_content_type(self, post: Post) -> ContentType:
        """Determine the content type of a post."""
        if post.typename == "GraphSidecar":
            return ContentType.CAROUSEL
        elif post.is_video:
            # Check if it's a reel (videos in reels have different characteristics)
            # Reels are typically vertical and have music
            if hasattr(post, "product_type") and post.product_type == "clips":
                return ContentType.REEL
            return ContentType.VIDEO
        else:
            return ContentType.IMAGE

    def _parse_post(self, post: Post) -> PostData:
        """Parse Instagram post into PostData."""
        caption = post.caption if post.caption else ""

        # Get owner info
        owner = post.owner_profile
        followers = None
        if owner:
            try:
                followers = owner.followers
            except Exception:
                pass  # May require login

        return PostData(
            platform=Platform.INSTAGRAM,
            platform_id=post.shortcode,
            content_type=self._determine_content_type(post),
            author_username=post.owner_username,
            author_followers=followers,
            caption=caption,
            hashtags=self._extract_hashtags(caption),
            likes=post.likes,
            comments=post.comments,
            shares=0,  # Instagram doesn't expose share counts
            views=post.video_view_count if post.is_video else 0,
            media_url=post.video_url if post.is_video else post.url,
            thumbnail_url=post.url,  # For videos, this is the thumbnail
            posted_at=post.date_utc,
        )

    async def get_hashtag_posts(
        self, hashtag: str, count: int = 30
    ) -> ScraperResult:
        """Get posts for a specific hashtag."""
        count = min(count, settings.max_posts_per_session)
        posts = []

        try:
            loader = self._get_loader()

            # Remove # if present
            hashtag = hashtag.lstrip("#")

            # Run in thread pool since instaloader is sync
            def fetch_posts():
                fetched = []
                try:
                    tag = Hashtag.from_name(loader.context, hashtag)
                    for i, post in enumerate(tag.get_posts()):
                        if i >= count:
                            break
                        try:
                            parsed = self._parse_post(post)
                            fetched.append(parsed)
                            logger.debug(f"Scraped Instagram #{hashtag}: {parsed.platform_id}")
                        except Exception as e:
                            logger.warning(f"Failed to parse post: {e}")
                            continue
                except Exception as e:
                    logger.error(f"Error fetching hashtag posts: {e}")
                return fetched

            loop = asyncio.get_event_loop()
            posts = await loop.run_in_executor(None, fetch_posts)

            # Add delays between posts (done in executor to not block)
            # Actually, the delay should be incorporated into fetch_posts
            # For now, we'll handle rate limiting at a higher level

            return ScraperResult(
                success=True,
                posts=posts,
                posts_requested=count,
                posts_retrieved=len(posts),
            )

        except Exception as e:
            logger.error(f"Instagram hashtag scrape failed: {e}")
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
            loader = self._get_loader()

            # Remove @ if present
            username = username.lstrip("@")

            def fetch_posts():
                fetched = []
                try:
                    profile = Profile.from_username(loader.context, username)
                    for i, post in enumerate(profile.get_posts()):
                        if i >= count:
                            break
                        try:
                            parsed = self._parse_post(post)
                            fetched.append(parsed)
                            logger.debug(f"Scraped Instagram @{username}: {parsed.platform_id}")
                        except Exception as e:
                            logger.warning(f"Failed to parse post: {e}")
                            continue
                except Exception as e:
                    logger.error(f"Error fetching user posts: {e}")
                return fetched

            loop = asyncio.get_event_loop()
            posts = await loop.run_in_executor(None, fetch_posts)

            return ScraperResult(
                success=True,
                posts=posts,
                posts_requested=count,
                posts_retrieved=len(posts),
            )

        except Exception as e:
            logger.error(f"Instagram user scrape failed: {e}")
            return ScraperResult(
                success=len(posts) > 0,
                posts=posts,
                error=str(e),
                posts_requested=count,
                posts_retrieved=len(posts),
            )

    async def get_trending(self, count: int = 30) -> ScraperResult:
        """
        Get trending content from Instagram.

        Note: Instagram doesn't have a public trending API.
        This will scrape from popular hashtags in the hospitality niche.
        For true explore page access, you need authenticated session.
        """
        # Use popular hospitality hashtags as a proxy for "trending"
        trending_hashtags = [
            "bartender",
            "nightlife",
            "cocktails",
            "foodtok",
            "barlife",
        ]

        all_posts = []
        posts_per_tag = max(1, count // len(trending_hashtags))

        for hashtag in trending_hashtags:
            result = await self.get_hashtag_posts(hashtag, posts_per_tag)
            all_posts.extend(result.posts)
            await self._random_delay()

            if len(all_posts) >= count:
                break

        # Sort by engagement (approximation of "trending")
        all_posts.sort(key=lambda p: p.likes + p.comments, reverse=True)

        return ScraperResult(
            success=True,
            posts=all_posts[:count],
            posts_requested=count,
            posts_retrieved=min(len(all_posts), count),
        )

    async def get_reels(self, username: str = None, count: int = 30) -> ScraperResult:
        """
        Get reels from a user or explore.

        Note: Requires authenticated session for explore reels.
        Without auth, can only get reels from public profiles.
        """
        if not username:
            # Can't get explore reels without auth
            return ScraperResult(
                success=False,
                error="Reels exploration requires authenticated session. Provide username for profile reels.",
                posts_requested=count,
                posts_retrieved=0,
            )

        # Get user posts and filter for reels
        result = await self.get_user_posts(username, count * 3)  # Fetch more to filter

        reels = [p for p in result.posts if p.content_type == ContentType.REEL]

        return ScraperResult(
            success=True,
            posts=reels[:count],
            posts_requested=count,
            posts_retrieved=min(len(reels), count),
        )

    async def close(self) -> None:
        """Cleanup Instaloader."""
        if self._loader:
            self._loader.close()
            self._loader = None
