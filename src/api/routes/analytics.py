"""Analytics endpoints for social media data analysis."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException

from src.storage import SupabaseStorage
from config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter()


def get_storage() -> Optional[SupabaseStorage]:
    """Get Supabase storage client (returns None if not configured)."""
    if not settings.supabase_url or not settings.supabase_key:
        return None
    try:
        return SupabaseStorage(
            url=settings.supabase_url,
            key=settings.supabase_key
        )
    except Exception as e:
        logger.warning(f"Failed to initialize Supabase: {e}")
        return None


# ==================== Core Analytics ====================


@router.get("/summary")
async def get_analytics_summary(niche_mode: Optional[str] = None):
    """
    Get analytics summary for a specific niche_mode.

    Args:
        niche_mode: 'entertainment', 'data_engineering', or None (defaults to entertainment)

    Returns different metrics based on niche_mode.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        summary = storage.get_analytics_summary(niche_mode=niche_mode)
        return summary
    except Exception as e:
        logger.error(f"Failed to get analytics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all")
async def get_all_analytics(niche_mode: Optional[str] = None):
    """
    Get all analytics data in one request.

    Args:
        niche_mode: 'entertainment', 'data_engineering', or None (defaults to entertainment)

    Combines summary, hooks, audio, visual, viral, and replicability data.
    Ideal for dashboard rendering.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        summary = storage.get_analytics_summary(niche_mode=niche_mode)
        summary["total_video_bytes"] = storage.get_total_video_bytes()
        summary["niche_mode"] = niche_mode or "entertainment"

        if niche_mode == "data_engineering":
            return {
                "summary": summary,
                "dataset_averages": storage.get_dataset_averages(niche_mode="data_engineering"),
            }
        else:
            return {
                "summary": summary,
                "hooks": storage.get_hook_trends(limit=10),
                "audio": storage.get_audio_trends(limit=10),
                "visual": storage.get_visual_trends(limit=10),
                "viral_factors": storage.get_viral_factors(limit=10),
                "top_replicable": storage.get_replicability_leaderboard(min_score=7, limit=10),
            }
    except Exception as e:
        logger.error(f"Failed to get all analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Trend Analytics ====================


@router.get("/hooks")
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


@router.get("/audio")
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


@router.get("/visual")
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


@router.get("/viral")
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


@router.get("/trends")
async def get_metric_trends(days: int = 7):
    """
    Get metric trend changes over time.

    Compares averages from recent period vs previous period.
    Returns positive values for improvements, negative for declines.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        trends = storage.get_metric_trends(days=days)
        return trends
    except Exception as e:
        logger.error(f"Failed to get metric trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Format & Niche Analytics ====================


@router.get("/format")
async def get_format_analytics():
    """
    Get content format distribution (video lengths, aspect ratios, etc.).
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        # This endpoint appears to call a method that may not exist
        # Keeping the pattern consistent with existing code
        result = storage.get_format_analytics() if hasattr(storage, 'get_format_analytics') else {}
        return {"format_analytics": result}
    except Exception as e:
        logger.error(f"Failed to get format analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/niche")
async def get_niche_analytics():
    """
    Get analytics grouped by niche.

    Shows video counts, analyzed counts, and average scores per niche.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        niches = storage.get_niche_analytics()
        return {"niche_analytics": niches}
    except Exception as e:
        logger.error(f"Failed to get niche analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hashtag-performance")
async def get_hashtag_performance(niche: Optional[str] = None):
    """
    Get hashtag performance metrics, optionally filtered by niche.

    Shows which hashtags produced the best content per niche.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        performance = storage.get_hashtag_performance(niche=niche)
        return {"hashtag_performance": performance}
    except Exception as e:
        logger.error(f"Failed to get hashtag performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Content Quality Analytics ====================


@router.get("/replicability")
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


@router.get("/production")
async def get_production_analytics():
    """
    Get production quality metrics distribution.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        result = storage.get_production_analytics() if hasattr(storage, 'get_production_analytics') else {}
        return {"production_analytics": result}
    except Exception as e:
        logger.error(f"Failed to get production analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/brand-safety")
async def get_brand_safety_analytics():
    """
    Get brand safety metrics and content flagging breakdown.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        result = storage.get_brand_safety_analytics() if hasattr(storage, 'get_brand_safety_analytics') else {}
        return {"brand_safety_analytics": result}
    except Exception as e:
        logger.error(f"Failed to get brand safety analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dataset/averages")
async def get_dataset_averages(niche_mode: Optional[str] = None):
    """
    Get dataset-wide average scores.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        averages = storage.get_dataset_averages(niche_mode=niche_mode)
        return {"dataset_averages": averages}
    except Exception as e:
        logger.error(f"Failed to get dataset averages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/viral-factors")
async def get_viral_factors(limit: int = 20):
    """
    Get top viral factors across analyzed content.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        factors = storage.get_viral_factors(limit=limit)
        return {"viral_factors": factors}
    except Exception as e:
        logger.error(f"Failed to get viral factors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Raw Data Endpoints ====================


@router.get("/raw-posts")
async def get_raw_posts(limit: int = 500, niche_mode: Optional[str] = None):
    """
    Get raw analyzed posts for cross-chart filtering.

    Args:
        niche_mode: 'entertainment', 'data_engineering', or None for all

    Returns posts with full analysis data for client-side aggregation.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        posts = storage.get_analyzed_posts_raw(limit=limit, niche_mode=niche_mode)
        return {"posts": posts, "count": len(posts), "niche_mode": niche_mode}
    except Exception as e:
        logger.error(f"Failed to get raw posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent-reply")
async def get_recent_reply():
    """
    Get the most recent Gemini AI analysis reply.

    Returns the full analysis data for the most recently analyzed video.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        recent = storage.get_most_recent_analysis()
        if not recent:
            return {"recent_reply": None, "message": "No analyzed videos found"}
        return {"recent_reply": recent}
    except Exception as e:
        logger.error(f"Failed to get recent reply: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/strategic-analysis")
async def get_strategic_analysis(niche: Optional[str] = None):
    """
    Get the latest strategic trend analysis (markdown).

    Args:
        niche: 'data_engineering' or 'entertainment' - returns niche-specific analysis

    Returns the content of analysis/LATEST_ANALYSIS_{NICHE}.md if it exists,
    or falls back to analysis/LATEST_ANALYSIS.md for backwards compatibility.
    """
    if niche == "data_engineering":
        analysis_path = Path("analysis/LATEST_ANALYSIS_DATA_ENGINEERING.md")
    elif niche == "entertainment":
        analysis_path = Path("analysis/LATEST_ANALYSIS_ENTERTAINMENT.md")
    else:
        analysis_path = Path("analysis/LATEST_ANALYSIS.md")

    if not analysis_path.exists():
        analysis_path = Path("analysis/LATEST_ANALYSIS.md")

    if not analysis_path.exists():
        return {
            "content": None,
            "message": "No strategic analysis available yet",
            "updated_at": None,
            "niche": niche
        }

    try:
        content = analysis_path.read_text(encoding="utf-8")
        stat = analysis_path.stat()
        updated_at = datetime.fromtimestamp(stat.st_mtime).isoformat()

        return {
            "content": content,
            "updated_at": updated_at,
            "niche": niche,
            "file": analysis_path.name
        }
    except Exception as e:
        logger.error(f"Failed to read strategic analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Educational Analytics (Data Engineering) ====================


@router.get("/educational")
async def get_educational_analytics():
    """
    Get educational content analytics for data engineering niche.

    Returns clarity, depth, value metrics aggregated by niche and hashtag.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        result = storage.client.table("educational_metrics").select("*").execute()
        return {"metrics": result.data}
    except Exception as e:
        logger.error(f"Failed to get educational metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools")
async def get_tool_coverage():
    """
    Get tool coverage breakdown for data engineering content.

    Shows which tools (Fabric, ADF, Power BI, etc.) are most mentioned.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        result = storage.client.table("tool_coverage").select("*").execute()
        return {"tools": result.data}
    except Exception as e:
        logger.error(f"Failed to get tool coverage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/content-types")
async def get_content_type_distribution():
    """
    Get content type distribution (tutorial, demo, career advice, etc.).
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        result = storage.client.table("content_type_distribution").select("*").execute()
        return {"content_types": result.data}
    except Exception as e:
        logger.error(f"Failed to get content type distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/teaching-techniques")
async def get_teaching_techniques():
    """
    Get teaching technique effectiveness metrics.

    Shows which techniques (screen share, live coding, etc.) perform best.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        result = storage.client.table("teaching_techniques").select("*").execute()
        return {"techniques": result.data}
    except Exception as e:
        logger.error(f"Failed to get teaching techniques: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/skill-levels")
async def get_skill_level_distribution():
    """
    Get skill level distribution of analyzed content.
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        result = storage.client.table("skill_level_distribution").select("*").execute()
        return {"skill_levels": result.data}
    except Exception as e:
        logger.error(f"Failed to get skill level distribution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data-engineering-context")
async def get_data_engineering_context():
    """
    Get data engineering context breakdown (cloud platforms, data layers, patterns).
    """
    storage = get_storage()
    if not storage:
        raise HTTPException(status_code=503, detail="Supabase not configured")

    try:
        result = storage.client.table("data_engineering_context").select("*").execute()
        return {"context": result.data}
    except Exception as e:
        logger.error(f"Failed to get data engineering context: {e}")
        raise HTTPException(status_code=500, detail=str(e))
