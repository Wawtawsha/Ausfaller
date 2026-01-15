# Ausfaller / Social Scraper - Claude Context

## Project Overview

Social media intelligence pipeline for extracting, analyzing, and visualizing TikTok/Instagram/YouTube content. Originally built for entertainment niches (bartending, nightlife), now extended to support **data engineering content** for the @engdata Substack client.

**GitHub**: `Wawtawsha/Ausfaller`
**Supabase Project**: `otmmkmjmbiljredeqhah` (Shrike Media org)

## Current State (January 2026)

### Data Engineering Niche Extension - COMPLETE

Extended the pipeline to support B2B/educational content analysis for data engineering:

#### New Platform Extractors
- **YouTube Shorts** (`src/extractor/youtube_shorts.py`) - Uses YouTube Data API v3
- **Substack** (`src/extractor/substack.py`) - RSS-based extraction for newsletter publications

#### Educational Analysis Schema
Added to `src/analyzer/gemini.py`:
- `EducationalAnalysis` dataclass - clarity, depth, educational value, teaching technique, tools mentioned
- `DataEngineeringContext` dataclass - cloud platform, data layer, architecture patterns
- `EDUCATIONAL_ANALYSIS_PROMPT` - Gemini prompt optimized for technical/B2B content
- `GeminiAnalyzer` accepts `niche_mode` parameter ("entertainment" or "data_engineering")

#### Database Schema
Migration `008_data_engineering_extension` applied to Supabase:
- `niche_mode` column on posts table
- `content_format` column on posts table
- Views: `educational_metrics`, `tool_coverage`, `content_type_distribution`, `teaching_techniques`, `skill_level_distribution`, `data_engineering_context`

#### API Endpoints Added
```
POST /extract/youtube-shorts     - Search YouTube Shorts by query
POST /extract/substack           - Extract from single Substack publication
POST /extract/substack/multiple  - Extract from multiple publications

GET /analytics/educational       - Educational metrics summary
GET /analytics/tools             - Tool coverage (Fabric, ADF, Power BI, etc.)
GET /analytics/content-types     - Tutorial vs demo vs career advice
GET /analytics/teaching-techniques - Screen share, live coding, etc.
GET /analytics/skill-levels      - Beginner/intermediate/advanced distribution
GET /analytics/data-engineering-context - Cloud platforms, data layers, patterns
```

#### Dashboard
- Niche mode toggle in header (Entertainment / Data Engineering)
- Educational metric cards (Explanation Clarity, Educational Value, Technical Depth)
- Conditional display based on selected niche mode

## Configuration

### Environment Variables (.env)
```bash
GEMINI_API_KEY=...              # Required - video analysis
YOUTUBE_API_KEY=...             # Required for YouTube Shorts extraction
SUPABASE_URL=https://otmmkmjmbiljredeqhah.supabase.co
SUPABASE_KEY=...                # Supabase anon key
NICHE_MODE=data_engineering     # or "entertainment"
HOST=0.0.0.0
PORT=8080
```

### Current .env Status
- GEMINI_API_KEY: Configured
- YOUTUBE_API_KEY: Configured (same key works for both)
- SUPABASE: Configured
- NICHE_MODE: Set to `data_engineering`

## Running the Pipeline

```bash
# Start server
python main.py

# Server runs at http://localhost:8080
# Dashboard at http://localhost:8080/
# API docs at http://localhost:8080/docs
```

### Data Engineering Hashtags to Scrape
TikTok:
- #microsoftfabric, #dataengineering, #powerbi, #azuredatafactory
- #databricks, #dataengineerlife, #techjobs, #learndata

YouTube Shorts queries:
- "microsoft fabric tutorial", "data engineering career"
- "power bi tips", "azure data factory", "medallion architecture"

Substack publications:
- engdata, seabornedata, dataengineeringweekly

## Architecture

```
Niche Query → [Generate Hashtags] → [Extract URLs] → [Download Videos] → [Analyze] → [Store to Supabase] → [Dashboard]
                    ↓                     ↓                ↓                 ↓
               Gemini AI            Playwright/API      yt-dlp         Gemini 2.0 Vision
```

## Key Files

| File | Purpose |
|------|---------|
| `src/api/server.py` | FastAPI server with all endpoints |
| `src/extractor/hashtag.py` | TikTok/Instagram Playwright extraction |
| `src/extractor/youtube_shorts.py` | YouTube Data API v3 integration |
| `src/extractor/substack.py` | RSS-based Substack extraction |
| `src/analyzer/gemini.py` | Video analysis with entertainment + educational prompts |
| `src/storage/supabase_client.py` | Database operations |
| `config/settings.py` | Environment configuration |
| `dashboard/` | Vanilla JS + Chart.js analytics dashboard |

## Platform Enum
```python
class Platform(str, Enum):
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"
    YOUTUBE_SHORTS = "youtube_shorts"
    SUBSTACK = "substack"
```

## Notes for Future Claude Instances

1. **This is NOT the Durandal MCP project** - this is Ausfaller/social-scraper
2. The database is shared between entertainment and data_engineering niches - filtered by `niche_mode` column
3. YouTube API has 10,000 units/day free tier - sufficient for normal use
4. Substack extraction is RSS-based, no API key needed
5. Dashboard toggle switches between entertainment metrics (hooks, viral potential) and educational metrics (clarity, depth, value)
6. The `dadausfaller` directory was a temporary clone - use `social-scraper` as the working directory
7. **NEVER analyze video content yourself** - Always send videos to Gemini API for analysis. Use `src/analyzer/gemini.py` and the `GeminiAnalyzer` class. Claude should orchestrate/script the analysis, not perform it directly.
8. **Dashboard is deployed on Vercel+Railway** - No local server needed to view the dashboard. Data goes to Supabase, frontend is hosted.

## Recent Changes (January 13, 2026)

- Commit `f628b61`: Added data engineering niche support
- Migration 008 applied to Supabase
- YouTube and Substack extractors created
- Educational analysis schema implemented
- Dashboard updated with niche toggle
- .env configured with YouTube API key and NICHE_MODE=data_engineering
