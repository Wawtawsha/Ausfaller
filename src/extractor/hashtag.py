"""
Playwright-based extractor for hashtag pages.

Extracts video URLs and engagement stats from TikTok and Instagram hashtag pages.
Uses sync Playwright API with thread pool executor for Windows compatibility.
"""

import asyncio
import sys

# IMPORTANT: Set Windows-compatible event loop policy BEFORE importing Playwright
# This must happen before Playwright creates its internal event loop
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import random
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from pathlib import Path
import logging
import json
from playwright.sync_api import sync_playwright, Page, Browser, BrowserContext

from config.settings import settings

logger = logging.getLogger(__name__)


class Platform(str, Enum):
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"


@dataclass
class VideoInfo:
    """Extracted video information."""
    platform: Platform
    video_url: str
    video_id: str
    author_username: str
    thumbnail_url: Optional[str] = None
    likes: int = 0
    comments: int = 0
    views: int = 0
    shares: int = 0
    caption: Optional[str] = None
    hashtags: list[str] = field(default_factory=list)
    sound_name: Optional[str] = None
    extracted_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "platform": self.platform.value,
            "video_url": self.video_url,
            "video_id": self.video_id,
            "author_username": self.author_username,
            "thumbnail_url": self.thumbnail_url,
            "likes": self.likes,
            "comments": self.comments,
            "views": self.views,
            "shares": self.shares,
            "caption": self.caption,
            "hashtags": self.hashtags,
            "sound_name": self.sound_name,
            "extracted_at": self.extracted_at.isoformat(),
        }


@dataclass
class ExtractionResult:
    """Result from extraction operation."""
    success: bool
    videos: list[VideoInfo] = field(default_factory=list)
    error: Optional[str] = None
    videos_requested: int = 0
    videos_found: int = 0


class HashtagExtractor:
    """Extract video URLs from hashtag pages using Playwright (sync API with thread pool)."""

    def __init__(self):
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None

    def _get_browser_sync(self) -> Browser:
        """Get or create browser instance (sync version)."""
        if self._browser is None:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                ]
            )
        return self._browser

    def _get_context_sync(self) -> BrowserContext:
        """Get or create browser context with stealth settings (sync version)."""
        if self._context is None:
            browser = self._get_browser_sync()

            # Randomize viewport
            viewports = [
                {"width": 1920, "height": 1080},
                {"width": 1366, "height": 768},
                {"width": 1536, "height": 864},
                {"width": 1440, "height": 900},
            ]
            viewport = random.choice(viewports)

            self._context = browser.new_context(
                viewport=viewport,
                user_agent=self._get_random_user_agent(),
                locale="en-US",
                timezone_id="America/New_York",
            )

            # Load cookies if they exist
            cookies_file = Path(settings.session_dir) / "cookies.json"
            if cookies_file.exists():
                try:
                    cookies = json.loads(cookies_file.read_text())
                    self._context.add_cookies(cookies)
                    logger.info("Loaded saved cookies")
                except Exception as e:
                    logger.warning(f"Failed to load cookies: {e}")

        return self._context

    def _get_random_user_agent(self) -> str:
        """Get a random modern user agent."""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        ]
        return random.choice(user_agents)

    def _human_delay_sync(self) -> None:
        """Add human-like delay (sync version)."""
        import time
        delay = random.uniform(settings.scrape_delay_min, settings.scrape_delay_max)
        time.sleep(delay)

    def _scroll_page_sync(self, page: Page, scroll_count: int = 3) -> None:
        """Scroll page to load more content (sync version)."""
        import time
        for i in range(scroll_count):
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            time.sleep(random.uniform(1.0, 2.5))
            logger.debug(f"Scroll {i+1}/{scroll_count}")

    def _parse_count(self, text: str) -> int:
        """Parse engagement count from text (e.g., '1.2M' -> 1200000)."""
        if not text:
            return 0

        text = text.strip().upper().replace(",", "")

        try:
            if "K" in text:
                return int(float(text.replace("K", "")) * 1_000)
            elif "M" in text:
                return int(float(text.replace("M", "")) * 1_000_000)
            elif "B" in text:
                return int(float(text.replace("B", "")) * 1_000_000_000)
            else:
                return int(text)
        except (ValueError, TypeError):
            return 0

    def _extract_tiktok_hashtag_sync(
        self, hashtag: str, count: int = 30
    ) -> ExtractionResult:
        """Extract videos from TikTok hashtag page (sync version)."""
        hashtag = hashtag.lstrip("#")
        url = f"https://www.tiktok.com/tag/{hashtag}"
        videos = []

        try:
            context = self._get_context_sync()
            page = context.new_page()

            logger.info(f"Loading TikTok hashtag page: {url}")
            page.goto(url, wait_until="networkidle", timeout=30000)
            self._human_delay_sync()

            # Scroll to load more videos
            scroll_count = min(count // 10 + 1, 5)
            self._scroll_page_sync(page, scroll_count)

            # Extract video data from the page
            video_elements = page.query_selector_all('[data-e2e="challenge-item"]')

            if not video_elements:
                # Try alternate selector
                video_elements = page.query_selector_all('div[class*="DivItemContainer"]')

            logger.info(f"Found {len(video_elements)} video elements")

            for elem in video_elements[:count]:
                try:
                    # Extract video link
                    link_elem = elem.query_selector("a")
                    if not link_elem:
                        continue

                    video_url = link_elem.get_attribute("href")
                    if not video_url:
                        continue

                    if not video_url.startswith("http"):
                        video_url = f"https://www.tiktok.com{video_url}"

                    # Extract video ID from URL
                    video_id_match = re.search(r"/video/(\d+)", video_url)
                    video_id = video_id_match.group(1) if video_id_match else ""

                    # Extract author from URL
                    author_match = re.search(r"@([^/]+)", video_url)
                    author = author_match.group(1) if author_match else ""

                    # Try to get engagement stats
                    likes = 0
                    likes_elem = elem.query_selector('[data-e2e="video-like-count"], strong[data-e2e="like-count"]')
                    if likes_elem:
                        likes_text = likes_elem.inner_text()
                        likes = self._parse_count(likes_text)

                    # Get thumbnail
                    thumbnail_url = None
                    img_elem = elem.query_selector("img")
                    if img_elem:
                        thumbnail_url = img_elem.get_attribute("src")

                    video_info = VideoInfo(
                        platform=Platform.TIKTOK,
                        video_url=video_url,
                        video_id=video_id,
                        author_username=author,
                        thumbnail_url=thumbnail_url,
                        likes=likes,
                    )
                    videos.append(video_info)
                    logger.debug(f"Extracted: {video_url}")

                except Exception as e:
                    logger.warning(f"Failed to extract video element: {e}")
                    continue

            page.close()

            return ExtractionResult(
                success=True,
                videos=videos,
                videos_requested=count,
                videos_found=len(videos),
            )

        except Exception as e:
            logger.error(f"TikTok extraction failed: {e}")
            return ExtractionResult(
                success=False,
                videos=videos,
                error=str(e),
                videos_requested=count,
                videos_found=len(videos),
            )

    async def extract_tiktok_hashtag(
        self, hashtag: str, count: int = 30
    ) -> ExtractionResult:
        """Extract videos from TikTok hashtag page using subprocess for Windows compatibility."""
        import subprocess
        import json as json_module

        # Create extraction script that runs Playwright synchronously in a fresh Python process
        script = f'''
import sys
sys.path.insert(0, r"{Path(__file__).parent.parent.parent}")

# Import only what we need to avoid triggering the async policy at module level
from playwright.sync_api import sync_playwright
import json
import re
import random
import time

def extract():
    hashtag = "{hashtag}"
    count = {count}
    url = f"https://www.tiktok.com/tag/{{hashtag}}"
    videos = []

    try:
        pw = sync_playwright().start()
        browser = pw.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--disable-dev-shm-usage", "--no-sandbox"]
        )
        context = browser.new_context(
            viewport={{"width": 1920, "height": 1080}},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
        )
        page = context.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        time.sleep(random.uniform(2, 4))

        # Scroll
        for _ in range(min(count // 10 + 1, 3)):
            page.evaluate("window.scrollBy(0, window.innerHeight)")
            time.sleep(random.uniform(1, 2.5))

        video_elements = page.query_selector_all('[data-e2e="challenge-item"]')
        if not video_elements:
            video_elements = page.query_selector_all('div[class*="DivItemContainer"]')

        for elem in video_elements[:count]:
            try:
                link_elem = elem.query_selector("a")
                if not link_elem:
                    continue
                video_url = link_elem.get_attribute("href")
                if not video_url:
                    continue
                if not video_url.startswith("http"):
                    video_url = f"https://www.tiktok.com{{video_url}}"

                video_id_match = re.search(r"/video/(\\d+)", video_url)
                video_id = video_id_match.group(1) if video_id_match else ""
                author_match = re.search(r"@([^/]+)", video_url)
                author = author_match.group(1) if author_match else ""

                likes = 0
                likes_elem = elem.query_selector('[data-e2e="video-like-count"], strong[data-e2e="like-count"]')
                if likes_elem:
                    likes_text = likes_elem.inner_text().strip().upper().replace(",", "")
                    if "K" in likes_text:
                        likes = int(float(likes_text.replace("K", "")) * 1000)
                    elif "M" in likes_text:
                        likes = int(float(likes_text.replace("M", "")) * 1000000)
                    else:
                        try:
                            likes = int(likes_text)
                        except:
                            pass

                thumbnail = None
                img = elem.query_selector("img")
                if img:
                    thumbnail = img.get_attribute("src")

                videos.append({{
                    "video_url": video_url,
                    "video_id": video_id,
                    "author_username": author,
                    "thumbnail_url": thumbnail,
                    "likes": likes,
                    "platform": "tiktok"
                }})
            except Exception as e:
                continue

        page.close()
        context.close()
        browser.close()
        pw.stop()

        print(json.dumps({{
            "success": True,
            "videos": videos,
            "videos_found": len(videos),
            "videos_requested": count,
            "error": None
        }}))
    except Exception as e:
        print(json.dumps({{
            "success": False,
            "videos": [],
            "videos_found": 0,
            "videos_requested": count,
            "error": str(e)
        }}))

extract()
'''

        try:
            venv_python = Path(__file__).parent.parent.parent / "venv" / "Scripts" / "python.exe"
            result = subprocess.run(
                [str(venv_python), "-c", script],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(Path(__file__).parent.parent.parent)
            )

            if result.returncode != 0:
                logger.error(f"Subprocess failed: {result.stderr}")
                return ExtractionResult(
                    success=False,
                    error=result.stderr,
                    videos_requested=count,
                )

            data = json_module.loads(result.stdout)
            videos = [VideoInfo(
                platform=Platform.TIKTOK,
                video_url=v["video_url"],
                video_id=v["video_id"],
                author_username=v["author_username"],
                thumbnail_url=v.get("thumbnail_url"),
                likes=v.get("likes", 0),
                comments=v.get("comments", 0),
                views=v.get("views", 0),
                shares=v.get("shares", 0),
                caption=v.get("caption"),
                hashtags=v.get("hashtags", []),
                sound_name=v.get("sound_name"),
            ) for v in data["videos"]]

            return ExtractionResult(
                success=data["success"],
                videos=videos,
                videos_found=data["videos_found"],
                videos_requested=data["videos_requested"],
                error=data.get("error"),
            )

        except subprocess.TimeoutExpired:
            return ExtractionResult(
                success=False,
                error="Extraction timed out",
                videos_requested=count,
            )
        except Exception as e:
            logger.error(f"Subprocess extraction failed: {e}")
            return ExtractionResult(
                success=False,
                error=str(e),
                videos_requested=count,
            )

    def _extract_instagram_hashtag_sync(
        self, hashtag: str, count: int = 30
    ) -> ExtractionResult:
        """Extract videos/posts from Instagram hashtag page (sync version)."""
        hashtag = hashtag.lstrip("#")
        url = f"https://www.instagram.com/explore/tags/{hashtag}/"
        videos = []

        try:
            context = self._get_context_sync()
            page = context.new_page()

            logger.info(f"Loading Instagram hashtag page: {url}")
            page.goto(url, wait_until="networkidle", timeout=30000)
            self._human_delay_sync()

            # Check for login wall
            login_wall = page.query_selector('input[name="username"]')
            if login_wall:
                logger.warning("Instagram login wall detected - limited access")

            # Scroll to load more
            scroll_count = min(count // 12 + 1, 5)
            self._scroll_page_sync(page, scroll_count)

            # Extract post links
            post_links = page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')

            logger.info(f"Found {len(post_links)} post elements")

            seen_urls = set()
            for link_elem in post_links:
                if len(videos) >= count:
                    break

                try:
                    href = link_elem.get_attribute("href")
                    if not href or href in seen_urls:
                        continue

                    seen_urls.add(href)

                    if not href.startswith("http"):
                        href = f"https://www.instagram.com{href}"

                    # Extract post ID
                    post_id_match = re.search(r"/(?:p|reel)/([^/]+)", href)
                    post_id = post_id_match.group(1) if post_id_match else ""

                    # Get thumbnail
                    thumbnail_url = None
                    img_elem = link_elem.query_selector("img")
                    if img_elem:
                        thumbnail_url = img_elem.get_attribute("src")

                    video_info = VideoInfo(
                        platform=Platform.INSTAGRAM,
                        video_url=href,
                        video_id=post_id,
                        author_username="",  # Would need to visit post page to get this
                        thumbnail_url=thumbnail_url,
                    )
                    videos.append(video_info)
                    logger.debug(f"Extracted: {href}")

                except Exception as e:
                    logger.warning(f"Failed to extract post element: {e}")
                    continue

            page.close()

            return ExtractionResult(
                success=True,
                videos=videos,
                videos_requested=count,
                videos_found=len(videos),
            )

        except Exception as e:
            logger.error(f"Instagram extraction failed: {e}")
            return ExtractionResult(
                success=False,
                videos=videos,
                error=str(e),
                videos_requested=count,
                videos_found=len(videos),
            )

    async def extract_instagram_hashtag(
        self, hashtag: str, count: int = 30
    ) -> ExtractionResult:
        """Extract videos/posts from Instagram hashtag page (async wrapper)."""
        return await asyncio.to_thread(
            self._extract_instagram_hashtag_sync,
            hashtag,
            count
        )

    async def extract_hashtag(
        self, platform: Platform, hashtag: str, count: int = 30
    ) -> ExtractionResult:
        """Extract from either platform."""
        if platform == Platform.TIKTOK:
            return await self.extract_tiktok_hashtag(hashtag, count)
        elif platform == Platform.INSTAGRAM:
            return await self.extract_instagram_hashtag(hashtag, count)
        else:
            return ExtractionResult(
                success=False,
                error=f"Unknown platform: {platform}",
                videos_requested=count,
            )

    def _save_cookies_sync(self) -> None:
        """Save current cookies for session persistence (sync version)."""
        if self._context:
            cookies = self._context.cookies()
            cookies_file = Path(settings.session_dir) / "cookies.json"
            cookies_file.write_text(json.dumps(cookies, indent=2))
            logger.info("Saved cookies for session persistence")

    async def save_cookies(self) -> None:
        """Save current cookies for session persistence (async wrapper)."""
        await asyncio.to_thread(self._save_cookies_sync)

    def _close_sync(self) -> None:
        """Cleanup browser resources (sync version)."""
        self._save_cookies_sync()

        if self._context:
            self._context.close()
            self._context = None

        if self._browser:
            self._browser.close()
            self._browser = None

        if self._playwright:
            self._playwright.stop()
            self._playwright = None

    async def close(self) -> None:
        """Cleanup browser resources (async wrapper)."""
        await asyncio.to_thread(self._close_sync)
