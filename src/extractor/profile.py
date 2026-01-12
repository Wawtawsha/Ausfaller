"""
Profile extractor for TikTok and Instagram user profiles.

Extracts profile metadata and video URLs from user profile pages.
Uses subprocess for Windows compatibility (same pattern as hashtag.py).
"""

import asyncio
import sys
import subprocess
import json
import re
import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from pathlib import Path
import logging

from src.extractor.hashtag import Platform, VideoInfo

logger = logging.getLogger(__name__)


@dataclass
class ProfileInfo:
    """Extracted profile information."""
    platform: Platform
    username: str
    display_name: str = ""
    bio: str = ""
    profile_picture_url: Optional[str] = None
    follower_count: int = 0
    following_count: int = 0
    post_count: int = 0
    is_verified: bool = False
    is_private: bool = False

    def to_dict(self) -> dict:
        return {
            "platform": self.platform.value,
            "username": self.username,
            "display_name": self.display_name,
            "bio": self.bio,
            "profile_picture_url": self.profile_picture_url,
            "follower_count": self.follower_count,
            "following_count": self.following_count,
            "post_count": self.post_count,
            "is_verified": self.is_verified,
            "is_private": self.is_private,
        }


@dataclass
class ProfileExtractionResult:
    """Result from profile extraction operation."""
    success: bool
    profile_info: Optional[ProfileInfo] = None
    videos: list[VideoInfo] = field(default_factory=list)
    error: Optional[str] = None
    videos_requested: int = 0
    videos_found: int = 0


class ProfileExtractor:
    """Extract profile info and videos from user profile pages."""

    async def extract_tiktok_profile(
        self, username: str, video_count: int = 30
    ) -> ProfileExtractionResult:
        """Extract profile info and videos from TikTok profile page."""
        username = username.lstrip("@")

        # Subprocess script for TikTok profile extraction
        script = f'''
import sys
sys.path.insert(0, r"{Path(__file__).parent.parent.parent}")

from playwright.sync_api import sync_playwright
import json
import re
import random
import time

def parse_count(text):
    """Parse engagement count (e.g., '1.2M' -> 1200000)."""
    if not text:
        return 0
    text = text.strip().upper().replace(",", "")
    try:
        if "K" in text:
            return int(float(text.replace("K", "")) * 1000)
        elif "M" in text:
            return int(float(text.replace("M", "")) * 1000000)
        elif "B" in text:
            return int(float(text.replace("B", "")) * 1000000000)
        else:
            return int(text)
    except (ValueError, TypeError):
        return 0

def extract():
    username = "{username}"
    video_count = {video_count}
    url = f"https://www.tiktok.com/@{{username}}"
    videos = []
    profile_info = None

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

        # Check for private account
        is_private = False
        private_indicators = page.query_selector_all('text=/[Pp]rivate/')
        if private_indicators:
            is_private = True

        # Extract profile info
        display_name = ""
        bio = ""
        follower_count = 0
        following_count = 0
        post_count = 0
        is_verified = False
        profile_picture_url = None

        # Display name
        name_elem = page.query_selector('h1[data-e2e="user-subtitle"], h2[data-e2e="user-subtitle"]')
        if name_elem:
            display_name = name_elem.inner_text().strip()

        # Bio
        bio_elem = page.query_selector('h2[data-e2e="user-bio"]')
        if bio_elem:
            bio = bio_elem.inner_text().strip()

        # Stats - look for follower/following/likes counts
        stat_elements = page.query_selector_all('[data-e2e="followers-count"], [data-e2e="following-count"], [data-e2e="likes-count"]')
        for elem in stat_elements:
            e2e = elem.get_attribute("data-e2e") or ""
            count_text = elem.inner_text()
            if "followers" in e2e:
                follower_count = parse_count(count_text)
            elif "following" in e2e:
                following_count = parse_count(count_text)

        # Verified badge
        verified_elem = page.query_selector('[data-e2e="user-verified"], svg[class*="Verified"]')
        if verified_elem:
            is_verified = True

        # Profile picture
        avatar_elem = page.query_selector('img[data-e2e="user-avatar"]')
        if avatar_elem:
            profile_picture_url = avatar_elem.get_attribute("src")

        # Scroll to load videos
        if not is_private:
            for _ in range(min(video_count // 10 + 1, 5)):
                page.evaluate("window.scrollBy(0, window.innerHeight)")
                time.sleep(random.uniform(1, 2.5))

            # Extract video elements from profile grid
            video_elements = page.query_selector_all('[data-e2e="user-post-item"]')
            if not video_elements:
                video_elements = page.query_selector_all('div[class*="DivItemContainer"]')

            post_count = len(video_elements)

            for elem in video_elements[:video_count]:
                try:
                    link_elem = elem.query_selector("a")
                    if not link_elem:
                        continue

                    video_url = link_elem.get_attribute("href")
                    if not video_url:
                        continue
                    if not video_url.startswith("http"):
                        video_url = f"https://www.tiktok.com{{video_url}}"

                    # Extract video ID
                    video_id_match = re.search(r"/video/(\\d+)", video_url)
                    video_id = video_id_match.group(1) if video_id_match else ""

                    # Likes
                    likes = 0
                    likes_elem = elem.query_selector('[data-e2e="video-like-count"], strong[data-e2e="like-count"]')
                    if likes_elem:
                        likes = parse_count(likes_elem.inner_text())

                    # Views (often shown on profile grid)
                    views = 0
                    views_elem = elem.query_selector('[data-e2e="video-views"], strong[class*="views"]')
                    if views_elem:
                        views = parse_count(views_elem.inner_text())

                    # Thumbnail
                    thumbnail = None
                    img = elem.query_selector("img")
                    if img:
                        thumbnail = img.get_attribute("src")

                    videos.append({{
                        "video_url": video_url,
                        "video_id": video_id,
                        "author_username": username,
                        "thumbnail_url": thumbnail,
                        "likes": likes,
                        "views": views,
                        "platform": "tiktok"
                    }})
                except Exception:
                    continue

        profile_info = {{
            "platform": "tiktok",
            "username": username,
            "display_name": display_name,
            "bio": bio,
            "profile_picture_url": profile_picture_url,
            "follower_count": follower_count,
            "following_count": following_count,
            "post_count": post_count,
            "is_verified": is_verified,
            "is_private": is_private
        }}

        page.close()
        context.close()
        browser.close()
        pw.stop()

        print(json.dumps({{
            "success": True,
            "profile_info": profile_info,
            "videos": videos,
            "videos_found": len(videos),
            "videos_requested": video_count,
            "error": None
        }}))
    except Exception as e:
        print(json.dumps({{
            "success": False,
            "profile_info": None,
            "videos": [],
            "videos_found": 0,
            "videos_requested": video_count,
            "error": str(e)
        }}))

extract()
'''

        try:
            base_path = Path(__file__).parent.parent.parent / "venv"
            if sys.platform == "win32":
                venv_python = base_path / "Scripts" / "python.exe"
            else:
                venv_python = base_path / "bin" / "python"

            if not venv_python.exists():
                venv_python = sys.executable

            result = subprocess.run(
                [str(venv_python), "-c", script],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(Path(__file__).parent.parent.parent)
            )

            if result.returncode != 0:
                logger.error(f"Subprocess failed: {result.stderr}")
                return ProfileExtractionResult(
                    success=False,
                    error=result.stderr,
                    videos_requested=video_count,
                )

            data = json.loads(result.stdout)

            profile_info = None
            if data.get("profile_info"):
                pi = data["profile_info"]
                profile_info = ProfileInfo(
                    platform=Platform.TIKTOK,
                    username=pi["username"],
                    display_name=pi.get("display_name", ""),
                    bio=pi.get("bio", ""),
                    profile_picture_url=pi.get("profile_picture_url"),
                    follower_count=pi.get("follower_count", 0),
                    following_count=pi.get("following_count", 0),
                    post_count=pi.get("post_count", 0),
                    is_verified=pi.get("is_verified", False),
                    is_private=pi.get("is_private", False),
                )

            videos = [VideoInfo(
                platform=Platform.TIKTOK,
                video_url=v["video_url"],
                video_id=v["video_id"],
                author_username=v["author_username"],
                thumbnail_url=v.get("thumbnail_url"),
                likes=v.get("likes", 0),
                views=v.get("views", 0),
            ) for v in data.get("videos", [])]

            return ProfileExtractionResult(
                success=data["success"],
                profile_info=profile_info,
                videos=videos,
                videos_found=data.get("videos_found", 0),
                videos_requested=data.get("videos_requested", video_count),
                error=data.get("error"),
            )

        except subprocess.TimeoutExpired:
            return ProfileExtractionResult(
                success=False,
                error="Profile extraction timed out",
                videos_requested=video_count,
            )
        except Exception as e:
            logger.error(f"Profile extraction failed: {e}")
            return ProfileExtractionResult(
                success=False,
                error=str(e),
                videos_requested=video_count,
            )

    async def extract_instagram_profile(
        self, username: str, video_count: int = 30
    ) -> ProfileExtractionResult:
        """Extract profile info and videos from Instagram profile page."""
        username = username.lstrip("@")

        script = f'''
import sys
sys.path.insert(0, r"{Path(__file__).parent.parent.parent}")

from playwright.sync_api import sync_playwright
import json
import re
import random
import time

def parse_count(text):
    if not text:
        return 0
    text = text.strip().upper().replace(",", "")
    try:
        if "K" in text:
            return int(float(text.replace("K", "")) * 1000)
        elif "M" in text:
            return int(float(text.replace("M", "")) * 1000000)
        elif "B" in text:
            return int(float(text.replace("B", "")) * 1000000000)
        else:
            return int(text)
    except (ValueError, TypeError):
        return 0

def extract():
    username = "{username}"
    video_count = {video_count}
    url = f"https://www.instagram.com/{{username}}/"
    videos = []
    profile_info = None

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

        # Check for login wall
        login_wall = page.query_selector('input[name="username"]')

        # Check for private account
        is_private = False
        private_text = page.query_selector('text=/[Pp]rivate/')
        if private_text:
            is_private = True

        # Extract profile info from meta tags or page content
        display_name = ""
        bio = ""
        follower_count = 0
        following_count = 0
        post_count = 0
        is_verified = False
        profile_picture_url = None

        # Try meta description for basic info
        meta_desc = page.query_selector('meta[name="description"]')
        if meta_desc:
            content = meta_desc.get_attribute("content") or ""
            # Format: "X Followers, X Following, X Posts - See Instagram photos and videos from Name (@username)"
            followers_match = re.search(r"([\\d,.]+[KMB]?)\\s*[Ff]ollowers", content)
            following_match = re.search(r"([\\d,.]+[KMB]?)\\s*[Ff]ollowing", content)
            posts_match = re.search(r"([\\d,.]+[KMB]?)\\s*[Pp]osts", content)

            if followers_match:
                follower_count = parse_count(followers_match.group(1))
            if following_match:
                following_count = parse_count(following_match.group(1))
            if posts_match:
                post_count = parse_count(posts_match.group(1))

        # Display name from header
        header_elem = page.query_selector('header section h1, header h2')
        if header_elem:
            display_name = header_elem.inner_text().strip()

        # Profile picture
        avatar_elem = page.query_selector('header img')
        if avatar_elem:
            profile_picture_url = avatar_elem.get_attribute("src")

        # Verified badge
        verified_elem = page.query_selector('header svg[aria-label*="Verified"], span[title="Verified"]')
        if verified_elem:
            is_verified = True

        # Scroll and extract posts if not private
        if not is_private and not login_wall:
            for _ in range(min(video_count // 12 + 1, 5)):
                page.evaluate("window.scrollBy(0, window.innerHeight)")
                time.sleep(random.uniform(1, 2.5))

            post_links = page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
            seen_urls = set()

            for link_elem in post_links:
                if len(videos) >= video_count:
                    break

                try:
                    href = link_elem.get_attribute("href")
                    if not href or href in seen_urls:
                        continue

                    seen_urls.add(href)

                    if not href.startswith("http"):
                        href = f"https://www.instagram.com{{href}}"

                    post_id_match = re.search(r"/(?:p|reel)/([^/]+)", href)
                    post_id = post_id_match.group(1) if post_id_match else ""

                    thumbnail = None
                    img = link_elem.query_selector("img")
                    if img:
                        thumbnail = img.get_attribute("src")

                    videos.append({{
                        "video_url": href,
                        "video_id": post_id,
                        "author_username": username,
                        "thumbnail_url": thumbnail,
                        "platform": "instagram"
                    }})
                except Exception:
                    continue

        profile_info = {{
            "platform": "instagram",
            "username": username,
            "display_name": display_name,
            "bio": bio,
            "profile_picture_url": profile_picture_url,
            "follower_count": follower_count,
            "following_count": following_count,
            "post_count": post_count,
            "is_verified": is_verified,
            "is_private": is_private
        }}

        page.close()
        context.close()
        browser.close()
        pw.stop()

        print(json.dumps({{
            "success": True,
            "profile_info": profile_info,
            "videos": videos,
            "videos_found": len(videos),
            "videos_requested": video_count,
            "error": None
        }}))
    except Exception as e:
        print(json.dumps({{
            "success": False,
            "profile_info": None,
            "videos": [],
            "videos_found": 0,
            "videos_requested": video_count,
            "error": str(e)
        }}))

extract()
'''

        try:
            base_path = Path(__file__).parent.parent.parent / "venv"
            if sys.platform == "win32":
                venv_python = base_path / "Scripts" / "python.exe"
            else:
                venv_python = base_path / "bin" / "python"

            if not venv_python.exists():
                venv_python = sys.executable

            result = subprocess.run(
                [str(venv_python), "-c", script],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(Path(__file__).parent.parent.parent)
            )

            if result.returncode != 0:
                logger.error(f"Instagram subprocess failed: {result.stderr}")
                return ProfileExtractionResult(
                    success=False,
                    error=result.stderr,
                    videos_requested=video_count,
                )

            data = json.loads(result.stdout)

            profile_info = None
            if data.get("profile_info"):
                pi = data["profile_info"]
                profile_info = ProfileInfo(
                    platform=Platform.INSTAGRAM,
                    username=pi["username"],
                    display_name=pi.get("display_name", ""),
                    bio=pi.get("bio", ""),
                    profile_picture_url=pi.get("profile_picture_url"),
                    follower_count=pi.get("follower_count", 0),
                    following_count=pi.get("following_count", 0),
                    post_count=pi.get("post_count", 0),
                    is_verified=pi.get("is_verified", False),
                    is_private=pi.get("is_private", False),
                )

            videos = [VideoInfo(
                platform=Platform.INSTAGRAM,
                video_url=v["video_url"],
                video_id=v["video_id"],
                author_username=v["author_username"],
                thumbnail_url=v.get("thumbnail_url"),
            ) for v in data.get("videos", [])]

            return ProfileExtractionResult(
                success=data["success"],
                profile_info=profile_info,
                videos=videos,
                videos_found=data.get("videos_found", 0),
                videos_requested=data.get("videos_requested", video_count),
                error=data.get("error"),
            )

        except subprocess.TimeoutExpired:
            return ProfileExtractionResult(
                success=False,
                error="Instagram profile extraction timed out",
                videos_requested=video_count,
            )
        except Exception as e:
            logger.error(f"Instagram profile extraction failed: {e}")
            return ProfileExtractionResult(
                success=False,
                error=str(e),
                videos_requested=video_count,
            )

    async def extract_profile(
        self, platform: Platform, username: str, video_count: int = 30
    ) -> ProfileExtractionResult:
        """Extract profile from either platform."""
        if platform == Platform.TIKTOK:
            return await self.extract_tiktok_profile(username, video_count)
        elif platform == Platform.INSTAGRAM:
            return await self.extract_instagram_profile(username, video_count)
        else:
            return ProfileExtractionResult(
                success=False,
                error=f"Unknown platform: {platform}",
                videos_requested=video_count,
            )
