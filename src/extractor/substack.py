"""
Substack extractor using RSS feeds.

Extracts posts and embedded videos from Substack publications.
"""

import asyncio
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from xml.etree import ElementTree
import httpx
from html.parser import HTMLParser

from src.extractor.hashtag import Platform, VideoInfo, ExtractionResult

logger = logging.getLogger(__name__)


@dataclass
class SubstackPost:
    """Extracted Substack post information."""
    title: str
    url: str
    author: str
    publication: str
    published_at: Optional[datetime] = None
    description: str = ""
    content_html: str = ""
    embedded_videos: list[str] = field(default_factory=list)


class VideoEmbedParser(HTMLParser):
    """Parse HTML content to extract video embed URLs."""

    def __init__(self):
        super().__init__()
        self.video_urls = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # YouTube embeds
        if tag == "iframe":
            src = attrs_dict.get("src", "")
            if "youtube.com" in src or "youtu.be" in src:
                video_id = self._extract_youtube_id(src)
                if video_id:
                    self.video_urls.append(f"https://www.youtube.com/watch?v={video_id}")

        # Loom embeds
        if tag == "iframe":
            src = attrs_dict.get("src", "")
            if "loom.com" in src:
                self.video_urls.append(src)

        # Vimeo embeds
        if tag == "iframe":
            src = attrs_dict.get("src", "")
            if "vimeo.com" in src:
                self.video_urls.append(src)

        # Direct video links
        if tag == "a":
            href = attrs_dict.get("href", "")
            if any(domain in href for domain in ["youtube.com", "youtu.be", "loom.com", "vimeo.com"]):
                self.video_urls.append(href)

    def _extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from various URL formats."""
        patterns = [
            r'youtube\.com/embed/([a-zA-Z0-9_-]+)',
            r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)',
            r'youtu\.be/([a-zA-Z0-9_-]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None


class SubstackExtractor:
    """Extract posts and videos from Substack publications via RSS."""

    def __init__(self):
        pass

    async def extract_publication(
        self,
        publication_name: str,
        count: int = 30
    ) -> tuple[list[SubstackPost], ExtractionResult]:
        """
        Extract posts from a Substack publication.

        Args:
            publication_name: The subdomain of the publication (e.g., "engdata" for engdata.substack.com)
            count: Maximum number of posts to retrieve

        Returns:
            Tuple of (list of SubstackPost objects, ExtractionResult with video embeds)
        """
        rss_url = f"https://{publication_name}.substack.com/feed"

        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(rss_url)
                response.raise_for_status()

                # Parse RSS XML
                root = ElementTree.fromstring(response.content)
                channel = root.find("channel")

                if channel is None:
                    return [], ExtractionResult(
                        success=False,
                        error="Invalid RSS feed structure",
                        videos_requested=count,
                    )

                pub_title = channel.findtext("title", publication_name)
                posts = []
                all_videos = []

                for item in channel.findall("item")[:count]:
                    title = item.findtext("title", "")
                    link = item.findtext("link", "")
                    description = item.findtext("description", "")

                    # Get full content if available (content:encoded)
                    content_html = ""
                    for elem in item:
                        if elem.tag.endswith("encoded"):
                            content_html = elem.text or ""
                            break

                    # Parse publish date
                    pub_date_str = item.findtext("pubDate", "")
                    published_at = None
                    if pub_date_str:
                        try:
                            from email.utils import parsedate_to_datetime
                            published_at = parsedate_to_datetime(pub_date_str)
                        except Exception:
                            pass

                    # Extract embedded videos
                    parser = VideoEmbedParser()
                    parser.feed(content_html or description)
                    embedded_videos = list(set(parser.video_urls))

                    # Get author from dc:creator if available
                    author = publication_name
                    for elem in item:
                        if elem.tag.endswith("creator"):
                            author = elem.text or publication_name
                            break

                    post = SubstackPost(
                        title=title,
                        url=link,
                        author=author,
                        publication=pub_title,
                        published_at=published_at,
                        description=description[:500] if description else "",
                        content_html=content_html,
                        embedded_videos=embedded_videos,
                    )
                    posts.append(post)

                    # Convert embedded videos to VideoInfo
                    for video_url in embedded_videos:
                        video_id = self._generate_video_id(video_url)
                        video_info = VideoInfo(
                            platform=Platform.SUBSTACK,
                            video_url=video_url,
                            video_id=video_id,
                            author_username=author,
                            caption=f"{title} (from {pub_title})",
                            extracted_at=datetime.utcnow(),
                        )
                        all_videos.append(video_info)

                return posts, ExtractionResult(
                    success=True,
                    videos=all_videos,
                    videos_requested=count,
                    videos_found=len(all_videos),
                )

        except httpx.HTTPStatusError as e:
            logger.error(f"Substack RSS error: {e.response.status_code}")
            return [], ExtractionResult(
                success=False,
                error=f"RSS fetch failed: {e.response.status_code}",
                videos_requested=count,
            )
        except Exception as e:
            logger.error(f"Substack extraction failed: {e}")
            return [], ExtractionResult(
                success=False,
                error=str(e),
                videos_requested=count,
            )

    async def extract_multiple_publications(
        self,
        publication_names: list[str],
        count_per_publication: int = 10
    ) -> ExtractionResult:
        """
        Extract from multiple Substack publications.

        Args:
            publication_names: List of publication subdomains
            count_per_publication: Posts per publication

        Returns:
            Combined ExtractionResult with all videos
        """
        all_videos = []
        errors = []

        for pub_name in publication_names:
            posts, result = await self.extract_publication(pub_name, count_per_publication)
            if result.success:
                all_videos.extend(result.videos)
            else:
                errors.append(f"{pub_name}: {result.error}")

        return ExtractionResult(
            success=len(all_videos) > 0,
            videos=all_videos,
            videos_requested=len(publication_names) * count_per_publication,
            videos_found=len(all_videos),
            error="; ".join(errors) if errors else None,
        )

    def _generate_video_id(self, url: str) -> str:
        """Generate a unique ID for a video URL."""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()[:16]
