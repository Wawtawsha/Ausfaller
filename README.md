# Social Scraper (Ausfaller)

Video extraction, download, and AI analysis pipeline for TikTok & Instagram marketing intelligence.

## Live Deployments

| Service | URL | Platform |
|---------|-----|----------|
| **Dashboard + API** | https://ausfaller.up.railway.app | Railway |
| **Database** | Supabase (otmmkmjmbiljredeqhah) | Supabase |

The dashboard and API are served from the same Railway deployment - no separate frontend hosting needed.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           LOCAL SCRAPING                                │
│  [Playwright Stealth] → [yt-dlp] → [Gemini 1.5 Flash] → [Supabase]     │
│       Extract URLs       Download      Analyze             Store        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    RAILWAY (API + Dashboard)                            │
│         [FastAPI] ──── serves ──── [Static Dashboard]                  │
│              │                           │                              │
│              └───── reads from ──────────┘                              │
│                          │                                              │
│                    [Supabase DB]                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

**Workflow:**
1. Run scraping locally (requires Playwright/browser)
2. Data stored in Supabase
3. Railway serves both API endpoints and dashboard from single deployment
4. Dashboard fetches analytics via same-origin API calls

## Quick Start (Local Development)

```bash
# 1. Clone and setup
git clone https://github.com/Wawtawsha/Ausfaller.git
cd Ausfaller

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# 3. Install dependencies
pip install -e .

# 4. Install Playwright browsers
playwright install chromium

# 5. Configure environment
cp .env.example .env
# Edit .env with your keys (see Environment Variables below)

# 6. Run the server
python main.py
```

## Environment Variables

```env
# Gemini API (for video analysis)
GEMINI_API_KEY=your_gemini_api_key

# Supabase (for storage)
SUPABASE_URL=https://otmmkmjmbiljredeqhah.supabase.co
SUPABASE_KEY=your_supabase_anon_key

# Server
HOST=0.0.0.0
PORT=8080
```

## API Endpoints

Visit http://localhost:8080/docs for interactive Swagger docs.

### Scraping Endpoints (Local Only)

#### POST /extract
Extract video URLs from hashtag page.
```json
{
  "platform": "tiktok",
  "hashtag": "bartender",
  "count": 30
}
```

#### POST /download
Download videos from URLs using yt-dlp.
```json
{
  "urls": ["https://tiktok.com/...", "..."],
  "platform": "tiktok"
}
```

#### POST /analyze
Analyze videos with Gemini 1.5 Flash.
```json
{
  "video_paths": ["/path/to/video.mp4", "..."]
}
```

#### POST /pipeline
Run full pipeline (extract → download → analyze → store).
```json
{
  "platform": "tiktok",
  "hashtag": "bartender",
  "count": 10,
  "skip_analysis": false
}
```
Returns `job_id`. Poll `/pipeline/{job_id}` for results.

### Batch Pipeline Endpoints (v0.5.0+)

#### POST /generate-hashtags
Generate relevant hashtags from a niche description using AI.
```json
{
  "niche_description": "cocktail bartending content for TikTok",
  "platform": "tiktok",
  "count": 10
}
```
Response:
```json
{
  "success": true,
  "hashtags": ["cocktail", "mixology", "bartender", "drinktok", "cocktailrecipe", ...],
  "niche_description": "cocktail bartending content for TikTok"
}
```

#### POST /batch-pipeline
Run pipeline on multiple hashtags sequentially with automatic retry.
```json
{
  "platform": "tiktok",
  "niche_query": "cocktail bartending",
  "hashtag_count": 10,
  "videos_per_hashtag": 10,
  "skip_analysis": false,
  "store_to_supabase": true
}
```
Or provide hashtags directly:
```json
{
  "platform": "tiktok",
  "hashtags": ["bartender", "mixology", "cocktails"],
  "videos_per_hashtag": 10
}
```
Returns `batch_id`. Poll `/batch-pipeline/{batch_id}` for progress.

#### GET /batch-pipeline/{batch_id}
Get batch job status with per-hashtag results.
```json
{
  "batch_id": "uuid",
  "status": "processing",
  "hashtags": ["bartender", "mixology"],
  "results": {
    "bartender": {"status": "completed", "videos_found": 10, "videos_downloaded": 8},
    "mixology": {"status": "running", "videos_found": 0}
  },
  "progress": {"total": 2, "completed": 1, "failed": 0, "remaining": 1}
}
```

#### GET /batch-jobs
List all batch jobs.

### Analytics Endpoints (Available on Railway)

#### GET /analytics/summary
Overall statistics.
```json
{
  "total_videos": 35,
  "analyzed_videos": 34,
  "avg_hook_strength": 8.0,
  "avg_viral_potential": 7.0,
  "avg_replicability": 7.0,
  "first_scraped": "2026-01-11T02:34:53.462994+00:00",
  "last_scraped": "2026-01-11T18:36:11.483116+00:00"
}
```

#### GET /analytics/hooks
Hook type and technique breakdown.

#### GET /analytics/audio
Audio/music category trends.

#### GET /analytics/visual
Visual style analysis.

#### GET /analytics/viral
Viral trend patterns.

#### GET /analytics/viral-factors
Top viral success factors.

#### GET /analytics/top-replicable
Leaderboard of most replicable content ideas.

#### GET /analytics/all
Combined endpoint returning all analytics data.

#### GET /health
Health check with service status.

## Database Schema

### Tables

**posts** - Main content storage
```sql
- id: UUID (PK)
- platform: text (tiktok/instagram)
- hashtag: text
- video_url: text
- author_username: text
- author_url: text
- description: text
- video_path: text
- analysis: JSONB (Gemini analysis results)
- scraped_at: timestamp
- analyzed_at: timestamp
```

### Analytics Views (SQL)

Located in `supabase/migrations/002_analytics_views.sql`:

- **analytics_summary** - Aggregate stats
- **hook_trends** - Hook type/technique breakdown
- **audio_trends** - Music/audio categories
- **visual_trends** - Visual style patterns
- **viral_trends** - Viral potential distribution
- **viral_factors_breakdown** - Top success factors
- **replicability_leaderboard** - Most replicable ideas

## Gemini Analysis Schema

Each video analysis includes:

```json
{
  "hook": {
    "hook_type": "question|statement|action|mystery|...",
    "hook_technique": "specific technique used",
    "hook_strength": 1-10,
    "first_3_seconds": "description"
  },
  "audio": {
    "music_type": "trending|original|voiceover|...",
    "audio_role": "how audio supports content",
    "category": "genre/style"
  },
  "visual": {
    "style": "POV|talking_head|montage|...",
    "editing_pace": "fast|medium|slow",
    "text_overlays": true/false,
    "transitions": "types used"
  },
  "trends": {
    "viral_potential_score": 1-10,
    "trend_alignment": "how it fits current trends",
    "uniqueness_factor": "what makes it stand out"
  },
  "replicability": {
    "replicability_score": 1-10,
    "difficulty": "easy|medium|hard",
    "why_it_works": "explanation",
    "replication_steps": ["step1", "step2", "..."],
    "equipment_needed": ["item1", "item2"]
  }
}
```

## Project Structure

```
social-scraper/
├── src/
│   ├── api/
│   │   └── server.py       # FastAPI server (scraping + analytics + batch)
│   ├── extractor/          # Playwright URL extraction
│   ├── downloader/         # yt-dlp video download
│   ├── analyzer/           # Gemini video analysis
│   ├── generator/          # AI hashtag generation (v0.5.0+)
│   │   └── hashtag_generator.py
│   └── storage/
│       └── supabase_client.py  # Database operations + analytics queries
├── dashboard/
│   ├── index.html          # Command Center UI
│   ├── styles.css          # Dark theme styling
│   └── app.js              # Chart.js visualizations
├── supabase/
│   └── migrations/
│       ├── 001_initial_schema.sql
│       └── 002_analytics_views.sql
├── config/
│   └── settings.py         # Environment config
├── railway.toml            # Railway deployment config
├── runtime.txt             # Python version for Railway
├── main.py                 # Entry point
└── test_pipeline.py        # Quick test
```

## Deployment

### Railway (API + Dashboard)
- Auto-deploys from GitHub main branch
- Uses `railway.toml` for configuration
- Environment variables set in Railway dashboard
- FastAPI serves dashboard as static files at root (`/`)
- API endpoints (`/health`, `/analytics/*`, `/docs`) take precedence over static files

### Adding New Data
Run scraping locally - data flows to Supabase automatically:
```bash
# Activate venv and run
python main.py

# Single hashtag
curl -X POST http://localhost:8080/pipeline \
  -H "Content-Type: application/json" \
  -d '{"platform":"tiktok","hashtag":"bartender","count":10}'

# Batch pipeline with AI-generated hashtags (v0.5.0+)
curl -X POST http://localhost:8080/batch-pipeline \
  -H "Content-Type: application/json" \
  -d '{"platform":"tiktok","niche_query":"cocktail bartending","videos_per_hashtag":10}'
```

Dashboard updates automatically since it reads from the same Supabase database.

## Tech Stack

- **Extraction**: Playwright + playwright-stealth
- **Download**: yt-dlp
- **Analysis**: Google Gemini 1.5 Flash
- **Storage**: Supabase (PostgreSQL + JSONB)
- **API**: FastAPI + uvicorn
- **Dashboard**: Vanilla JS + Chart.js
- **Hosting**: Railway (API + static dashboard)

## Data Collected

Hashtags analyzed:
- #bartender
- #barlife

35 videos total, 34 analyzed with full Gemini breakdown.

## Future Enhancements

- [ ] Instagram support (extractor exists, needs testing)
- [ ] Scheduled scraping via n8n
- [ ] More hashtag coverage
- [ ] Export to CSV/reports
- [ ] User authentication for dashboard
