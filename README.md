# Social Scraper (Ausfaller)

Video extraction, download, and analysis pipeline for TikTok & Instagram.

## Architecture

```
[Playwright Stealth] → [yt-dlp] → [Gemini 1.5 Flash] → [Supabase]
     Extract URLs       Download      Analyze            Store
```

**Designed for n8n orchestration** - each step is a separate API endpoint.

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 2. Install dependencies
pip install -e .

# 3. Install Playwright browsers
playwright install chromium

# 4. Configure environment
cp .env.example .env
# Edit .env - add your GEMINI_API_KEY

# 5. Run the server
python main.py
```

## API Endpoints

Visit http://localhost:8080/docs for interactive API docs.

### POST /extract
Extract video URLs from hashtag page.

```json
{
  "platform": "tiktok",
  "hashtag": "bartender",
  "count": 30
}
```

### POST /download
Download videos from URLs using yt-dlp.

```json
{
  "urls": ["https://tiktok.com/...", "..."],
  "platform": "tiktok"
}
```

### POST /analyze
Analyze videos with Gemini 1.5 Flash.

```json
{
  "video_paths": ["/path/to/video.mp4", "..."]
}
```

### POST /pipeline
Run full pipeline (extract → download → analyze).

```json
{
  "platform": "tiktok",
  "hashtag": "bartender",
  "count": 10,
  "skip_analysis": false
}
```

Returns `job_id`. Poll `/pipeline/{job_id}` for results.

### GET /health
Health check with storage stats.

## n8n Integration

Call endpoints from n8n using HTTP Request nodes:

**Workflow 1: Scheduled Scrape**
```
[Schedule Trigger: Every 6 hours]
  → [HTTP POST /pipeline]
  → [Wait/Poll for completion]
  → [Supabase: Store results]
  → [Slack: Notify]
```

**Workflow 2: On-Demand Analysis**
```
[Webhook: Client query]
  → [HTTP POST /extract]
  → [HTTP POST /download]
  → [HTTP POST /analyze]
  → [Return results]
```

## Testing

```bash
# Quick pipeline test
python test_pipeline.py

# Test extraction only (no Gemini needed)
python -c "
import asyncio
from src.extractor import HashtagExtractor, Platform

async def test():
    e = HashtagExtractor()
    r = await e.extract_tiktok_hashtag('bartender', 3)
    print(f'Found {r.videos_found} videos')
    for v in r.videos:
        print(f'  {v.video_url}')
    await e.close()

asyncio.run(test())
"
```

## Requirements

- Python 3.10+
- Playwright + Chromium
- yt-dlp
- Gemini API key (for analysis)

## Project Structure

```
social-scraper/
├── src/
│   ├── extractor/      # Playwright URL extraction
│   ├── downloader/     # yt-dlp video download
│   ├── analyzer/       # Gemini video analysis
│   └── api/            # FastAPI server
├── config/
│   └── settings.py     # Environment config
├── main.py             # Entry point
└── test_pipeline.py    # Quick test
```
