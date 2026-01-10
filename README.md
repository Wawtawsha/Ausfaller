# Social Scraper

TikTok & Instagram scraping service for social media content analysis.

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 2. Install dependencies
pip install -e .

# 3. Install Playwright browsers (required for TikTok)
playwright install chromium

# 4. Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Run the server
python main.py
```

## API Endpoints

Once running, visit http://localhost:8080/docs for interactive API docs.

### POST /scrape
Queue a scrape job.

```json
{
  "platform": "instagram",
  "target_type": "hashtag",
  "target": "bartender",
  "count": 30
}
```

### GET /scrape/{job_id}
Get job status and results.

### GET /health
Health check with rate limit stats.

## Testing

```bash
# Quick test of scrapers
python test_scrapers.py
```

## n8n Integration

Call the API from n8n using HTTP Request node:

1. **POST** to `http://localhost:8080/scrape` to start job
2. **GET** `http://localhost:8080/scrape/{job_id}` to poll for results
3. Parse the `posts` array from the response

## Notes

- TikTok scraping requires `ms_token` from browser cookies for reliable access
- Instagram public data works without auth; explore/reels need login
- Scraping is slow by design (5-15s delays) to avoid detection
- Default limit: 50 posts per session
