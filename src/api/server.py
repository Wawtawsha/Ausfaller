"""
FastAPI server for social media scraping pipeline.

Endpoints:
- POST /extract - Extract video URLs from hashtag pages
- POST /download - Download videos from URLs
- POST /analyze - Analyze videos with Gemini
- POST /pipeline - Run full pipeline (extract → download → analyze)
- GET /health - Health check
- GET /analytics/* - Analytics dashboard endpoints
"""

import asyncio
import sys
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
from pathlib import Path
import logging

# Fix Windows asyncio compatibility with Playwright
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.extractor import HashtagExtractor, Platform, ExtractionResult, VideoInfo
from src.downloader import VideoDownloader, DownloadResult
from src.analyzer import GeminiAnalyzer, VideoAnalysis
from src.storage import SupabaseStorage
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Social Scraper API",
    description="Extract, download, and analyze social media videos",
    version="0.4.0",
)

# Enable CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (including file://)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (lazy initialized)
_extractor: Optional[HashtagExtractor] = None
_downloader: Optional[VideoDownloader] = None
_analyzer: Optional[GeminiAnalyzer] = None
_storage: Optional[SupabaseStorage] = None

# Job storage
jobs: dict[str, dict] = {}


class JobStatus(str, Enum):
    QUEUED = "queued"
    EXTRACTING = "extracting"
    DOWNLOADING = "downloading"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


# Request/Response Models

class ExtractRequest(BaseModel):
    platform: Platform
    hashtag: str = Field(..., description="Hashtag to extract (without #)")
    count: int = Field(default=30, ge=1, le=100)


class DownloadRequest(BaseModel):
    urls: list[str] = Field(..., description="List of video URLs to download")
    platform: str = Field(default="unknown")


class AnalyzeRequest(BaseModel):
    video_paths: list[str] = Field(..., description="List of video file paths")


class PipelineRequest(BaseModel):
    platform: Platform
    hashtag: str
    count: int = Field(default=30, ge=1, le=50)
    skip_analysis: bool = Field(default=False, description="Skip Gemini analysis")
    store_to_supabase: bool = Field(default=False, description="Store results in Supabase")


class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str


class ExtractResponse(BaseModel):
    success: bool
    videos_found: int
    videos: list[dict]
    error: Optional[str] = None


class DownloadResponse(BaseModel):
    success: bool
    downloaded: int
    failed: int
    results: list[dict]


class AnalyzeResponse(BaseModel):
    success: bool
    analyzed: int
    results: list[dict]


class PipelineResult(BaseModel):
    job_id: str
    status: JobStatus
    extraction: Optional[dict] = None
    downloads: Optional[list[dict]] = None
    analyses: Optional[list[dict]] = None
    error: Optional[str] = None


# Helper functions

def get_extractor() -> HashtagExtractor:
    global _extractor
    if _extractor is None:
        _extractor = HashtagExtractor()
    return _extractor


def get_downloader() -> VideoDownloader:
    global _downloader
    if _downloader is None:
        _downloader = VideoDownloader(output_dir=settings.videos_dir)
    return _downloader


def get_analyzer() -> GeminiAnalyzer:
    global _analyzer
    if _analyzer is None:
        if not settings.gemini_api_key:
            raise HTTPException(
                status_code=500,
                detail="Gemini API key not configured"
            )
        _analyzer = GeminiAnalyzer(api_key=settings.gemini_api_key)
    return _analyzer


def get_storage() -> Optional[SupabaseStorage]:
    """Get Supabase storage client (returns None if not configured)."""
    global _storage
    if _storage is None and settings.supabase_url and settings.supabase_key:
        try:
            _storage = SupabaseStorage(
                url=settings.supabase_url,
                key=settings.supabase_key
            )
            logger.info("Supabase storage initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Supabase: {e}")
            return None
    return _storage


# Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    downloader = get_downloader()
    disk_storage = downloader.get_storage_usage()

    return {
        "status": "healthy",
        "version": "0.4.0",
        "gemini_configured": bool(settings.gemini_api_key),
        "supabase_configured": bool(settings.supabase_url and settings.supabase_key),
        "storage": disk_storage,
        "active_jobs": len([j for j in jobs.values() if j["status"] not in [JobStatus.COMPLETED, JobStatus.FAILED]]),
    }


@app.post("/extract", response_model=ExtractResponse)
async def extract_videos(request: ExtractRequest):
    """
    Extract video URLs from a hashtag page.

    Returns list of video URLs and metadata.
    """
    extractor = get_extractor()

    result = await extractor.extract_hashtag(
        platform=request.platform,
        hashtag=request.hashtag,
        count=request.count,
    )

    return ExtractResponse(
        success=result.success,
        videos_found=result.videos_found,
        videos=[v.to_dict() for v in result.videos],
        error=result.error,
    )


@app.post("/download", response_model=DownloadResponse)
async def download_videos(request: DownloadRequest):
    """
    Download videos from URLs using yt-dlp.

    Returns list of download results with file paths.
    """
    downloader = get_downloader()

    results = await downloader.download_batch(
        urls=request.urls,
        platform=request.platform,
        max_concurrent=settings.max_concurrent_downloads,
    )

    successful = [r for r in results if r.success]
    failed = [r for r in results if not r.success]

    return DownloadResponse(
        success=len(successful) > 0,
        downloaded=len(successful),
        failed=len(failed),
        results=[r.to_dict() for r in results],
    )


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_videos(request: AnalyzeRequest):
    """
    Analyze videos with Gemini.

    Returns list of analysis results.
    """
    analyzer = get_analyzer()

    paths = [Path(p) for p in request.video_paths]
    results = await analyzer.analyze_batch(
        video_paths=paths,
        max_concurrent=settings.max_concurrent_analyses,
    )

    successful = [r for r in results if r.success]

    return AnalyzeResponse(
        success=len(successful) > 0,
        analyzed=len(successful),
        results=[r.to_dict() for r in results],
    )


@app.post("/pipeline", response_model=JobResponse)
async def run_pipeline(
    request: PipelineRequest,
    background_tasks: BackgroundTasks,
):
    """
    Run full pipeline: extract → download → analyze.

    Returns job_id. Poll /pipeline/{job_id} for results.
    """
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "job_id": job_id,
        "status": JobStatus.QUEUED,
        "request": request.model_dump(),
        "extraction": None,
        "downloads": None,
        "analyses": None,
        "error": None,
        "started_at": None,
        "completed_at": None,
    }

    background_tasks.add_task(run_pipeline_job, job_id, request)

    return JobResponse(
        job_id=job_id,
        status=JobStatus.QUEUED,
        message=f"Pipeline queued for #{request.hashtag} on {request.platform.value}",
    )


async def run_pipeline_job(job_id: str, request: PipelineRequest) -> None:
    """Background task to run full pipeline."""
    jobs[job_id]["started_at"] = datetime.utcnow().isoformat()

    try:
        # Step 1: Extract
        jobs[job_id]["status"] = JobStatus.EXTRACTING
        logger.info(f"[{job_id}] Extracting #{request.hashtag}")

        extractor = get_extractor()
        extraction = await extractor.extract_hashtag(
            platform=request.platform,
            hashtag=request.hashtag,
            count=request.count,
        )

        jobs[job_id]["extraction"] = {
            "success": extraction.success,
            "videos_found": extraction.videos_found,
            "videos": [v.to_dict() for v in extraction.videos],
            "error": extraction.error,
        }

        if not extraction.success or not extraction.videos:
            raise Exception(f"Extraction failed: {extraction.error or 'No videos found'}")

        # Step 2: Download
        jobs[job_id]["status"] = JobStatus.DOWNLOADING
        logger.info(f"[{job_id}] Downloading {len(extraction.videos)} videos")

        downloader = get_downloader()
        urls = [v.video_url for v in extraction.videos]

        downloads = await downloader.download_batch(
            urls=urls,
            platform=request.platform.value,
            max_concurrent=settings.max_concurrent_downloads,
        )

        jobs[job_id]["downloads"] = [d.to_dict() for d in downloads]

        successful_downloads = [d for d in downloads if d.success and d.file_path]

        if not successful_downloads:
            raise Exception("No videos downloaded successfully")

        # Step 3: Analyze (optional)
        if not request.skip_analysis:
            jobs[job_id]["status"] = JobStatus.ANALYZING
            logger.info(f"[{job_id}] Analyzing {len(successful_downloads)} videos")

            analyzer = get_analyzer()
            paths = [d.file_path for d in successful_downloads]

            analyses = await analyzer.analyze_batch(
                video_paths=paths,
                max_concurrent=settings.max_concurrent_analyses,
            )

            jobs[job_id]["analyses"] = [a.to_dict() for a in analyses]

        # Step 4: Store to Supabase (optional)
        if request.store_to_supabase:
            storage = get_storage()
            if storage:
                logger.info(f"[{job_id}] Storing to Supabase")
                analyses_list = analyses if not request.skip_analysis else None
                stored = storage.store_batch(
                    videos=extraction.videos,
                    downloads=downloads,
                    analyses=analyses_list,
                )
                logger.info(f"[{job_id}] Stored {stored} posts to Supabase")
            else:
                logger.warning(f"[{job_id}] Supabase not configured, skipping storage")

        jobs[job_id]["status"] = JobStatus.COMPLETED
        logger.info(f"[{job_id}] Pipeline completed")

    except Exception as e:
        logger.error(f"[{job_id}] Pipeline failed: {e}")
        jobs[job_id]["status"] = JobStatus.FAILED
        jobs[job_id]["error"] = str(e)

    finally:
        jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()


@app.get("/pipeline/{job_id}", response_model=PipelineResult)
async def get_pipeline_status(job_id: str):
    """Get pipeline job status and results."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs[job_id]

    return PipelineResult(
        job_id=job["job_id"],
        status=job["status"],
        extraction=job["extraction"],
        downloads=job["downloads"],
        analyses=job["analyses"],
        error=job["error"],
    )


@app.get("/jobs")
async def list_jobs():
    """List all jobs."""
    return {
        "count": len(jobs),
        "jobs": [
            {
                "job_id": j["job_id"],
                "status": j["status"],
                "started_at": j.get("started_at"),
                "completed_at": j.get("completed_at"),
            }
            for j in jobs.values()
        ],
    }


@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a completed job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    if jobs[job_id]["status"] not in [JobStatus.COMPLETED, JobStatus.FAILED]:
        raise HTTPException(status_code=400, detail="Cannot delete running job")

    del jobs[job_id]
    return {"message": "Job deleted"}


@app.post("/cleanup")
async def cleanup_old_videos(max_age_hours: int = 24):
    """Delete videos older than max_age_hours."""
    downloader = get_downloader()
    deleted = downloader.cleanup_old_videos(max_age_hours=max_age_hours)
    return {"deleted": deleted}


# ==================== Analytics Endpoints ====================

@app.get("/analytics/summary")
async def get_analytics_summary():
    """
    Get overall analytics summary.

    Returns total videos, averages for hook strength, viral potential, replicability.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        summary = storage.get_analytics_summary()
        return summary
    except Exception as e:
        logger.error(f"Failed to get analytics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/hooks")
async def get_hook_trends(limit: int = 20):
    """
    Get hook type and technique distribution.

    Shows which hook types (text, question, visual, etc.) and techniques
    (relatable_pain, curiosity_gap, etc.) are most common.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        hooks = storage.get_hook_trends(limit=limit)
        return {"hook_trends": hooks}
    except Exception as e:
        logger.error(f"Failed to get hook trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/audio")
async def get_audio_trends(limit: int = 20):
    """
    Get audio/sound category distribution.

    Shows trending_audio, voiceover, dialogue, etc. breakdown.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        audio = storage.get_audio_trends(limit=limit)
        return {"audio_trends": audio}
    except Exception as e:
        logger.error(f"Failed to get audio trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/visual")
async def get_visual_trends(limit: int = 20):
    """
    Get visual style and setting distribution.

    Shows casual vs raw vs polished styles, and setting types (bar, outdoor, etc.).
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        visual = storage.get_visual_trends(limit=limit)
        return {"visual_trends": visual}
    except Exception as e:
        logger.error(f"Failed to get visual trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/viral")
async def get_viral_trends(limit: int = 20):
    """
    Get viral potential score distribution and top viral factors.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        viral = storage.get_viral_trends(limit=limit)
        factors = storage.get_viral_factors(limit=limit)
        return {
            "viral_score_distribution": viral,
            "top_viral_factors": factors,
        }
    except Exception as e:
        logger.error(f"Failed to get viral trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/replicability")
async def get_replicability_leaderboard(
    min_score: int = 6,
    difficulty: Optional[str] = None,
    limit: int = 20,
):
    """
    Get top videos by replicability score.

    Filter by minimum score and difficulty level (easy, medium, hard).
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        leaderboard = storage.get_replicability_leaderboard(
            min_score=min_score,
            difficulty=difficulty,
            limit=limit,
        )
        return {"replicability_leaderboard": leaderboard}
    except Exception as e:
        logger.error(f"Failed to get replicability leaderboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analytics/all")
async def get_all_analytics():
    """
    Get all analytics data in one request.

    Combines summary, hooks, audio, visual, viral, and replicability data.
    Ideal for dashboard rendering.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        return {
            "summary": storage.get_analytics_summary(),
            "hooks": storage.get_hook_trends(limit=10),
            "audio": storage.get_audio_trends(limit=10),
            "visual": storage.get_visual_trends(limit=10),
            "viral_factors": storage.get_viral_factors(limit=10),
            "top_replicable": storage.get_replicability_leaderboard(min_score=7, limit=10),
        }
    except Exception as e:
        logger.error(f"Failed to get all analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global _extractor

    if _extractor:
        await _extractor.close()


# For running directly
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=False,  # Disabled for Windows Playwright compatibility
    )
