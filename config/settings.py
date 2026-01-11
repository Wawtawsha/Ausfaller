from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
import os


class Settings(BaseSettings):
    # Gemini API
    gemini_api_key: str = ""

    # Supabase (for future use)
    supabase_url: str = ""
    supabase_key: str = ""

    # Scraping behavior
    scrape_delay_min: float = 3.0  # Min seconds between requests
    scrape_delay_max: float = 8.0  # Max seconds between requests
    max_videos_per_session: int = 50  # Limit to avoid detection

    # Download settings
    max_video_duration: int = 300  # 5 minutes max
    max_video_size_mb: int = 100  # 100MB max
    max_concurrent_downloads: int = 3

    # Analysis settings
    max_concurrent_analyses: int = 2  # Gemini rate limits
    gemini_model: str = "gemini-2.0-flash-lite"  # Can also try: gemini-2.0-flash, gemini-2.5-flash

    # Batch processing settings
    batch_delay_between_hashtags: int = 30  # Seconds between processing hashtags
    batch_max_hashtags: int = 50  # Maximum hashtags per batch
    batch_retry_delay: int = 60  # Extra delay before retry pass
    batch_max_retries: int = 1  # Number of retry passes for failed hashtags

    # Server
    host: str = "0.0.0.0"
    port: int = 8080

    # Paths
    base_dir: Path = Path.home() / ".social-scraper"

    @property
    def session_dir(self) -> Path:
        path = self.base_dir / "sessions"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def cache_dir(self) -> Path:
        path = self.base_dir / "cache"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def videos_dir(self) -> Path:
        path = self.base_dir / "videos"
        path.mkdir(parents=True, exist_ok=True)
        return path

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
