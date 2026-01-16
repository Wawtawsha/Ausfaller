"""
Instagram extractor using instagrapi.

Extracts posts, reels, and stories from Instagram hashtags and user profiles
using the Instagram Private API via instagrapi library.
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from instagrapi import Client
from instagrapi.exceptions import (
    LoginRequired,
    ChallengeRequired,
    BadPassword,
    TwoFactorRequired,
)

from config.settings import settings
from src.extractor.hashtag import Platform, VideoInfo, ExtractionResult

logger = logging.getLogger(__name__)

# Thread pool for running sync instagrapi calls
_executor = ThreadPoolExecutor(max_workers=2)


@dataclass
class InstagramComment:
    """Instagram comment data."""
    username: str
    text: str
    created_at: datetime
    likes: int = 0


class InstagramExtractor:
    """Extract Instagram content using instagrapi (Instagram Private API)."""

    def __init__(
        self,
        session_path: str = "instagram_session.json",
        proxy: Optional[str] = None
    ):
        """
        Initialize Instagram extractor.

        Args:
            session_path: Path to save/load session file
            proxy: Optional proxy URL (socks5://user:pass@host:port)
        """
        self.cl = Client()
        self.cl.delay_range = [2, 5]  # Random delay between requests
        self.session_path = Path(session_path)
        self._logged_in = False

        if proxy:
            self.cl.set_proxy(proxy)
            logger.info(f"Instagram extractor using proxy")

    def _login_sync(self, username: str, password: str) -> bool:
        """Sync login with session management."""
        # Try to restore existing session first
        if self.session_path.exists():
            try:
                self.cl.load_settings(self.session_path)
                self.cl.get_timeline_feed()  # Verify session is valid
                logger.info("Restored existing Instagram session")
                self._logged_in = True
                return True
            except Exception as e:
                logger.info(f"Session expired or invalid: {e}")

        # Fresh login
        try:
            self.cl.login(username, password)
            self.cl.dump_settings(self.session_path)
            logger.info("Instagram login successful, session saved")
            self._logged_in = True
            return True
        except TwoFactorRequired:
            logger.error("2FA required - provide verification code")
            raise
        except ChallengeRequired:
            logger.error("Challenge required - manual verification needed")
            raise
        except BadPassword:
            logger.error("Invalid Instagram password")
            raise
        except Exception as e:
            logger.error(f"Instagram login failed: {e}")
            raise

    async def login(self, username: str = None, password: str = None) -> bool:
        """
        Login to Instagram or restore session.

        Args:
            username: Instagram username (defaults to env var)
            password: Instagram password (defaults to env var)

        Returns:
            True if login successful
        """
        username = username or getattr(settings, 'instagram_username', None)
        password = password or getattr(settings, 'instagram_password', None)

        if not username or not password:
            raise ValueError(
                "Instagram credentials required. Set INSTAGRAM_USERNAME and "
                "INSTAGRAM_PASSWORD in .env or pass as arguments"
            )

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _executor, self._login_sync, username, password
        )

    def _get_hashtag_posts_sync(self, hashtag: str, limit: int) -> list[VideoInfo]:
        """Sync method to get hashtag posts."""
        if not self._logged_in:
            raise LoginRequired("Must login before extracting")

        videos = []
        try:
            medias = self.cl.hashtag_medias_recent(hashtag, amount=limit)
            for media in medias:
                video_info = self._media_to_video_info(media)
                if video_info:
                    videos.append(video_info)
        except Exception as e:
            logger.error(f"Failed to get hashtag posts: {e}")
            raise

        return videos

    async def get_hashtag_posts(
        self,
        hashtag: str,
        limit: int = 50
    ) -> ExtractionResult:
        """
        Get recent posts for a hashtag.

        Args:
            hashtag: Hashtag to search (without #)
            limit: Maximum posts to retrieve

        Returns:
            ExtractionResult with list of VideoInfo objects
        """
        try:
            loop = asyncio.get_event_loop()
            videos = await loop.run_in_executor(
                _executor, self._get_hashtag_posts_sync, hashtag, limit
            )
            return ExtractionResult(
                success=True,
                videos=videos,
                videos_requested=limit,
                videos_found=len(videos),
            )
        except LoginRequired as e:
            return ExtractionResult(
                success=False,
                error="Not logged in - call login() first",
                videos_requested=limit,
            )
        except Exception as e:
            logger.error(f"Hashtag extraction failed: {e}")
            return ExtractionResult(
                success=False,
                error=str(e),
                videos_requested=limit,
            )

    def _get_user_posts_sync(self, username: str, limit: int) -> list[VideoInfo]:
        """Sync method to get user posts."""
        if not self._logged_in:
            raise LoginRequired("Must login before extracting")

        videos = []
        try:
            user_id = self.cl.user_id_from_username(username)
            medias = self.cl.user_medias(user_id, amount=limit)
            for media in medias:
                video_info = self._media_to_video_info(media)
                if video_info:
                    videos.append(video_info)
        except Exception as e:
            logger.error(f"Failed to get user posts: {e}")
            raise

        return videos

    async def get_user_posts(
        self,
        username: str,
        limit: int = 20
    ) -> ExtractionResult:
        """
        Get posts from a specific user.

        Args:
            username: Instagram username
            limit: Maximum posts to retrieve

        Returns:
            ExtractionResult with list of VideoInfo objects
        """
        try:
            loop = asyncio.get_event_loop()
            videos = await loop.run_in_executor(
                _executor, self._get_user_posts_sync, username, limit
            )
            return ExtractionResult(
                success=True,
                videos=videos,
                videos_requested=limit,
                videos_found=len(videos),
            )
        except LoginRequired:
            return ExtractionResult(
                success=False,
                error="Not logged in - call login() first",
                videos_requested=limit,
            )
        except Exception as e:
            logger.error(f"User extraction failed: {e}")
            return ExtractionResult(
                success=False,
                error=str(e),
                videos_requested=limit,
            )

    def _get_post_comments_sync(
        self,
        media_id: str,
        limit: int
    ) -> list[InstagramComment]:
        """Sync method to get post comments."""
        if not self._logged_in:
            raise LoginRequired("Must login before extracting")

        comments_list = []
        try:
            comments = self.cl.media_comments(media_id, amount=limit)
            for c in comments:
                comments_list.append(InstagramComment(
                    username=c.user.username,
                    text=c.text,
                    created_at=c.created_at,
                    likes=getattr(c, 'like_count', 0) or 0,
                ))
        except Exception as e:
            logger.error(f"Failed to get comments: {e}")
            raise

        return comments_list

    async def get_post_comments(
        self,
        media_id: str,
        limit: int = 100
    ) -> list[InstagramComment]:
        """
        Get comments on a post.

        Args:
            media_id: Instagram media ID (pk)
            limit: Maximum comments to retrieve

        Returns:
            List of InstagramComment objects
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            _executor, self._get_post_comments_sync, media_id, limit
        )

    def _media_to_video_info(self, media) -> Optional[VideoInfo]:
        """Convert instagrapi Media object to VideoInfo."""
        try:
            # media_type: 1=Photo, 2=Video, 8=Album
            media_type = media.media_type

            # Get the video/image URL
            video_url = None
            if media_type == 2 and media.video_url:
                video_url = str(media.video_url)
            elif media.thumbnail_url:
                video_url = str(media.thumbnail_url)

            # Extract hashtags from caption
            hashtags = []
            caption = media.caption_text or ""
            if caption:
                import re
                hashtags = re.findall(r'#(\w+)', caption)

            return VideoInfo(
                platform=Platform.INSTAGRAM,
                video_url=f"https://instagram.com/p/{media.code}",
                video_id=str(media.pk),
                author_username=media.user.username if media.user else "",
                thumbnail_url=str(media.thumbnail_url) if media.thumbnail_url else None,
                likes=media.like_count or 0,
                comments=media.comment_count or 0,
                views=media.view_count or 0 if media_type == 2 else 0,
                caption=caption,
                hashtags=hashtags,
                extracted_at=datetime.utcnow(),
            )
        except Exception as e:
            logger.warning(f"Failed to convert media: {e}")
            return None

    @property
    def is_logged_in(self) -> bool:
        """Check if currently logged in."""
        return self._logged_in

    def logout(self):
        """Logout and clear session."""
        try:
            self.cl.logout()
        except Exception:
            pass
        self._logged_in = False
        if self.session_path.exists():
            self.session_path.unlink()
        logger.info("Logged out of Instagram")
