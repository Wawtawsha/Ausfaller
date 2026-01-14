"""
Video downloader using yt-dlp.

Downloads videos from TikTok, Instagram, and other platforms.
"""

import asyncio
import subprocess
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from datetime import datetime
import logging
import shutil

from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class DownloadResult:
    """Result from a download operation."""
    success: bool
    video_url: str
    file_path: Optional[Path] = None
    file_size_bytes: int = 0
    duration_seconds: float = 0.0
    title: Optional[str] = None
    author: Optional[str] = None
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "video_url": self.video_url,
            "file_path": str(self.file_path) if self.file_path else None,
            "file_size_bytes": self.file_size_bytes,
            "duration_seconds": self.duration_seconds,
            "title": self.title,
            "author": self.author,
            "error": self.error,
        }


class VideoDownloader:
    """Download videos using yt-dlp."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or Path(settings.cache_dir) / "videos"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Find yt-dlp - check venv first, then system
        self.ytdlp_path = self._find_ytdlp()
        if not self.ytdlp_path:
            raise RuntimeError("yt-dlp is not installed. Run: pip install yt-dlp")

    def _find_ytdlp(self) -> Optional[str]:
        """Find yt-dlp executable."""
        import sys

        # Check in same directory as python (venv)
        venv_ytdlp = Path(sys.executable).parent / "yt-dlp.exe"
        if venv_ytdlp.exists():
            return str(venv_ytdlp)

        # Check in PATH
        system_ytdlp = shutil.which("yt-dlp")
        if system_ytdlp:
            return system_ytdlp

        return None

    def _generate_filename(self, video_id: str, platform: str) -> str:
        """Generate unique filename for downloaded video."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"{platform}_{video_id}_{timestamp}"

    async def download(
        self,
        url: str,
        video_id: str = "",
        platform: str = "unknown",
        max_duration: int = 300,  # 5 minutes max
    ) -> DownloadResult:
        """
        Download a video from URL.

        Args:
            url: Video URL to download
            video_id: Optional ID for filename
            platform: Platform name for filename
            max_duration: Maximum video duration in seconds

        Returns:
            DownloadResult with file path and metadata
        """
        if not video_id:
            video_id = str(hash(url))[-8:]

        filename = self._generate_filename(video_id, platform)
        output_template = str(self.output_dir / f"{filename}.%(ext)s")

        # yt-dlp command
        cmd = [
            self.ytdlp_path,
            "--no-progress",
            "--js-runtimes", "node",  # Use Node.js for YouTube extraction
            "--remote-components", "ejs:github",  # Download EJS component for YouTube
            "-f", "best[ext=mp4]/best",  # Prefer mp4
            "--max-filesize", "100M",  # Max 100MB
            "--write-info-json",  # Save metadata
            "-o", output_template,
            url,
        ]

        try:
            logger.info(f"Downloading: {url}")

            # Run yt-dlp
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=120,  # 2 minute timeout
            )

            logger.debug(f"yt-dlp returncode: {process.returncode}")
            logger.debug(f"yt-dlp stdout: {stdout[:200] if stdout else 'None'}")
            logger.debug(f"yt-dlp stderr: {stderr[:200] if stderr else 'None'}")

            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else ""
                stdout_msg = stdout.decode() if stdout else ""
                full_error = error_msg or stdout_msg or f"yt-dlp exited with code {process.returncode}"
                logger.error(f"Download failed (code {process.returncode}): {full_error}")
                return DownloadResult(
                    success=False,
                    video_url=url,
                    error=full_error,
                )

            # Find the downloaded file
            video_file = None
            json_file = None

            for f in self.output_dir.glob(f"{filename}.*"):
                if f.suffix == ".json":
                    json_file = f
                elif f.suffix in [".mp4", ".webm", ".mkv", ".mov"]:
                    video_file = f

            if not video_file:
                return DownloadResult(
                    success=False,
                    video_url=url,
                    error="Video file not found after download",
                )

            # Read metadata
            metadata = {}
            title = None
            author = None
            duration = 0.0

            if json_file and json_file.exists():
                try:
                    metadata = json.loads(json_file.read_text())
                    title = metadata.get("title")
                    author = metadata.get("uploader") or metadata.get("channel")
                    duration = float(metadata.get("duration", 0))
                except Exception as e:
                    logger.warning(f"Failed to read metadata: {e}")

            file_size = video_file.stat().st_size

            logger.info(f"Downloaded: {video_file.name} ({file_size / 1024 / 1024:.1f}MB)")

            return DownloadResult(
                success=True,
                video_url=url,
                file_path=video_file,
                file_size_bytes=file_size,
                duration_seconds=duration,
                title=title,
                author=author,
                metadata=metadata,
            )

        except asyncio.TimeoutError:
            return DownloadResult(
                success=False,
                video_url=url,
                error="Download timed out",
            )
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return DownloadResult(
                success=False,
                video_url=url,
                error=str(e),
            )

    async def download_batch(
        self,
        urls: list[str],
        platform: str = "unknown",
        max_concurrent: int = 3,
    ) -> list[DownloadResult]:
        """
        Download multiple videos concurrently.

        Args:
            urls: List of video URLs
            platform: Platform name
            max_concurrent: Max concurrent downloads

        Returns:
            List of DownloadResults
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def download_with_semaphore(url: str, idx: int) -> DownloadResult:
            async with semaphore:
                return await self.download(
                    url=url,
                    video_id=str(idx),
                    platform=platform,
                )

        tasks = [
            download_with_semaphore(url, idx)
            for idx, url in enumerate(urls)
        ]

        return await asyncio.gather(*tasks)

    def cleanup_old_videos(self, max_age_hours: int = 24) -> int:
        """
        Delete videos older than max_age_hours.

        Returns number of files deleted.
        """
        deleted = 0
        now = datetime.utcnow()

        for f in self.output_dir.glob("*"):
            if f.is_file():
                age = now - datetime.fromtimestamp(f.stat().st_mtime)
                if age.total_seconds() > max_age_hours * 3600:
                    f.unlink()
                    deleted += 1
                    logger.debug(f"Deleted old file: {f.name}")

        if deleted:
            logger.info(f"Cleaned up {deleted} old video files")

        return deleted

    def get_storage_usage(self) -> dict:
        """Get storage usage stats."""
        total_size = 0
        file_count = 0

        for f in self.output_dir.glob("*"):
            if f.is_file() and f.suffix != ".json":
                total_size += f.stat().st_size
                file_count += 1

        return {
            "file_count": file_count,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / 1024 / 1024,
            "output_dir": str(self.output_dir),
        }
