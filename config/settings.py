from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Supabase
    supabase_url: str = ""
    supabase_key: str = ""

    # Scraping
    scrape_delay_min: float = 5.0  # Min seconds between requests
    scrape_delay_max: float = 15.0  # Max seconds between requests
    max_posts_per_session: int = 50  # Limit to avoid detection

    # Instagram (optional, for authenticated scraping)
    instagram_username: Optional[str] = None
    instagram_password: Optional[str] = None

    # TikTok
    tiktok_ms_token: Optional[str] = None  # For TikTokApi authentication

    # Server
    host: str = "0.0.0.0"
    port: int = 8080

    # Paths
    session_dir: str = os.path.expanduser("~/.social-scraper/sessions")
    cache_dir: str = os.path.expanduser("~/.social-scraper/cache")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Ensure directories exist
os.makedirs(settings.session_dir, exist_ok=True)
os.makedirs(settings.cache_dir, exist_ok=True)
