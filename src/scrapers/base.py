from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum
import asyncio
import random

from config.settings import settings


class Platform(str, Enum):
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"


class ContentType(str, Enum):
    VIDEO = "video"
    IMAGE = "image"
    CAROUSEL = "carousel"
    REEL = "reel"


@dataclass
class PostData:
    """Standardized post data across platforms."""

    platform: Platform
    platform_id: str
    content_type: ContentType

    # Author info
    author_username: str
    author_followers: Optional[int] = None

    # Content
    caption: Optional[str] = None
    hashtags: list[str] = field(default_factory=list)

    # Engagement
    likes: int = 0
    comments: int = 0
    shares: int = 0
    views: int = 0

    # Media URLs
    media_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

    # Timestamps
    posted_at: Optional[datetime] = None
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    # TikTok specific
    sound_name: Optional[str] = None
    sound_author: Optional[str] = None

    @property
    def engagement_rate(self) -> float:
        """Calculate engagement rate based on available metrics."""
        if self.views > 0:
            return (self.likes + self.comments + self.shares) / self.views
        elif self.author_followers and self.author_followers > 0:
            return (self.likes + self.comments) / self.author_followers
        return 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "platform": self.platform.value,
            "platform_id": self.platform_id,
            "content_type": self.content_type.value,
            "author_username": self.author_username,
            "author_followers": self.author_followers,
            "caption": self.caption,
            "hashtags": self.hashtags,
            "likes": self.likes,
            "comments": self.comments,
            "shares": self.shares,
            "views": self.views,
            "engagement_rate": self.engagement_rate,
            "media_url": self.media_url,
            "thumbnail_url": self.thumbnail_url,
            "posted_at": self.posted_at.isoformat() if self.posted_at else None,
            "scraped_at": self.scraped_at.isoformat(),
            "sound_name": self.sound_name,
            "sound_author": self.sound_author,
        }


@dataclass
class ScraperResult:
    """Result from a scraping operation."""

    success: bool
    posts: list[PostData] = field(default_factory=list)
    error: Optional[str] = None
    posts_requested: int = 0
    posts_retrieved: int = 0

    @property
    def partial_success(self) -> bool:
        return self.posts_retrieved > 0 and self.posts_retrieved < self.posts_requested


class BaseScraper(ABC):
    """Abstract base class for platform scrapers."""

    platform: Platform

    async def _random_delay(self) -> None:
        """Add human-like delay between requests."""
        delay = random.uniform(settings.scrape_delay_min, settings.scrape_delay_max)
        await asyncio.sleep(delay)

    @abstractmethod
    async def get_hashtag_posts(
        self, hashtag: str, count: int = 30
    ) -> ScraperResult:
        """Get posts for a specific hashtag."""
        pass

    @abstractmethod
    async def get_user_posts(
        self, username: str, count: int = 30
    ) -> ScraperResult:
        """Get recent posts from a user."""
        pass

    @abstractmethod
    async def get_trending(self, count: int = 30) -> ScraperResult:
        """Get trending/popular content."""
        pass

    async def close(self) -> None:
        """Cleanup resources. Override if needed."""
        pass
