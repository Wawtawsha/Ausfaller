"""
Supabase storage client for social scraper.

Handles storing posts, analyses, and job tracking.
"""

from datetime import datetime
from typing import Optional
from pathlib import Path
import logging

from supabase import create_client, Client

from config.settings import settings
from src.extractor import VideoInfo, ExtractionResult
from src.downloader.video import DownloadResult
from src.analyzer.gemini import VideoAnalysis

logger = logging.getLogger(__name__)


class SupabaseStorage:
    """Storage client for Supabase."""

    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        self.url = url or settings.supabase_url
        self.key = key or settings.supabase_key

        if not self.url or not self.key:
            raise ValueError(
                "Supabase credentials required. Set SUPABASE_URL and SUPABASE_KEY in .env"
            )

        self.client: Client = create_client(self.url, self.key)

    def store_post(
        self,
        video_info: VideoInfo,
        download_result: Optional[DownloadResult] = None,
        analysis: Optional[VideoAnalysis] = None,
        niche: Optional[str] = None,
        source_hashtag: Optional[str] = None,
    ) -> dict:
        """
        Store a post with optional download and analysis data.

        Returns the inserted/updated record.
        """
        data = {
            "platform": video_info.platform.value,
            "platform_id": video_info.video_id,
            "video_url": video_info.video_url,
            "author_username": video_info.author_username,
            "content_type": "video",
            "likes": video_info.likes,
            "comments": video_info.comments,
            "shares": video_info.shares,
            "scraped_at": datetime.utcnow().isoformat(),
        }

        # Add niche tracking
        if niche:
            data["niche"] = niche
        if source_hashtag:
            data["source_hashtag"] = source_hashtag

        if download_result and download_result.success:
            data["local_file_path"] = str(download_result.file_path)
            data["file_size_bytes"] = download_result.file_size_bytes
            data["duration_seconds"] = download_result.duration_seconds
            if download_result.title:
                data["caption"] = download_result.title

            # Extract engagement from yt-dlp metadata (more accurate than hashtag grid)
            if download_result.metadata:
                meta = download_result.metadata
                if meta.get("view_count"):
                    data["views"] = meta["view_count"]
                if meta.get("like_count"):
                    data["likes"] = meta["like_count"]
                if meta.get("comment_count"):
                    data["comments"] = meta["comment_count"]
                if meta.get("repost_count"):
                    data["shares"] = meta["repost_count"]
                # Extract upload timestamp for time-weighted metrics
                if meta.get("timestamp"):
                    data["posted_at"] = datetime.utcfromtimestamp(meta["timestamp"]).isoformat()

        if analysis and analysis.success:
            data["analysis"] = analysis.to_dict()
            data["analyzed_at"] = datetime.utcnow().isoformat()

        result = (
            self.client.table("posts")
            .upsert(data, on_conflict="platform,platform_id")
            .execute()
        )

        logger.info(f"Stored post: {video_info.platform.value}/{video_info.video_id}")
        return result.data[0] if result.data else {}

    def store_batch(
        self,
        videos: list[VideoInfo],
        downloads: Optional[list[DownloadResult]] = None,
        analyses: Optional[list[VideoAnalysis]] = None,
        niche: Optional[str] = None,
        source_hashtag: Optional[str] = None,
    ) -> int:
        """
        Store multiple posts at once.

        Returns count of stored posts.
        """
        downloads_map = {}
        if downloads:
            for d in downloads:
                if d.success and d.file_path:
                    downloads_map[d.video_url] = d

        analyses_map = {}
        if analyses:
            for a in analyses:
                if a.success and a.video_path:
                    analyses_map[a.video_path] = a

        stored = 0
        for video in videos:
            download = downloads_map.get(video.video_url)
            analysis = None
            if download and download.file_path:
                analysis = analyses_map.get(str(download.file_path))

            try:
                self.store_post(video, download, analysis, niche=niche, source_hashtag=source_hashtag)
                stored += 1
            except Exception as e:
                logger.error(f"Failed to store post {video.video_id}: {e}")

        return stored

    def create_job(
        self,
        platform: str,
        hashtag: str,
        target_count: int,
        client_id: Optional[str] = None,
    ) -> str:
        """Create a new scrape job. Returns job ID."""
        data = {
            "platform": platform,
            "hashtag": hashtag,
            "target_count": target_count,
            "status": "pending",
        }
        if client_id:
            data["client_id"] = client_id

        result = self.client.table("scrape_jobs").insert(data).execute()
        job_id = result.data[0]["id"]
        logger.info(f"Created job: {job_id}")
        return job_id

    def update_job(
        self,
        job_id: str,
        status: Optional[str] = None,
        videos_found: Optional[int] = None,
        videos_downloaded: Optional[int] = None,
        videos_analyzed: Optional[int] = None,
        error: Optional[str] = None,
    ) -> None:
        """Update job status and metrics."""
        data = {}
        if status:
            data["status"] = status
            if status == "running":
                data["started_at"] = datetime.utcnow().isoformat()
            elif status in ["completed", "failed"]:
                data["completed_at"] = datetime.utcnow().isoformat()
        if videos_found is not None:
            data["videos_found"] = videos_found
        if videos_downloaded is not None:
            data["videos_downloaded"] = videos_downloaded
        if videos_analyzed is not None:
            data["videos_analyzed"] = videos_analyzed
        if error:
            data["error"] = error

        if data:
            self.client.table("scrape_jobs").update(data).eq("id", job_id).execute()
            logger.debug(f"Updated job {job_id}: {data}")

    def get_recent_posts(
        self,
        platform: Optional[str] = None,
        hashtag: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Get recent posts, optionally filtered."""
        query = self.client.table("posts").select("*").order("scraped_at", desc=True).limit(limit)

        if platform:
            query = query.eq("platform", platform)
        if hashtag:
            query = query.contains("hashtags", [hashtag])

        result = query.execute()
        return result.data

    def get_unanalyzed_posts(self, limit: int = 20) -> list[dict]:
        """Get posts that haven't been analyzed yet."""
        result = (
            self.client.table("posts")
            .select("*")
            .is_("analyzed_at", "null")
            .not_.is_("local_file_path", "null")
            .order("scraped_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data

    def update_post_analysis(self, post_id: str, analysis: VideoAnalysis) -> None:
        """Update a post with analysis results."""
        data = {
            "analysis": analysis.to_dict(),
            "analyzed_at": datetime.utcnow().isoformat(),
        }
        self.client.table("posts").update(data).eq("id", post_id).execute()
        logger.debug(f"Updated analysis for post {post_id}")

    def upsert_trend(
        self,
        platform: str,
        trend_type: str,
        name: str,
        post_count: int,
        avg_engagement: Optional[float] = None,
    ) -> None:
        """Insert or update a trend."""
        data = {
            "platform": platform,
            "trend_type": trend_type,
            "name": name,
            "post_count": post_count,
            "last_seen": datetime.utcnow().isoformat(),
        }
        if avg_engagement:
            data["avg_engagement"] = avg_engagement

        self.client.table("trends").upsert(
            data, on_conflict="platform,trend_type,name"
        ).execute()

    # ==================== Analytics Methods ====================

    def get_analytics_summary(self) -> dict:
        """Get overall analytics summary."""
        result = self.client.table("analytics_summary").select("*").execute()
        if result.data:
            return result.data[0]
        return {}

    def get_total_video_bytes(self) -> int:
        """Get total bytes of all downloaded videos."""
        try:
            result = (
                self.client.table("posts")
                .select("file_size_bytes")
                .not_.is_("file_size_bytes", "null")
                .execute()
            )
            total = sum(row.get("file_size_bytes", 0) or 0 for row in result.data)
            return total
        except Exception as e:
            logger.error(f"Error getting total video bytes: {e}")
            return 0

    def get_niche_analytics(self) -> list[dict]:
        """Get analytics grouped by niche."""
        result = self.client.table("niche_analytics").select("*").execute()
        return result.data

    def get_hashtag_performance(self, niche: Optional[str] = None) -> list[dict]:
        """Get hashtag performance, optionally filtered by niche."""
        query = self.client.table("hashtag_performance").select("*")
        if niche:
            query = query.eq("niche", niche)
        result = query.execute()
        return result.data

    def get_hook_trends(self, limit: int = 20) -> list[dict]:
        """Get hook type and technique distribution."""
        result = (
            self.client.table("hook_trends")
            .select("*")
            .limit(limit)
            .execute()
        )
        return result.data

    def get_audio_trends(self, limit: int = 20) -> list[dict]:
        """Get audio/sound category distribution."""
        result = (
            self.client.table("audio_trends")
            .select("*")
            .limit(limit)
            .execute()
        )
        return result.data

    def get_visual_trends(self, limit: int = 20) -> list[dict]:
        """Get visual style and setting distribution."""
        result = (
            self.client.table("visual_trends")
            .select("*")
            .limit(limit)
            .execute()
        )
        return result.data

    def get_viral_trends(self, limit: int = 20) -> list[dict]:
        """Get viral potential score distribution."""
        result = (
            self.client.table("viral_trends")
            .select("*")
            .limit(limit)
            .execute()
        )
        return result.data

    def get_viral_factors(self, limit: int = 20) -> list[dict]:
        """Get top viral factors across all videos."""
        result = (
            self.client.table("viral_factors_breakdown")
            .select("*")
            .limit(limit)
            .execute()
        )
        return result.data

    def get_replicability_leaderboard(
        self,
        min_score: int = 6,
        difficulty: Optional[str] = None,
        limit: int = 20,
    ) -> list[dict]:
        """Get top videos by replicability score."""
        query = (
            self.client.table("replicability_leaderboard")
            .select("*")
            .gte("replicability_score", min_score)
        )
        if difficulty:
            query = query.eq("difficulty", difficulty)

        result = query.limit(limit).execute()
        return result.data

    def get_analyzed_posts_raw(
        self,
        limit: int = 100,
        platform: Optional[str] = None,
    ) -> list[dict]:
        """Get raw analyzed posts for custom aggregation."""
        query = (
            self.client.table("posts")
            .select("id, platform, platform_id, video_url, author_username, analysis, scraped_at")
            .not_.is_("analysis", "null")
            .order("scraped_at", desc=True)
        )
        if platform:
            query = query.eq("platform", platform)

        result = query.limit(limit).execute()
        return result.data

    def get_most_recent_analysis(self) -> Optional[dict]:
        """Get the most recently analyzed post with full analysis data."""
        result = (
            self.client.table("posts")
            .select("id, platform, platform_id, video_url, author_username, caption, analysis, analyzed_at, scraped_at")
            .not_.is_("analysis", "null")
            .order("analyzed_at", desc=True)
            .limit(1)
            .execute()
        )
        if result.data:
            return result.data[0]
        return None

    def get_metric_trends(self, days: int = 7) -> dict:
        """
        Get metric trends - simplified version that just counts analyzed posts.
        """
        import json

        result = {
            "period_days": days,
            "recent_count": 0,
            "previous_count": 0,
            "hook_change": None,
            "viral_change": None,
            "replicate_change": None
        }

        try:
            # Simple count query
            count_result = (
                self.client.table("posts")
                .select("id", count="exact")
                .not_.is_("analysis", "null")
                .execute()
            )

            total_analyzed = count_result.count if count_result.count else 0
            result["recent_count"] = total_analyzed
            result["debug"] = {"total_analyzed": total_analyzed}

        except Exception as e:
            logger.error(f"Error in get_metric_trends: {e}", exc_info=True)
            result["error"] = str(e)

        return result
