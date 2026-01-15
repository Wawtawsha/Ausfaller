"""Quick script to parse collection progress from server logs."""
import re
import sys

LOG_FILE = r'C:\Users\steph\AppData\Local\Temp\claude\C--Users-steph-OneDrive-Desktop-claude-social-scraper\tasks\b577bbc.output'

try:
    content = open(LOG_FILE, encoding='utf-8', errors='ignore').read()
except FileNotFoundError:
    print("Log file not found")
    sys.exit(1)

# Parse metrics
yt = re.findall(r'Found (\d+) shorts for', content)
tt = re.findall(r'Found (\d+) TikToks for', content)
failed_tt = len(re.findall(r'TikTok extraction failed', content))
failed_yt = len(re.findall(r'YouTube search failed', content))

yt_total = sum(int(x) for x in yt)
tt_total = sum(int(x) for x in tt)

total_queries = 40  # TikTok only batch
completed = len(yt) + len(tt) + failed_tt + failed_yt
pct = completed / total_queries * 100

print("=" * 60)
print("        10K BATCH COLLECTION - LIVE METRICS")
print("=" * 60)
print()
print("  PLATFORM           QUERIES     VIDEOS      AVG/QUERY")
print("  " + "-" * 54)
print(f"  YouTube Shorts     {len(yt):>3}/60     {yt_total:>7,}       {yt_total // max(1, len(yt)):>3}")
print(f"  TikTok             {len(tt):>3}/35     {tt_total:>7,}       {tt_total // max(1, len(tt)):>3}")
print("  " + "-" * 54)
print(f"  TOTAL              {completed:>3}/95     {yt_total + tt_total:>7,}")
print()

# Progress bar
bar_len = 30
filled = int(pct / 100 * bar_len)
bar = "#" * filled + "-" * (bar_len - filled)
print(f"  Progress: [{bar}] {pct:.0f}%")
print()

if failed_tt or failed_yt:
    print(f"  (!) {failed_tt + failed_yt} query/hashtag(s) timed out")

# Check if complete
if "Collection saved" in content or "Saved collection" in content:
    print()
    print("  STATUS: COLLECTION COMPLETE!")
elif "starting batch" in content.lower() or pct >= 100:
    print()
    print("  STATUS: Collection finishing up...")
else:
    print()
    print("  STATUS: Collection in progress...")

print("=" * 60)
