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

    # ==================== Query Helpers ====================

    def _fetch_table(
        self,
        table_name: str,
        columns: str = "*",
        filters: Optional[dict] = None,
        limit: Optional[int] = None,
        order_by: Optional[str] = None,
        order_desc: bool = True,
    ) -> list[dict]:
        """
        Fetch rows from a table with optional filtering, ordering, and limits.

        Args:
            table_name: Name of the table or view
            columns: Columns to select (default "*")
            filters: Dict of column -> value for equality filters
            limit: Maximum rows to return
            order_by: Column to order by
            order_desc: Whether to order descending (default True)

        Returns:
            List of matching rows, or empty list if none found
        """
        query = self.client.table(table_name).select(columns)

        if filters:
            for column, value in filters.items():
                query = query.eq(column, value)

        if order_by:
            query = query.order(order_by, desc=order_desc)

        if limit:
            query = query.limit(limit)

        result = query.execute()
        return result.data if result.data else []

    def _fetch_one(
        self,
        table_name: str,
        columns: str = "*",
        filters: Optional[dict] = None,
    ) -> Optional[dict]:
        """
        Fetch a single row from a table.

        Args:
            table_name: Name of the table or view
            columns: Columns to select (default "*")
            filters: Dict of column -> value for equality filters

        Returns:
            First matching row, or None if not found
        """
        rows = self._fetch_table(table_name, columns, filters, limit=1)
        return rows[0] if rows else None

    def store_post(
        self,
        video_info: VideoInfo,
        download_result: Optional[DownloadResult] = None,
        analysis: Optional[VideoAnalysis] = None,
        niche: Optional[str] = None,
        source_hashtag: Optional[str] = None,
        niche_mode: Optional[str] = None,
    ) -> dict:
        """
        Store a post with optional download and analysis data.

        Args:
            niche: Business vertical (e.g., 'dj_nightlife', 'bars_restaurants')
            niche_mode: Analysis mode ('entertainment', 'data_engineering', 'both')

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
        # Set niche_mode (defaults to global setting if not specified)
        data["niche_mode"] = niche_mode or settings.niche_mode

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
        niche_mode: Optional[str] = None,
    ) -> int:
        """
        Store multiple posts at once.

        Args:
            niche: Business vertical (e.g., 'dj_nightlife', 'bars_restaurants')
            niche_mode: Analysis mode ('entertainment', 'data_engineering', 'both')

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
                self.store_post(
                    video, download, analysis,
                    niche=niche, source_hashtag=source_hashtag, niche_mode=niche_mode
                )
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
        niche_mode: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict]:
        """Get recent posts, optionally filtered by platform, hashtag, or niche_mode."""
        query = self.client.table("posts").select("*").order("scraped_at", desc=True).limit(limit)

        if platform:
            query = query.eq("platform", platform)
        if hashtag:
            query = query.contains("hashtags", [hashtag])
        if niche_mode:
            query = query.eq("niche_mode", niche_mode)

        result = query.execute()
        return result.data

    def get_unanalyzed_posts(
        self,
        limit: int = 20,
        niche_mode: Optional[str] = None,
    ) -> list[dict]:
        """Get posts that haven't been analyzed yet, optionally filtered by niche_mode."""
        query = (
            self.client.table("posts")
            .select("*")
            .is_("analyzed_at", "null")
            .not_.is_("local_file_path", "null")
            .order("scraped_at", desc=True)
            .limit(limit)
        )
        if niche_mode:
            query = query.eq("niche_mode", niche_mode)
        result = query.execute()
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

    def get_analytics_summary(self, niche_mode: Optional[str] = None) -> dict:
        """
        Get analytics summary for a specific niche_mode.

        Args:
            niche_mode: 'entertainment', 'data_engineering', or None for entertainment (default view)

        Returns summary stats for the specified niche.
        """
        if niche_mode == "data_engineering":
            # Use data engineering summary view
            result = self.client.table("data_engineering_summary").select("*").execute()
        else:
            # Default to entertainment view (analytics_summary is filtered to entertainment)
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
        return self._fetch_table("niche_analytics")

    def get_hashtag_performance(self, niche: Optional[str] = None) -> list[dict]:
        """Get hashtag performance, optionally filtered by niche."""
        filters = {"niche": niche} if niche else None
        return self._fetch_table("hashtag_performance", filters=filters)

    def get_hook_trends(self, limit: int = 20) -> list[dict]:
        """Get hook type and technique distribution."""
        return self._fetch_table("hook_trends", limit=limit)

    def get_audio_trends(self, limit: int = 20) -> list[dict]:
        """Get audio/sound category distribution."""
        return self._fetch_table("audio_trends", limit=limit)

    def get_visual_trends(self, limit: int = 20) -> list[dict]:
        """Get visual style and setting distribution."""
        return self._fetch_table("visual_trends", limit=limit)

    def get_viral_trends(self, limit: int = 20) -> list[dict]:
        """Get viral potential score distribution."""
        return self._fetch_table("viral_trends", limit=limit)

    def get_viral_factors(self, limit: int = 20) -> list[dict]:
        """Get top viral factors across all videos."""
        return self._fetch_table("viral_factors_breakdown", limit=limit)

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
        niche_mode: Optional[str] = None,
    ) -> list[dict]:
        """Get raw analyzed posts for custom aggregation, optionally filtered by niche_mode."""
        query = (
            self.client.table("posts")
            .select("id, platform, platform_id, video_url, author_username, analysis, scraped_at, niche_mode")
            .not_.is_("analysis", "null")
            .order("scraped_at", desc=True)
        )
        if platform:
            query = query.eq("platform", platform)
        if niche_mode:
            query = query.eq("niche_mode", niche_mode)

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

    # ==================== Account Methods ====================

    def create_account(self, platform: str, username: str) -> dict:
        """Create a new account to track. Returns the created account."""
        data = {
            "platform": platform,
            "username": username.lstrip("@"),
            "status": "pending",
        }
        result = (
            self.client.table("accounts")
            .upsert(data, on_conflict="platform,username")
            .execute()
        )
        logger.info(f"Created account: {platform}/{username}")
        return result.data[0] if result.data else {}

    def get_account(self, account_id: str) -> Optional[dict]:
        """Get account by ID."""
        return self._fetch_one("accounts", filters={"id": account_id})

    def get_account_by_username(self, platform: str, username: str) -> Optional[dict]:
        """Get account by platform and username."""
        return self._fetch_one(
            "accounts",
            filters={"platform": platform, "username": username.lstrip("@")}
        )

    def list_accounts(self) -> list[dict]:
        """List all tracked accounts."""
        return self._fetch_table("account_summary", order_by="created_at")

    def update_account(
        self,
        account_id: str,
        display_name: Optional[str] = None,
        bio: Optional[str] = None,
        profile_picture_url: Optional[str] = None,
        follower_count: Optional[int] = None,
        following_count: Optional[int] = None,
        post_count: Optional[int] = None,
        is_verified: Optional[bool] = None,
        is_private: Optional[bool] = None,
        status: Optional[str] = None,
        scrape_error: Optional[str] = None,
    ) -> dict:
        """Update account fields."""
        data = {"updated_at": datetime.utcnow().isoformat()}

        if display_name is not None:
            data["display_name"] = display_name
        if bio is not None:
            data["bio"] = bio
        if profile_picture_url is not None:
            data["profile_picture_url"] = profile_picture_url
        if follower_count is not None:
            data["follower_count"] = follower_count
        if following_count is not None:
            data["following_count"] = following_count
        if post_count is not None:
            data["post_count"] = post_count
        if is_verified is not None:
            data["is_verified"] = is_verified
        if is_private is not None:
            data["is_private"] = is_private
        if status is not None:
            data["status"] = status
            if status == "active":
                data["last_scraped_at"] = datetime.utcnow().isoformat()
        if scrape_error is not None:
            data["scrape_error"] = scrape_error

        result = (
            self.client.table("accounts")
            .update(data)
            .eq("id", account_id)
            .execute()
        )
        logger.debug(f"Updated account {account_id}")
        return result.data[0] if result.data else {}

    def delete_account(self, account_id: str) -> bool:
        """Delete an account (cascades to snapshots, nullifies posts)."""
        try:
            self.client.table("accounts").delete().eq("id", account_id).execute()
            logger.info(f"Deleted account: {account_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete account {account_id}: {e}")
            return False

    def link_posts_to_account(self, account_id: str, author_username: str) -> int:
        """Link existing posts by author to an account. Returns count linked."""
        result = (
            self.client.table("posts")
            .update({"account_id": account_id})
            .eq("author_username", author_username)
            .is_("account_id", "null")
            .execute()
        )
        count = len(result.data) if result.data else 0
        logger.info(f"Linked {count} posts to account {account_id}")
        return count

    def get_account_posts(self, account_id: str, limit: int = 100) -> list[dict]:
        """Get all posts for an account."""
        return self._fetch_table(
            "posts",
            filters={"account_id": account_id},
            order_by="scraped_at",
            limit=limit
        )

    def create_account_snapshot(
        self,
        account_id: str,
        video_count: int = 0,
        analyzed_count: int = 0,
        avg_hook_strength: Optional[float] = None,
        avg_viral_potential: Optional[float] = None,
        avg_replicability: Optional[float] = None,
        hook_types: Optional[dict] = None,
        audio_categories: Optional[dict] = None,
        visual_styles: Optional[dict] = None,
        dataset_comparison: Optional[dict] = None,
        percentile_ranks: Optional[dict] = None,
        recommendations: Optional[list] = None,
        gaps: Optional[list] = None,
    ) -> dict:
        """Create a snapshot of account metrics at this point in time."""
        data = {
            "account_id": account_id,
            "video_count": video_count,
            "analyzed_count": analyzed_count,
        }

        if avg_hook_strength is not None:
            data["avg_hook_strength"] = avg_hook_strength
        if avg_viral_potential is not None:
            data["avg_viral_potential"] = avg_viral_potential
        if avg_replicability is not None:
            data["avg_replicability"] = avg_replicability
        if hook_types is not None:
            data["hook_types"] = hook_types
        if audio_categories is not None:
            data["audio_categories"] = audio_categories
        if visual_styles is not None:
            data["visual_styles"] = visual_styles
        if dataset_comparison is not None:
            data["dataset_comparison"] = dataset_comparison
        if percentile_ranks is not None:
            data["percentile_ranks"] = percentile_ranks
        if recommendations is not None:
            data["recommendations"] = recommendations
        if gaps is not None:
            data["gaps"] = gaps

        result = self.client.table("account_snapshots").insert(data).execute()
        logger.info(f"Created snapshot for account {account_id}")
        return result.data[0] if result.data else {}

    def get_account_snapshots(self, account_id: str, limit: int = 10) -> list[dict]:
        """Get historical snapshots for an account."""
        return self._fetch_table(
            "account_snapshots",
            filters={"account_id": account_id},
            order_by="snapshot_at",
            limit=limit
        )

    def get_account_comparison(self, account_id: str) -> Optional[dict]:
        """Get account comparison vs dataset from the view."""
        return self._fetch_one("account_vs_dataset", filters={"account_id": account_id})

    def get_dataset_averages(self, niche_mode: Optional[str] = None) -> dict:
        """
        Get dataset averages for comparison, optionally filtered by niche_mode.

        Args:
            niche_mode: 'entertainment', 'data_engineering', or None for all data

        Returns different metrics based on niche_mode:
            - entertainment: hook, viral, replicability
            - data_engineering: clarity, depth, edu_value, practical
        """
        query = (
            self.client.table("posts")
            .select("analysis, niche_mode")
            .not_.is_("analysis", "null")
        )
        if niche_mode:
            query = query.eq("niche_mode", niche_mode)

        result = query.execute()

        if not result.data:
            if niche_mode == "data_engineering":
                return {"clarity": 0, "depth": 0, "edu_value": 0, "practical": 0, "count": 0}
            return {"hook": 0, "viral": 0, "replicability": 0, "count": 0}

        if niche_mode == "data_engineering":
            # Data engineering metrics
            clarities = []
            depths = []
            edu_values = []
            practicals = []

            for post in result.data:
                analysis = post.get("analysis", {})
                if analysis:
                    edu = analysis.get("educational", {})
                    if edu.get("explanation_clarity") is not None:
                        clarities.append(float(edu["explanation_clarity"]))
                    if edu.get("technical_depth") is not None:
                        depths.append(float(edu["technical_depth"]))
                    if edu.get("educational_value") is not None:
                        edu_values.append(float(edu["educational_value"]))
                    if edu.get("practical_applicability") is not None:
                        practicals.append(float(edu["practical_applicability"]))

            return {
                "clarity": sum(clarities) / len(clarities) if clarities else 0,
                "depth": sum(depths) / len(depths) if depths else 0,
                "edu_value": sum(edu_values) / len(edu_values) if edu_values else 0,
                "practical": sum(practicals) / len(practicals) if practicals else 0,
                "count": len(result.data),
            }
        else:
            # Entertainment metrics (default)
            hooks = []
            virals = []
            replicabilities = []

            for post in result.data:
                analysis = post.get("analysis", {})
                if analysis:
                    hook_val = analysis.get("hook", {}).get("hook_strength")
                    viral_val = analysis.get("trends", {}).get("viral_potential_score")
                    replicate_val = analysis.get("replicability", {}).get("replicability_score")

                    if hook_val is not None:
                        hooks.append(float(hook_val))
                    if viral_val is not None:
                        virals.append(float(viral_val))
                    if replicate_val is not None:
                        replicabilities.append(float(replicate_val))

            return {
                "hook": sum(hooks) / len(hooks) if hooks else 0,
                "viral": sum(virals) / len(virals) if virals else 0,
                "replicability": sum(replicabilities) / len(replicabilities) if replicabilities else 0,
                "count": len(result.data),
            }
