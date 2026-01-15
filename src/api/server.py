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
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.extractor import HashtagExtractor, Platform, ExtractionResult, VideoInfo
from src.extractor import ProfileExtractor, ProfileInfo, ProfileExtractionResult
from src.extractor.youtube_shorts import YouTubeShortsExtractor
from src.extractor.substack import SubstackExtractor
from src.downloader import VideoDownloader, DownloadResult
from src.analyzer import GeminiAnalyzer, VideoAnalysis, AccountComparer
from src.storage import SupabaseStorage
from src.generator import HashtagGenerator
from src.api.routes import analytics_router
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Social Scraper API",
    description="Extract, download, and analyze social media videos",
    version="0.5.0",
)

# Enable CORS for dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (including file://)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analytics_router, prefix="/analytics", tags=["analytics"])

# Global instances (lazy initialized)
_extractor: Optional[HashtagExtractor] = None
_profile_extractor: Optional[ProfileExtractor] = None
_downloader: Optional[VideoDownloader] = None
_analyzer: Optional[GeminiAnalyzer] = None
_comparer: Optional[AccountComparer] = None
_storage: Optional[SupabaseStorage] = None
_generator: Optional[HashtagGenerator] = None

# Job storage
jobs: dict[str, dict] = {}
batch_jobs: dict[str, dict] = {}
account_jobs: dict[str, dict] = {}


class JobStatus(str, Enum):
    QUEUED = "queued"
    EXTRACTING = "extracting"
    DOWNLOADING = "downloading"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class BatchJobStatus(str, Enum):
    QUEUED = "queued"
    GENERATING = "generating"  # Generating hashtags from niche query
    PROCESSING = "processing"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"


class HashtagStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


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
    niche_mode: Optional[str] = Field(
        default=None,
        description="Analysis mode: 'entertainment', 'data_engineering', or 'both'. Defaults to global setting."
    )


class PipelineRequest(BaseModel):
    platform: Platform
    hashtag: str
    count: int = Field(default=30, ge=1, le=50)
    skip_analysis: bool = Field(default=False, description="Skip Gemini analysis")
    store_to_supabase: bool = Field(default=False, description="Store results in Supabase")
    niche_mode: Optional[str] = Field(
        default=None,
        description="Analysis mode: 'entertainment', 'data_engineering', or 'both'. Defaults to global setting."
    )


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


# Batch Pipeline Models

class GenerateHashtagsRequest(BaseModel):
    niche_description: str = Field(..., description="Description of the content niche")
    platform: Platform = Platform.TIKTOK
    count: int = Field(default=10, ge=1, le=50)


class GenerateHashtagsResponse(BaseModel):
    success: bool
    hashtags: list[str]
    niche_description: str
    error: Optional[str] = None


class BatchPipelineRequest(BaseModel):
    platform: Platform
    hashtags: Optional[list[str]] = Field(default=None, description="List of hashtags to process")
    niche_query: Optional[str] = Field(default=None, description="Generate hashtags from niche description")
    niche: Optional[str] = Field(default=None, description="Niche category for grouping (e.g., 'dj_nightlife', 'bars_restaurants')")
    niche_mode: Optional[str] = Field(
        default=None,
        description="Analysis mode: 'entertainment', 'data_engineering', or 'both'. Defaults to global setting."
    )
    hashtag_count: int = Field(default=10, ge=1, le=50, description="Number of hashtags to generate")
    videos_per_hashtag: int = Field(default=10, ge=1, le=30)
    skip_analysis: bool = False
    store_to_supabase: bool = True
    delay_between_hashtags: Optional[int] = None  # Uses settings default if not specified


class BatchJobResponse(BaseModel):
    batch_id: str
    status: BatchJobStatus
    message: str


class HashtagResult(BaseModel):
    hashtag: str
    status: HashtagStatus
    videos_found: int = 0
    videos_downloaded: int = 0
    videos_analyzed: int = 0
    error: Optional[str] = None
    attempt: int = 1


class BatchPipelineResult(BaseModel):
    batch_id: str
    status: BatchJobStatus
    hashtags: list[str]
    results: dict[str, HashtagResult]
    progress: dict
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


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


def get_generator() -> HashtagGenerator:
    """Get or create the hashtag generator."""
    global _generator
    if _generator is None:
        if not settings.gemini_api_key:
            raise HTTPException(
                status_code=500,
                detail="Gemini API key not configured"
            )
        _generator = HashtagGenerator(api_key=settings.gemini_api_key)
    return _generator


def get_profile_extractor() -> ProfileExtractor:
    """Get or create the profile extractor."""
    global _profile_extractor
    if _profile_extractor is None:
        _profile_extractor = ProfileExtractor()
    return _profile_extractor


def get_comparer() -> AccountComparer:
    """Get or create the account comparer."""
    global _comparer
    if _comparer is None:
        _comparer = AccountComparer()
    return _comparer


# Endpoints

@app.get("/api")
async def api_info():
    """API info endpoint."""
    return {
        "name": "Social Scraper API",
        "version": "0.5.0",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    downloader = get_downloader()
    disk_storage = downloader.get_storage_usage()

    return {
        "status": "healthy",
        "version": "0.5.0",
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

    Args:
        request.niche_mode: 'entertainment', 'data_engineering', or 'both'

    Returns list of analysis results.
    """
    # Create analyzer with specified niche_mode (or use default from settings)
    niche_mode = request.niche_mode or settings.niche_mode
    analyzer = GeminiAnalyzer(api_key=settings.gemini_api_key, niche_mode=niche_mode)

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

            # Create analyzer with specified niche_mode
            niche_mode = request.niche_mode or settings.niche_mode
            analyzer = GeminiAnalyzer(api_key=settings.gemini_api_key, niche_mode=niche_mode)
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
                niche_mode = request.niche_mode or settings.niche_mode
                stored = storage.store_batch(
                    videos=extraction.videos,
                    downloads=downloads,
                    analyses=analyses_list,
                    niche_mode=niche_mode,
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


# ==================== Batch Pipeline Endpoints ====================

@app.post("/generate-hashtags", response_model=GenerateHashtagsResponse)
async def generate_hashtags(request: GenerateHashtagsRequest):
    """
    Generate relevant hashtags from a niche description using AI.

    Example: "cocktail bartending content" → ["bartender", "mixology", "cocktails", ...]
    """
    generator = get_generator()

    result = await generator.generate_hashtags(
        niche_description=request.niche_description,
        platform=request.platform.value,
        count=request.count,
    )

    return GenerateHashtagsResponse(
        success=result.success,
        hashtags=result.hashtags,
        niche_description=result.niche_description,
        error=result.error,
    )


@app.post("/batch-pipeline", response_model=BatchJobResponse)
async def run_batch_pipeline(
    request: BatchPipelineRequest,
    background_tasks: BackgroundTasks,
):
    """
    Run pipeline on multiple hashtags sequentially.

    Either provide a list of hashtags OR a niche_query to generate hashtags.
    Failed hashtags are retried at the end of the batch.
    """
    if not request.hashtags and not request.niche_query:
        raise HTTPException(
            status_code=400,
            detail="Must provide either 'hashtags' list or 'niche_query'"
        )

    batch_id = str(uuid.uuid4())

    batch_jobs[batch_id] = {
        "batch_id": batch_id,
        "status": BatchJobStatus.QUEUED,
        "request": request.model_dump(),
        "hashtags": request.hashtags or [],
        "results": {},
        "current_hashtag": None,
        "current_pass": 1,
        "progress": {
            "total": 0,
            "completed": 0,
            "failed": 0,
            "remaining": 0,
        },
        "error": None,
        "started_at": None,
        "completed_at": None,
    }

    background_tasks.add_task(run_batch_pipeline_job, batch_id, request)

    return BatchJobResponse(
        batch_id=batch_id,
        status=BatchJobStatus.QUEUED,
        message=f"Batch pipeline queued for {request.platform.value}",
    )


async def process_single_hashtag(
    hashtag: str,
    platform: Platform,
    count: int,
    skip_analysis: bool,
    store_to_supabase: bool,
    niche: Optional[str] = None,
    niche_mode: Optional[str] = None,
) -> dict:
    """
    Process a single hashtag through the full pipeline.

    Args:
        niche: Business vertical for grouping (e.g., 'dj_nightlife')
        niche_mode: Analysis mode ('entertainment', 'data_engineering', 'both')

    Returns dict with extraction, download, and analysis results.
    """
    result = {
        "videos_found": 0,
        "videos_downloaded": 0,
        "videos_analyzed": 0,
    }

    # Step 1: Extract
    extractor = get_extractor()
    extraction = await extractor.extract_hashtag(
        platform=platform,
        hashtag=hashtag,
        count=count,
    )

    if not extraction.success or not extraction.videos:
        raise Exception(f"Extraction failed: {extraction.error or 'No videos found'}")

    result["videos_found"] = extraction.videos_found

    # Step 2: Download
    downloader = get_downloader()
    urls = [v.video_url for v in extraction.videos]

    downloads = await downloader.download_batch(
        urls=urls,
        platform=platform.value,
        max_concurrent=settings.max_concurrent_downloads,
    )

    successful_downloads = [d for d in downloads if d.success and d.file_path]
    result["videos_downloaded"] = len(successful_downloads)

    if not successful_downloads:
        raise Exception("No videos downloaded successfully")

    # Step 3: Analyze (optional)
    analyses = []
    if not skip_analysis:
        # Create analyzer with specified niche_mode
        effective_niche_mode = niche_mode or settings.niche_mode
        analyzer = GeminiAnalyzer(api_key=settings.gemini_api_key, niche_mode=effective_niche_mode)
        paths = [d.file_path for d in successful_downloads]

        analyses = await analyzer.analyze_batch(
            video_paths=paths,
            max_concurrent=settings.max_concurrent_analyses,
        )
        result["videos_analyzed"] = len([a for a in analyses if a.success])

    # Step 4: Store to Supabase (optional)
    if store_to_supabase:
        storage = get_storage()
        if storage:
            effective_niche_mode = niche_mode or settings.niche_mode
            stored = storage.store_batch(
                videos=extraction.videos,
                downloads=downloads,
                analyses=analyses if analyses else None,
                niche=niche,
                source_hashtag=hashtag,
                niche_mode=effective_niche_mode,
            )
            logger.info(f"Stored {stored} posts for #{hashtag}")

    return result


async def run_batch_pipeline_job(batch_id: str, request: BatchPipelineRequest) -> None:
    """Background task to run batch pipeline across multiple hashtags."""
    batch_jobs[batch_id]["started_at"] = datetime.utcnow().isoformat()

    try:
        # Phase 1: Get hashtags (generate if needed)
        if request.niche_query:
            batch_jobs[batch_id]["status"] = BatchJobStatus.GENERATING
            logger.info(f"[{batch_id}] Generating hashtags for: {request.niche_query}")

            generator = get_generator()
            gen_result = await generator.generate_hashtags(
                niche_description=request.niche_query,
                platform=request.platform.value,
                count=request.hashtag_count,
            )

            if not gen_result.success:
                raise Exception(f"Hashtag generation failed: {gen_result.error}")

            hashtags = gen_result.hashtags
        else:
            hashtags = request.hashtags

        batch_jobs[batch_id]["hashtags"] = hashtags
        batch_jobs[batch_id]["progress"]["total"] = len(hashtags)
        batch_jobs[batch_id]["progress"]["remaining"] = len(hashtags)

        # Initialize results for each hashtag
        for hashtag in hashtags:
            batch_jobs[batch_id]["results"][hashtag] = {
                "hashtag": hashtag,
                "status": HashtagStatus.PENDING.value,
                "videos_found": 0,
                "videos_downloaded": 0,
                "videos_analyzed": 0,
                "error": None,
                "attempt": 1,
            }

        # Phase 2: First pass - process all hashtags
        batch_jobs[batch_id]["status"] = BatchJobStatus.PROCESSING
        delay = request.delay_between_hashtags or settings.batch_delay_between_hashtags
        failed_hashtags = []

        for i, hashtag in enumerate(hashtags):
            batch_jobs[batch_id]["current_hashtag"] = hashtag
            batch_jobs[batch_id]["results"][hashtag]["status"] = HashtagStatus.RUNNING.value
            logger.info(f"[{batch_id}] Processing #{hashtag} ({i+1}/{len(hashtags)})")

            try:
                result = await process_single_hashtag(
                    hashtag=hashtag,
                    platform=request.platform,
                    count=request.videos_per_hashtag,
                    skip_analysis=request.skip_analysis,
                    store_to_supabase=request.store_to_supabase,
                    niche=request.niche,
                    niche_mode=request.niche_mode,
                )

                batch_jobs[batch_id]["results"][hashtag].update(result)
                batch_jobs[batch_id]["results"][hashtag]["status"] = HashtagStatus.COMPLETED.value
                batch_jobs[batch_id]["progress"]["completed"] += 1

            except Exception as e:
                logger.error(f"[{batch_id}] #{hashtag} failed: {e}")
                batch_jobs[batch_id]["results"][hashtag]["status"] = HashtagStatus.FAILED.value
                batch_jobs[batch_id]["results"][hashtag]["error"] = str(e)
                batch_jobs[batch_id]["progress"]["failed"] += 1
                failed_hashtags.append(hashtag)

            batch_jobs[batch_id]["progress"]["remaining"] -= 1

            # Delay between hashtags (except for last one)
            if i < len(hashtags) - 1:
                logger.info(f"[{batch_id}] Waiting {delay}s before next hashtag...")
                await asyncio.sleep(delay)

        # Phase 3: Retry pass for failed hashtags
        if failed_hashtags and settings.batch_max_retries > 0:
            batch_jobs[batch_id]["status"] = BatchJobStatus.RETRYING
            batch_jobs[batch_id]["current_pass"] = 2
            logger.info(f"[{batch_id}] Retrying {len(failed_hashtags)} failed hashtags...")

            # Extra delay before retry pass
            await asyncio.sleep(settings.batch_retry_delay)

            for hashtag in failed_hashtags:
                batch_jobs[batch_id]["current_hashtag"] = hashtag
                batch_jobs[batch_id]["results"][hashtag]["status"] = HashtagStatus.RETRYING.value
                batch_jobs[batch_id]["results"][hashtag]["attempt"] = 2
                logger.info(f"[{batch_id}] Retrying #{hashtag}")

                try:
                    result = await process_single_hashtag(
                        hashtag=hashtag,
                        platform=request.platform,
                        count=request.videos_per_hashtag,
                        skip_analysis=request.skip_analysis,
                        niche=request.niche,
                        niche_mode=request.niche_mode,
                        store_to_supabase=request.store_to_supabase,
                    )

                    batch_jobs[batch_id]["results"][hashtag].update(result)
                    batch_jobs[batch_id]["results"][hashtag]["status"] = HashtagStatus.COMPLETED.value
                    # Adjust counts
                    batch_jobs[batch_id]["progress"]["completed"] += 1
                    batch_jobs[batch_id]["progress"]["failed"] -= 1

                except Exception as e:
                    logger.error(f"[{batch_id}] #{hashtag} retry failed: {e}")
                    batch_jobs[batch_id]["results"][hashtag]["status"] = HashtagStatus.FAILED.value
                    batch_jobs[batch_id]["results"][hashtag]["error"] = str(e)

                await asyncio.sleep(delay)

        batch_jobs[batch_id]["status"] = BatchJobStatus.COMPLETED
        batch_jobs[batch_id]["current_hashtag"] = None
        logger.info(f"[{batch_id}] Batch pipeline completed")

    except Exception as e:
        logger.error(f"[{batch_id}] Batch pipeline failed: {e}")
        batch_jobs[batch_id]["status"] = BatchJobStatus.FAILED
        batch_jobs[batch_id]["error"] = str(e)

    finally:
        batch_jobs[batch_id]["completed_at"] = datetime.utcnow().isoformat()


@app.get("/batch-pipeline/{batch_id}")
async def get_batch_pipeline_status(batch_id: str):
    """Get batch pipeline job status and per-hashtag results."""
    if batch_id not in batch_jobs:
        raise HTTPException(status_code=404, detail="Batch job not found")

    job = batch_jobs[batch_id]

    return {
        "batch_id": job["batch_id"],
        "status": job["status"],
        "hashtags": job["hashtags"],
        "results": job["results"],
        "current_hashtag": job.get("current_hashtag"),
        "current_pass": job.get("current_pass", 1),
        "progress": job["progress"],
        "error": job["error"],
        "started_at": job["started_at"],
        "completed_at": job["completed_at"],
    }


@app.get("/batch-jobs")
async def list_batch_jobs():
    """List all batch jobs."""
    return {
        "count": len(batch_jobs),
        "jobs": [
            {
                "batch_id": j["batch_id"],
                "status": j["status"],
                "hashtags_count": len(j.get("hashtags", [])),
                "progress": j.get("progress"),
                "started_at": j.get("started_at"),
                "completed_at": j.get("completed_at"),
            }
            for j in batch_jobs.values()
        ],
    }


# ==================== YouTube Shorts & Substack Endpoints ====================

class YouTubeShortsRequest(BaseModel):
    query: str = Field(..., description="Search query (e.g., 'microsoft fabric tutorial')")
    count: int = Field(default=30, ge=1, le=50, description="Number of videos to extract")
    order: str = Field(default="relevance", description="Sort order: relevance, date, viewCount")


class SubstackRequest(BaseModel):
    publication: str = Field(..., description="Publication subdomain (e.g., 'engdata' for engdata.substack.com)")
    count: int = Field(default=30, ge=1, le=100, description="Number of posts to extract")


class MultiSubstackRequest(BaseModel):
    publications: list[str] = Field(..., description="List of publication subdomains")
    count_per_publication: int = Field(default=10, ge=1, le=50)


@app.post("/extract/youtube-shorts")
async def extract_youtube_shorts(request: YouTubeShortsRequest):
    """
    Extract YouTube Shorts matching a search query.

    Uses YouTube Data API v3 to search for Shorts (videos under 60 seconds).
    Requires YOUTUBE_API_KEY in environment.
    """
    if not settings.youtube_api_key:
        raise HTTPException(
            status_code=503,
            detail="YouTube API key not configured. Set YOUTUBE_API_KEY in .env"
        )

    try:
        extractor = YouTubeShortsExtractor(api_key=settings.youtube_api_key)
        result = await extractor.search_shorts(
            query=request.query,
            count=request.count,
            order=request.order
        )

        return {
            "success": result.success,
            "videos_requested": result.videos_requested,
            "videos_found": result.videos_found,
            "videos": [v.to_dict() for v in result.videos],
            "error": result.error,
        }
    except Exception as e:
        logger.error(f"YouTube Shorts extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/extract/substack")
async def extract_substack(request: SubstackRequest):
    """
    Extract posts and embedded videos from a Substack publication.

    Parses the RSS feed to find posts with embedded videos (YouTube, Loom, etc.).
    """
    try:
        extractor = SubstackExtractor()
        posts, result = await extractor.extract_publication(
            publication_name=request.publication,
            count=request.count
        )

        return {
            "success": result.success,
            "publication": request.publication,
            "posts_found": len(posts),
            "videos_found": result.videos_found,
            "posts": [
                {
                    "title": p.title,
                    "url": p.url,
                    "author": p.author,
                    "published_at": p.published_at.isoformat() if p.published_at else None,
                    "embedded_videos": p.embedded_videos,
                }
                for p in posts
            ],
            "videos": [v.to_dict() for v in result.videos],
            "error": result.error,
        }
    except Exception as e:
        logger.error(f"Substack extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/extract/substack/multiple")
async def extract_multiple_substacks(request: MultiSubstackRequest):
    """
    Extract from multiple Substack publications at once.
    """
    try:
        extractor = SubstackExtractor()
        result = await extractor.extract_multiple_publications(
            publication_names=request.publications,
            count_per_publication=request.count_per_publication
        )

        return {
            "success": result.success,
            "publications_requested": len(request.publications),
            "videos_found": result.videos_found,
            "videos": [v.to_dict() for v in result.videos],
            "error": result.error,
        }
    except Exception as e:
        logger.error(f"Multiple Substack extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Account Analysis Endpoints ====================

class AccountJobStatus(str, Enum):
    QUEUED = "queued"
    SCRAPING = "scraping"
    DOWNLOADING = "downloading"
    ANALYZING = "analyzing"
    COMPARING = "comparing"
    COMPLETED = "completed"
    FAILED = "failed"


class CreateAccountRequest(BaseModel):
    platform: Platform
    username: str = Field(..., description="Username (without @)")


class AccountResponse(BaseModel):
    id: str
    platform: str
    username: str
    display_name: Optional[str] = None
    follower_count: Optional[int] = None
    status: str
    created_at: str


@app.post("/accounts")
async def create_account(request: CreateAccountRequest):
    """
    Add an account to track.

    Creates the account record and optionally links any existing posts.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        account = storage.create_account(
            platform=request.platform.value,
            username=request.username,
        )

        # Link any existing posts from this author
        if account.get("id"):
            linked = storage.link_posts_to_account(
                account_id=account["id"],
                author_username=request.username,
            )
            account["posts_linked"] = linked

        return account
    except Exception as e:
        logger.error(f"Failed to create account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/accounts")
async def list_accounts():
    """
    List all tracked accounts with summary stats.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        accounts = storage.list_accounts()
        return {"accounts": accounts, "count": len(accounts)}
    except Exception as e:
        logger.error(f"Failed to list accounts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/accounts/{account_id}")
async def get_account(account_id: str):
    """
    Get account details by ID.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        account = storage.get_account(account_id)
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")
        return account
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/accounts/{account_id}")
async def delete_account(account_id: str):
    """
    Delete an account (cascades snapshots, nullifies post links).
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        success = storage.delete_account(account_id)
        if not success:
            raise HTTPException(status_code=404, detail="Account not found or delete failed")
        return {"message": "Account deleted", "account_id": account_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete account: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/accounts/{account_id}/analyze")
async def analyze_account(
    account_id: str,
    background_tasks: BackgroundTasks,
    video_count: int = 30,
    niche_mode: Optional[str] = None,
):
    """
    Run full analysis on an account: scrape profile → download videos → analyze → compare.

    Args:
        niche_mode: Analysis mode ('entertainment', 'data_engineering', 'both'). Defaults to global setting.

    Returns a job_id to poll for status.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    # Verify account exists
    account = storage.get_account(account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    job_id = str(uuid.uuid4())

    account_jobs[job_id] = {
        "job_id": job_id,
        "account_id": account_id,
        "status": AccountJobStatus.QUEUED,
        "platform": account["platform"],
        "username": account["username"],
        "video_count": video_count,
        "progress": {
            "videos_found": 0,
            "videos_downloaded": 0,
            "videos_analyzed": 0,
        },
        "comparison": None,
        "error": None,
        "started_at": None,
        "completed_at": None,
    }

    # Update account status
    storage.update_account(account_id, status="analyzing")

    background_tasks.add_task(run_account_analysis_job, job_id, account, video_count, niche_mode)

    return {
        "job_id": job_id,
        "status": AccountJobStatus.QUEUED,
        "message": f"Analysis queued for @{account['username']}",
    }


async def run_account_analysis_job(
    job_id: str,
    account: dict,
    video_count: int,
    niche_mode: Optional[str] = None,
) -> None:
    """Background task to run full account analysis."""
    account_jobs[job_id]["started_at"] = datetime.utcnow().isoformat()
    storage = get_storage()
    account_id = account["id"]

    try:
        # Step 1: Scrape profile
        account_jobs[job_id]["status"] = AccountJobStatus.SCRAPING
        logger.info(f"[{job_id}] Scraping profile @{account['username']}")

        profile_extractor = get_profile_extractor()
        platform = Platform(account["platform"])

        extraction = await profile_extractor.extract_profile(
            platform=platform,
            username=account["username"],
            video_count=video_count,
        )

        if not extraction.success:
            raise Exception(f"Profile extraction failed: {extraction.error}")

        # Update account with profile info
        if extraction.profile_info:
            pi = extraction.profile_info
            storage.update_account(
                account_id,
                display_name=pi.display_name,
                bio=pi.bio,
                profile_picture_url=pi.profile_picture_url,
                follower_count=pi.follower_count,
                following_count=pi.following_count,
                post_count=pi.post_count,
                is_verified=pi.is_verified,
                is_private=pi.is_private,
            )

            if pi.is_private:
                raise Exception("Account is private - cannot access videos")

        account_jobs[job_id]["progress"]["videos_found"] = len(extraction.videos)

        if not extraction.videos:
            raise Exception("No videos found on profile")

        # Step 2: Download videos
        account_jobs[job_id]["status"] = AccountJobStatus.DOWNLOADING
        logger.info(f"[{job_id}] Downloading {len(extraction.videos)} videos")

        downloader = get_downloader()
        urls = [v.video_url for v in extraction.videos]

        downloads = await downloader.download_batch(
            urls=urls,
            platform=platform.value,
            max_concurrent=settings.max_concurrent_downloads,
        )

        successful_downloads = [d for d in downloads if d.success and d.file_path]
        account_jobs[job_id]["progress"]["videos_downloaded"] = len(successful_downloads)

        if not successful_downloads:
            raise Exception("No videos downloaded successfully")

        # Step 3: Analyze videos
        account_jobs[job_id]["status"] = AccountJobStatus.ANALYZING
        logger.info(f"[{job_id}] Analyzing {len(successful_downloads)} videos")

        analyzer = get_analyzer()
        paths = [d.file_path for d in successful_downloads]

        analyses = await analyzer.analyze_batch(
            video_paths=paths,
            max_concurrent=settings.max_concurrent_analyses,
        )

        successful_analyses = [a for a in analyses if a.success]
        account_jobs[job_id]["progress"]["videos_analyzed"] = len(successful_analyses)

        # Step 4: Store posts linked to account
        stored = storage.store_batch(
            videos=extraction.videos,
            downloads=downloads,
            analyses=analyses,
            niche_mode=niche_mode,
        )
        logger.info(f"[{job_id}] Stored {stored} posts")

        # Link posts to account
        storage.link_posts_to_account(account_id, account["username"])

        # Step 5: Generate comparison
        account_jobs[job_id]["status"] = AccountJobStatus.COMPARING
        logger.info(f"[{job_id}] Generating comparison")

        # Get account posts and dataset posts for comparison
        account_posts = storage.get_account_posts(account_id)
        dataset_posts = storage.get_analyzed_posts_raw(limit=500)
        dataset_averages = storage.get_dataset_averages()

        comparer = get_comparer()
        comparison = comparer.generate_full_comparison(
            account_posts=account_posts,
            dataset_posts=dataset_posts,
            dataset_averages=dataset_averages,
        )

        account_jobs[job_id]["comparison"] = comparison

        # Create a snapshot
        storage.create_account_snapshot(
            account_id=account_id,
            video_count=comparison["scores"]["video_count"],
            analyzed_count=comparison["scores"]["analyzed_count"],
            avg_hook_strength=comparison["scores"]["account_averages"]["hook"],
            avg_viral_potential=comparison["scores"]["account_averages"]["viral"],
            avg_replicability=comparison["scores"]["account_averages"]["replicability"],
            hook_types=comparison["patterns"]["account_patterns"].get("hook_types"),
            audio_categories=comparison["patterns"]["account_patterns"].get("audio_categories"),
            visual_styles=comparison["patterns"]["account_patterns"].get("visual_styles"),
            dataset_comparison=comparison["scores"]["vs_dataset"],
            percentile_ranks=comparison["scores"]["percentiles"],
            recommendations=comparison["recommendations"],
            gaps=comparison["gaps"],
        )

        # Update account status
        storage.update_account(account_id, status="active")
        storage.client.table("accounts").update({
            "last_analyzed_at": datetime.utcnow().isoformat()
        }).eq("id", account_id).execute()

        account_jobs[job_id]["status"] = AccountJobStatus.COMPLETED
        logger.info(f"[{job_id}] Account analysis completed")

    except Exception as e:
        logger.error(f"[{job_id}] Account analysis failed: {e}")
        account_jobs[job_id]["status"] = AccountJobStatus.FAILED
        account_jobs[job_id]["error"] = str(e)
        if storage:
            storage.update_account(account_id, status="error", scrape_error=str(e))

    finally:
        account_jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()


@app.get("/accounts/{account_id}/analyze/{job_id}")
async def get_account_analysis_status(account_id: str, job_id: str):
    """
    Get status of an account analysis job.
    """
    if job_id not in account_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = account_jobs[job_id]

    if job["account_id"] != account_id:
        raise HTTPException(status_code=404, detail="Job not found for this account")

    return job


@app.get("/accounts/{account_id}/comparison")
async def get_account_comparison(account_id: str):
    """
    Get full comparison data for an account vs the dataset.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        # Get account posts
        account_posts = storage.get_account_posts(account_id)
        if not account_posts:
            return {
                "message": "No posts found for account",
                "comparison": None,
            }

        # Get dataset for comparison
        dataset_posts = storage.get_analyzed_posts_raw(limit=500)
        dataset_averages = storage.get_dataset_averages()

        comparer = get_comparer()
        comparison = comparer.generate_full_comparison(
            account_posts=account_posts,
            dataset_posts=dataset_posts,
            dataset_averages=dataset_averages,
        )

        return {"comparison": comparison}
    except Exception as e:
        logger.error(f"Failed to get account comparison: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/accounts/{account_id}/snapshots")
async def get_account_snapshots(account_id: str, limit: int = 10):
    """
    Get historical snapshots for an account.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        snapshots = storage.get_account_snapshots(account_id, limit=limit)
        return {"snapshots": snapshots, "count": len(snapshots)}
    except Exception as e:
        logger.error(f"Failed to get snapshots: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/accounts/{account_id}/snapshot")
async def create_account_snapshot(account_id: str):
    """
    Create a new snapshot of current account metrics.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        # Get current account posts and generate comparison
        account_posts = storage.get_account_posts(account_id)
        if not account_posts:
            raise HTTPException(status_code=400, detail="No posts to snapshot")

        dataset_posts = storage.get_analyzed_posts_raw(limit=500)
        dataset_averages = storage.get_dataset_averages()

        comparer = get_comparer()
        comparison = comparer.generate_full_comparison(
            account_posts=account_posts,
            dataset_posts=dataset_posts,
            dataset_averages=dataset_averages,
        )

        snapshot = storage.create_account_snapshot(
            account_id=account_id,
            video_count=comparison["scores"]["video_count"],
            analyzed_count=comparison["scores"]["analyzed_count"],
            avg_hook_strength=comparison["scores"]["account_averages"]["hook"],
            avg_viral_potential=comparison["scores"]["account_averages"]["viral"],
            avg_replicability=comparison["scores"]["account_averages"]["replicability"],
            hook_types=comparison["patterns"]["account_patterns"].get("hook_types"),
            audio_categories=comparison["patterns"]["account_patterns"].get("audio_categories"),
            visual_styles=comparison["patterns"]["account_patterns"].get("visual_styles"),
            dataset_comparison=comparison["scores"]["vs_dataset"],
            percentile_ranks=comparison["scores"]["percentiles"],
            recommendations=comparison["recommendations"],
            gaps=comparison["gaps"],
        )

        return snapshot
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create snapshot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# BATCH PROCESSING ENDPOINTS
# =============================================================================

class BatchCollectRequest(BaseModel):
    """Request for batch collection."""
    youtube_queries: Optional[list[str]] = Field(default=None, description="YouTube search queries")
    tiktok_hashtags: Optional[list[str]] = Field(default=None, description="TikTok hashtags (without #)")
    substack_publications: Optional[list[str]] = Field(default=None, description="Substack publication names")
    count_per_source: int = Field(default=50, ge=1, le=200, description="Items to collect per query/hashtag")


class BatchProcessRequest(BaseModel):
    """Request for full batch processing."""
    batch_id: str = Field(description="Batch ID from collection")
    niche: Optional[str] = Field(default=None, description="Business vertical for grouping (e.g., 'dj_nightlife')")
    niche_mode: str = Field(default="data_engineering", description="Analysis mode: 'entertainment', 'data_engineering', or 'both'")
    max_concurrent_downloads: int = Field(default=5, ge=1, le=10)
    max_concurrent_analyses: int = Field(default=3, ge=1, le=5)
    store_to_supabase: bool = Field(default=True)


# In-memory batch job storage
batch_collect_jobs: dict = {}


@app.post("/batch/collect")
async def batch_collect(request: BatchCollectRequest, background_tasks: BackgroundTasks):
    """
    Collect content URLs from multiple sources for batch processing.

    Returns a batch_id that can be used to check status and start processing.
    """
    from src.batch import BatchProcessor

    if not request.youtube_queries and not request.tiktok_hashtags and not request.substack_publications:
        raise HTTPException(
            status_code=400,
            detail="Must provide at least one source (youtube_queries, tiktok_hashtags, or substack_publications)"
        )

    batch_id = str(uuid.uuid4())

    batch_collect_jobs[batch_id] = {
        "batch_id": batch_id,
        "status": "collecting",
        "request": request.model_dump(),
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "result": None,
        "error": None,
    }

    async def run_collection():
        try:
            processor = BatchProcessor()
            result = await processor.collect_all(
                youtube_queries=request.youtube_queries,
                tiktok_hashtags=request.tiktok_hashtags,
                substack_pubs=request.substack_publications,
                count_per_source=request.count_per_source,
            )

            # Flatten all items
            all_items = (
                result.get("youtube_shorts", []) +
                result.get("tiktok", []) +
                result.get("substack", [])
            )

            # Save collection to file
            processor.save_collection(batch_id, all_items)

            # Get stats
            stats = processor.get_batch_stats(all_items)

            batch_collect_jobs[batch_id]["status"] = "completed"
            batch_collect_jobs[batch_id]["completed_at"] = datetime.utcnow().isoformat()
            batch_collect_jobs[batch_id]["result"] = stats

        except Exception as e:
            logger.error(f"Batch collection failed: {e}")
            batch_collect_jobs[batch_id]["status"] = "failed"
            batch_collect_jobs[batch_id]["error"] = str(e)

    background_tasks.add_task(run_collection)

    return {
        "batch_id": batch_id,
        "status": "collecting",
        "message": "Batch collection started. Use GET /batch/collect/{batch_id} to check status."
    }


@app.get("/batch/collect/{batch_id}")
async def get_batch_collect_status(batch_id: str):
    """Get status of a batch collection job."""
    if batch_id not in batch_collect_jobs:
        raise HTTPException(status_code=404, detail="Batch not found")

    return batch_collect_jobs[batch_id]


@app.post("/batch/process/{batch_id}")
async def batch_process(batch_id: str, request: BatchProcessRequest, background_tasks: BackgroundTasks):
    """
    Process a collected batch: download all videos and analyze with Gemini.

    This runs the full pipeline on previously collected URLs.
    """
    from src.batch import BatchProcessor
    from src.batch.analyzer import BatchAnalyzer

    # Check if collection exists
    if batch_id not in batch_collect_jobs:
        raise HTTPException(status_code=404, detail="Batch not found. Run /batch/collect first.")

    if batch_collect_jobs[batch_id]["status"] != "completed":
        raise HTTPException(status_code=400, detail=f"Batch not ready. Status: {batch_collect_jobs[batch_id]['status']}")

    process_job_id = f"{batch_id}_process"
    batch_collect_jobs[process_job_id] = {
        "batch_id": batch_id,
        "process_id": process_job_id,
        "status": "downloading",
        "started_at": datetime.utcnow().isoformat(),
        "progress": {
            "downloaded": 0,
            "analyzed": 0,
            "stored": 0,
            "total": 0,
        },
        "error": None,
    }

    async def run_processing():
        try:
            processor = BatchProcessor()
            analyzer = BatchAnalyzer(requests_per_minute=30)

            # Load collected items
            items = processor.load_collection(batch_id)
            batch_collect_jobs[process_job_id]["progress"]["total"] = len(items)

            # Download all
            logger.info(f"Downloading {len(items)} items...")
            batch_collect_jobs[process_job_id]["status"] = "downloading"
            downloaded_items = await processor.download_batch(
                items=items,
                max_concurrent=request.max_concurrent_downloads,
            )

            downloaded_count = sum(1 for i in downloaded_items if i.get("download_success"))
            batch_collect_jobs[process_job_id]["progress"]["downloaded"] = downloaded_count

            # Analyze all
            logger.info(f"Analyzing {downloaded_count} videos...")
            batch_collect_jobs[process_job_id]["status"] = "analyzing"
            analysis_result = await analyzer.analyze_with_concurrency(
                items=downloaded_items,
                batch_id=batch_id,
                max_concurrent=request.max_concurrent_analyses,
                niche_mode=request.niche_mode,
            )

            batch_collect_jobs[process_job_id]["progress"]["analyzed"] = analysis_result.analyzed

            # Store to Supabase
            if request.store_to_supabase:
                batch_collect_jobs[process_job_id]["status"] = "storing"
                storage = get_storage()
                if storage:
                    results = analyzer.load_results(batch_id)
                    stored = 0
                    for item in results:
                        if item.get("analysis"):
                            try:
                                from src.extractor import VideoInfo, Platform
                                video_info = VideoInfo(
                                    platform=Platform(item["source"]) if item["source"] in ["tiktok", "youtube_shorts"] else Platform.TIKTOK,
                                    video_url=item["url"],
                                    video_id=item.get("video_id", ""),
                                    author_username=item.get("author", ""),
                                    likes=item.get("likes", 0),
                                    views=item.get("views", 0),
                                    caption=item.get("title", ""),
                                )

                                from src.analyzer import VideoAnalysis
                                analysis = VideoAnalysis(**item["analysis"]) if isinstance(item["analysis"], dict) else item["analysis"]

                                storage.store_post(
                                    video_info=video_info,
                                    analysis=analysis,
                                    niche=request.niche,
                                    niche_mode=request.niche_mode,
                                )
                                stored += 1
                            except Exception as e:
                                logger.warning(f"Failed to store item: {e}")

                    batch_collect_jobs[process_job_id]["progress"]["stored"] = stored

            # Summary
            summary = analyzer.get_analysis_summary(analyzer.load_results(batch_id))

            batch_collect_jobs[process_job_id]["status"] = "completed"
            batch_collect_jobs[process_job_id]["completed_at"] = datetime.utcnow().isoformat()
            batch_collect_jobs[process_job_id]["summary"] = summary

        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            batch_collect_jobs[process_job_id]["status"] = "failed"
            batch_collect_jobs[process_job_id]["error"] = str(e)

    background_tasks.add_task(run_processing)

    return {
        "process_id": process_job_id,
        "status": "downloading",
        "message": "Batch processing started. Use GET /batch/process/{process_id} to check status."
    }


@app.get("/batch/process/{process_id}")
async def get_batch_process_status(process_id: str):
    """Get status of a batch processing job."""
    if process_id not in batch_collect_jobs:
        raise HTTPException(status_code=404, detail="Process job not found")

    return batch_collect_jobs[process_id]


@app.get("/batch/jobs")
async def list_batch_jobs():
    """List all batch jobs (collection and processing)."""
    return {
        "jobs": list(batch_collect_jobs.values()),
        "count": len(batch_collect_jobs),
    }


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    global _extractor

    if _extractor:
        await _extractor.close()


# Mount dashboard static files (must be after all API routes)
# This serves index.html at "/" and other static assets
app.mount("/", StaticFiles(directory="dashboard", html=True), name="dashboard")


# For running directly
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        reload=False,  # Disabled for Windows Playwright compatibility
    )
