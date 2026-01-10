"""
Quick test script for the pipeline.

Tests:
1. URL extraction from hashtag page
2. Video download with yt-dlp
3. Video analysis with Gemini (if configured)

Usage:
    python test_pipeline.py
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.extractor import HashtagExtractor, Platform
from src.downloader import VideoDownloader
from config.settings import settings


async def test_extraction():
    """Test URL extraction from TikTok hashtag page."""
    print("\n" + "=" * 50)
    print("TEST 1: URL Extraction")
    print("=" * 50)
    print("Target: TikTok #bartender (3 videos)")

    extractor = HashtagExtractor()

    try:
        result = await extractor.extract_tiktok_hashtag("bartender", count=3)

        print(f"Success: {result.success}")
        print(f"Videos found: {result.videos_found}")

        if result.error:
            print(f"Error: {result.error}")

        for i, video in enumerate(result.videos[:3], 1):
            print(f"\n  Video {i}:")
            print(f"    URL: {video.video_url[:60]}...")
            print(f"    Author: @{video.author_username}")
            print(f"    Likes: {video.likes}")

        return result.videos[:2] if result.videos else []

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []

    finally:
        await extractor.close()


async def test_download(videos):
    """Test video download with yt-dlp."""
    print("\n" + "=" * 50)
    print("TEST 2: Video Download")
    print("=" * 50)

    if not videos:
        print("Skipping: No videos to download")
        return []

    print(f"Downloading {len(videos)} video(s)...")

    downloader = VideoDownloader()
    downloaded = []

    for i, video in enumerate(videos):
        print(f"\n  Downloading {i+1}/{len(videos)}: {video.video_url[:50]}...")

        result = await downloader.download(
            url=video.video_url,
            video_id=video.video_id,
            platform="tiktok",
        )

        if result.success:
            print(f"    Success: {result.file_path}")
            print(f"    Size: {result.file_size_bytes / 1024:.1f} KB")
            downloaded.append(result)
        else:
            print(f"    Failed: {result.error}")

    return downloaded


async def test_analysis(downloads):
    """Test video analysis with Gemini."""
    print("\n" + "=" * 50)
    print("TEST 3: Video Analysis (Gemini)")
    print("=" * 50)

    if not settings.gemini_api_key:
        print("Skipping: GEMINI_API_KEY not configured")
        return

    if not downloads:
        print("Skipping: No videos to analyze")
        return

    from src.analyzer import GeminiAnalyzer

    print(f"Analyzing {len(downloads)} video(s)...")

    try:
        analyzer = GeminiAnalyzer()

        for i, download in enumerate(downloads):
            print(f"\n  Analyzing {i+1}/{len(downloads)}: {download.file_path.name}...")

            result = await analyzer.analyze_video(download.file_path)

            if result.success:
                print(f"    Description: {result.description[:100]}...")
                print(f"    Tone: {result.tone}")
                print(f"    Hook: {result.hook[:80]}..." if result.hook else "    Hook: N/A")
                print(f"    Replicability: {result.replicability_score}/10")
            else:
                print(f"    Failed: {result.error}")

    except Exception as e:
        print(f"Error: {e}")


async def main():
    print("=" * 50)
    print("Social Scraper - Pipeline Test")
    print("=" * 50)

    # Test 1: Extraction
    videos = await test_extraction()

    # Test 2: Download
    downloads = await test_download(videos)

    # Test 3: Analysis
    await test_analysis(downloads)

    print("\n" + "=" * 50)
    print("Test complete!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
