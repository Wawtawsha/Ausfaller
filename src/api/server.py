import asyncio
import uuid
from datetime import datetime
from enum import Enum
from typing import Optional
import logging

from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field

from src.scrapers import TikTokScraper, InstagramScraper, PostData, ScraperResult
from src.utils import RateLimiter
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Social Scraper API",
    description="Scraping service for TikTok and Instagram content",
    version="0.1.0",
)

# Global state
rate_limiter = RateLimiter(
    min_delay=settings.scrape_delay_min,
    max_requests_per_window=settings.max_posts_per_session * 2,
)
jobs: dict[str, dict] = {}

# Scrapers (lazy initialized)
_tiktok_scraper: Optional[TikTokScraper] = None
_instagram_scraper: Optional[InstagramScraper] = None


async def get_tiktok_scraper() -> TikTokScraper:
    global _tiktok_scraper
    if _tiktok_scraper is None:
        _tiktok_scraper = TikTokScraper()
    return _tiktok_scraper


async def get_instagram_scraper() -> InstagramScraper:
    global _instagram_scraper
    if _instagram_scraper is None:
        _instagram_scraper = InstagramScraper()
    return _instagram_scraper


class Platform(str, Enum):
    TIKTOK = "tiktok"
    INSTAGRAM = "instagram"


class TargetType(str, Enum):
    HASHTAG = "hashtag"
    USER = "user"
    TRENDING = "trending"
    SOUND = "sound"  # TikTok only


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScrapeRequest(BaseModel):
    platform: Platform
    target_type: TargetType
    target: str = Field(
        ...,
        description="Hashtag name, username, or 'trending' for trending content",
        examples=["bartender", "tipsy_bartender", "trending"],
    )
    count: int = Field(
        default=30,
        ge=1,
        le=100,
        description="Number of posts to scrape",
    )


class ScrapeResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str


class JobResult(BaseModel):
    job_id: str
    status: JobStatus
    platform: Platform
    target_type: TargetType
    target: str
    posts_requested: int
    posts_retrieved: int
    posts: list[dict] = Field(default_factory=list)
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    version: str
    rate_limits: dict


async def run_scrape_job(job_id: str, request: ScrapeRequest) -> None:
    """Background task to run a scrape job."""
    jobs[job_id]["status"] = JobStatus.RUNNING
    jobs[job_id]["started_at"] = datetime.utcnow().isoformat()

    try:
        # Acquire rate limit
        await rate_limiter.acquire(request.platform.value)

        # Get appropriate scraper
        if request.platform == Platform.TIKTOK:
            scraper = await get_tiktok_scraper()
        else:
            scraper = await get_instagram_scraper()

        # Execute scrape based on target type
        result: ScraperResult

        if request.target_type == TargetType.HASHTAG:
            result = await scraper.get_hashtag_posts(request.target, request.count)
        elif request.target_type == TargetType.USER:
            result = await scraper.get_user_posts(request.target, request.count)
        elif request.target_type == TargetType.TRENDING:
            result = await scraper.get_trending(request.count)
        elif request.target_type == TargetType.SOUND:
            if request.platform != Platform.TIKTOK:
                raise ValueError("Sound scraping only available for TikTok")
            result = await scraper.get_sound_posts(request.target, request.count)
        else:
            raise ValueError(f"Unknown target type: {request.target_type}")

        # Report success/failure to rate limiter
        if result.success:
            rate_limiter.report_success(request.platform.value)
        else:
            rate_limiter.report_failure(request.platform.value)

        # Update job
        jobs[job_id]["status"] = JobStatus.COMPLETED if result.success else JobStatus.FAILED
        jobs[job_id]["posts"] = [p.to_dict() for p in result.posts]
        jobs[job_id]["posts_retrieved"] = result.posts_retrieved
        jobs[job_id]["error"] = result.error

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        rate_limiter.report_failure(request.platform.value)
        jobs[job_id]["status"] = JobStatus.FAILED
        jobs[job_id]["error"] = str(e)

    finally:
        jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        rate_limits={
            "tiktok": rate_limiter.get_stats("tiktok"),
            "instagram": rate_limiter.get_stats("instagram"),
        },
    )


@app.post("/scrape", response_model=ScrapeResponse)
async def create_scrape_job(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks,
):
    """
    Queue a new scrape job.

    Returns immediately with a job_id. Poll /scrape/{job_id} to get results.
    """
    job_id = str(uuid.uuid4())

    jobs[job_id] = {
        "job_id": job_id,
        "status": JobStatus.QUEUED,
        "platform": request.platform,
        "target_type": request.target_type,
        "target": request.target,
        "posts_requested": request.count,
        "posts_retrieved": 0,
        "posts": [],
        "error": None,
        "started_at": None,
        "completed_at": None,
    }

    background_tasks.add_task(run_scrape_job, job_id, request)

    return ScrapeResponse(
        job_id=job_id,
        status=JobStatus.QUEUED,
        message=f"Scrape job queued for {request.platform.value} {request.target_type.value}: {request.target}",
    )


@app.get("/scrape/{job_id}", response_model=JobResult)
async def get_job_status(job_id: str):
    """Get the status and results of a scrape job."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobResult(**jobs[job_id])


@app.delete("/scrape/{job_id}")
async def delete_job(job_id: str):
    """Delete a completed job from memory."""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    if jobs[job_id]["status"] in [JobStatus.QUEUED, JobStatus.RUNNING]:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete a job that is still running",
        )

    del jobs[job_id]
    return {"message": "Job deleted"}


@app.get("/jobs")
async def list_jobs():
    """List all jobs (for debugging)."""
    return {
        "count": len(jobs),
        "jobs": [
            {
                "job_id": j["job_id"],
                "status": j["status"],
                "platform": j["platform"],
                "target": j["target"],
                "posts_retrieved": j["posts_retrieved"],
            }
            for j in jobs.values()
        ],
    }


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup scrapers on shutdown."""
    global _tiktok_scraper, _instagram_scraper

    if _tiktok_scraper:
        await _tiktok_scraper.close()
    if _instagram_scraper:
        await _instagram_scraper.close()


# For running directly
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.server:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
