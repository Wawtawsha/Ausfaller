"""Monitor download progress by counting actual files."""
from pathlib import Path

VIDEO_DIR = Path(r'C:\Users\steph\.social-scraper\cache\videos')
TARGET_TOTAL = 12445  # Target from all 3 batches

def display():
    tiktok = len(list(VIDEO_DIR.glob('tiktok_*.mp4')))
    youtube = len(list(VIDEO_DIR.glob('youtube_*.mp4')))
    total = tiktok + youtube

    # Calculate sizes
    tiktok_size = sum(f.stat().st_size for f in VIDEO_DIR.glob('tiktok_*.mp4')) / (1024**3)
    youtube_size = sum(f.stat().st_size for f in VIDEO_DIR.glob('youtube_*.mp4')) / (1024**3)
    total_size = tiktok_size + youtube_size

    pct = (total / TARGET_TOTAL * 100) if TARGET_TOTAL > 0 else 0

    print("=" * 60)
    print("         DOWNLOAD PROGRESS - LIVE")
    print("=" * 60)
    print()
    print("  PLATFORM        VIDEOS       SIZE")
    print("  " + "-" * 44)
    print(f"  TikTok          {tiktok:>6,}      {tiktok_size:>5.1f} GB")
    print(f"  YouTube         {youtube:>6,}      {youtube_size:>5.1f} GB")
    print("  " + "-" * 44)
    print(f"  TOTAL           {total:>6,}      {total_size:>5.1f} GB")
    print()
    print(f"  Target: {TARGET_TOTAL:,} | Progress: {pct:.1f}%")
    print()

    # Progress bar
    bar_len = 40
    filled = int(min(pct, 100) / 100 * bar_len)
    bar = "#" * filled + "-" * (bar_len - filled)
    print(f"  [{bar}]")
    print()
    print("=" * 60)

if __name__ == "__main__":
    display()
