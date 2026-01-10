"""
Quick test script for scrapers.

Run this to test if the scrapers are working:
    python test_scrapers.py

Note: TikTok scraper requires playwright browsers installed:
    playwright install chromium
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.scrapers import TikTokScraper, InstagramScraper


async def test_instagram():
    """Test Instagram scraper with a hospitality hashtag."""
    print("\n=== Testing Instagram Scraper ===")
    print("Target: #bartender (5 posts)")

    scraper = InstagramScraper()

    try:
        result = await scraper.get_hashtag_posts("bartender", count=5)

        print(f"Success: {result.success}")
        print(f"Posts retrieved: {result.posts_retrieved}")

        if result.error:
            print(f"Error: {result.error}")

        for i, post in enumerate(result.posts[:3], 1):
            print(f"\n  Post {i}:")
            print(f"    ID: {post.platform_id}")
            print(f"    Author: @{post.author_username}")
            print(f"    Likes: {post.likes}")
            print(f"    Type: {post.content_type.value}")
            print(f"    Hashtags: {', '.join(post.hashtags[:5])}")

        return result.success

    except Exception as e:
        print(f"Error: {e}")
        return False

    finally:
        await scraper.close()


async def test_tiktok():
    """Test TikTok scraper with a hospitality hashtag."""
    print("\n=== Testing TikTok Scraper ===")
    print("Target: #bartender (5 posts)")
    print("Note: TikTok may require ms_token for reliable access")

    scraper = TikTokScraper()

    try:
        result = await scraper.get_hashtag_posts("bartender", count=5)

        print(f"Success: {result.success}")
        print(f"Posts retrieved: {result.posts_retrieved}")

        if result.error:
            print(f"Error: {result.error}")

        for i, post in enumerate(result.posts[:3], 1):
            print(f"\n  Post {i}:")
            print(f"    ID: {post.platform_id}")
            print(f"    Author: @{post.author_username}")
            print(f"    Views: {post.views}")
            print(f"    Likes: {post.likes}")
            print(f"    Sound: {post.sound_name}")

        return result.success

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await scraper.close()


async def main():
    print("=" * 50)
    print("Social Scraper - Test Suite")
    print("=" * 50)

    # Test Instagram first (usually more reliable without auth)
    ig_success = await test_instagram()

    print("\n" + "-" * 50)

    # Test TikTok
    tt_success = await test_tiktok()

    print("\n" + "=" * 50)
    print("Results:")
    print(f"  Instagram: {'PASS' if ig_success else 'FAIL'}")
    print(f"  TikTok: {'PASS' if tt_success else 'FAIL'}")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
