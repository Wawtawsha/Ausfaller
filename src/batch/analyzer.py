"""
Batch analyzer for processing many videos with Gemini.

Implements rate-limited batch analysis to handle large volumes efficiently.
For true 50% cost savings, would need Vertex AI Batch Prediction API.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class BatchAnalysisResult:
    """Result of batch analysis job."""
    batch_id: str
    total: int
    analyzed: int
    failed: int
    results_file: Optional[Path] = None
    error: Optional[str] = None


class BatchAnalyzer:
    """
    Analyzes videos in batches with rate limiting.

    Rate limits for Gemini 2.0 Flash:
    - 10 RPM (requests per minute) for free tier
    - 1000 RPM for paid tier

    We use conservative rate limiting to avoid quota errors.
    """

    def __init__(
        self,
        requests_per_minute: int = 30,
        output_dir: Optional[Path] = None,
    ):
        self.rpm = requests_per_minute
        self.delay_between_requests = 60.0 / requests_per_minute
        self.output_dir = output_dir or Path(settings.cache_dir) / "batch"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def analyze_batch(
        self,
        items: list[dict],
        batch_id: str,
        niche_mode: str = "data_engineering",
        save_incrementally: bool = True,
    ) -> BatchAnalysisResult:
        """
        Analyze a batch of videos with rate limiting.

        Args:
            items: List of items with file_path for videos
            batch_id: Unique batch identifier
            niche_mode: Niche for analysis prompt
            save_incrementally: Save results after each analysis

        Returns:
            BatchAnalysisResult with summary and results file path
        """
        from src.analyzer.gemini import GeminiAnalyzer

        analyzer = GeminiAnalyzer(niche_mode=niche_mode)

        results = []
        analyzed = 0
        failed = 0

        # Filter to items with video files
        video_items = [
            item for item in items
            if item.get("file_path") and item.get("download_success")
        ]

        total = len(video_items)
        logger.info(f"Starting batch analysis of {total} videos (rate: {self.rpm} RPM)")

        results_file = self.output_dir / f"{batch_id}_results.jsonl"

        for i, item in enumerate(video_items):
            file_path = Path(item["file_path"])

            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                item["analysis"] = None
                item["analysis_error"] = "File not found"
                failed += 1
                continue

            try:
                logger.info(f"Analyzing {i+1}/{total}: {file_path.name}")

                analysis = await analyzer.analyze_video(file_path)

                if analysis.success:
                    item["analysis"] = analysis.to_dict()
                    item["analysis_error"] = None
                    analyzed += 1
                else:
                    item["analysis"] = None
                    item["analysis_error"] = analysis.error
                    failed += 1

            except Exception as e:
                logger.error(f"Analysis failed for {file_path}: {e}")
                item["analysis"] = None
                item["analysis_error"] = str(e)
                failed += 1

            results.append(item)

            # Save incrementally
            if save_incrementally:
                with open(results_file, "a") as f:
                    f.write(json.dumps(item) + "\n")

            # Rate limiting
            if i < total - 1:  # Don't delay after last item
                await asyncio.sleep(self.delay_between_requests)

            # Progress update every 10 items
            if (i + 1) % 10 == 0:
                logger.info(f"Progress: {i+1}/{total} ({analyzed} analyzed, {failed} failed)")

        logger.info(f"Batch analysis complete: {analyzed}/{total} analyzed, {failed} failed")

        return BatchAnalysisResult(
            batch_id=batch_id,
            total=total,
            analyzed=analyzed,
            failed=failed,
            results_file=results_file,
        )

    async def analyze_with_concurrency(
        self,
        items: list[dict],
        batch_id: str,
        max_concurrent: int = 3,
        niche_mode: str = "data_engineering",
    ) -> BatchAnalysisResult:
        """
        Analyze videos with controlled concurrency.

        Faster than sequential but respects rate limits.
        """
        from src.analyzer.gemini import GeminiAnalyzer

        analyzer = GeminiAnalyzer(niche_mode=niche_mode)
        semaphore = asyncio.Semaphore(max_concurrent)

        video_items = [
            item for item in items
            if item.get("file_path") and item.get("download_success")
        ]

        total = len(video_items)
        analyzed = 0
        failed = 0

        results_file = self.output_dir / f"{batch_id}_results.jsonl"
        results_lock = asyncio.Lock()

        async def analyze_one(item: dict, index: int) -> dict:
            nonlocal analyzed, failed

            async with semaphore:
                file_path = Path(item["file_path"])

                if not file_path.exists():
                    item["analysis"] = None
                    item["analysis_error"] = "File not found"
                    failed += 1
                    return item

                try:
                    logger.info(f"Analyzing {index+1}/{total}: {file_path.name}")

                    analysis = await analyzer.analyze_video(file_path)

                    if analysis.success:
                        item["analysis"] = analysis.to_dict()
                        item["analysis_error"] = None
                        analyzed += 1
                    else:
                        item["analysis"] = None
                        item["analysis_error"] = analysis.error
                        failed += 1

                except Exception as e:
                    logger.error(f"Analysis failed for {file_path}: {e}")
                    item["analysis"] = None
                    item["analysis_error"] = str(e)
                    failed += 1

                # Save result
                async with results_lock:
                    with open(results_file, "a") as f:
                        f.write(json.dumps(item) + "\n")

                # Rate limit delay
                await asyncio.sleep(self.delay_between_requests)

                return item

        logger.info(f"Starting concurrent batch analysis of {total} videos")

        results = await asyncio.gather(
            *[analyze_one(item, i) for i, item in enumerate(video_items)],
            return_exceptions=True,
        )

        # Count exceptions as failures
        for r in results:
            if isinstance(r, Exception):
                failed += 1

        logger.info(f"Batch analysis complete: {analyzed}/{total} analyzed, {failed} failed")

        return BatchAnalysisResult(
            batch_id=batch_id,
            total=total,
            analyzed=analyzed,
            failed=failed,
            results_file=results_file,
        )

    def load_results(self, batch_id: str) -> list[dict]:
        """Load results from a batch analysis."""
        results_file = self.output_dir / f"{batch_id}_results.jsonl"

        if not results_file.exists():
            raise FileNotFoundError(f"Results not found: {results_file}")

        results = []
        with open(results_file) as f:
            for line in f:
                if line.strip():
                    results.append(json.loads(line))

        return results

    def get_analysis_summary(self, results: list[dict]) -> dict:
        """Get summary statistics from analysis results."""
        total = len(results)
        analyzed = sum(1 for r in results if r.get("analysis"))
        failed = total - analyzed

        # Aggregate by source
        by_source = {}
        for r in results:
            source = r.get("source", "unknown")
            if source not in by_source:
                by_source[source] = {"count": 0, "analyzed": 0}
            by_source[source]["count"] += 1
            if r.get("analysis"):
                by_source[source]["analyzed"] += 1

        # Get analysis metrics if available
        hook_strengths = []
        educational_values = []
        brand_safety_scores = []

        for r in results:
            analysis = r.get("analysis")
            if analysis:
                if analysis.get("hook", {}).get("hook_strength"):
                    hook_strengths.append(analysis["hook"]["hook_strength"])
                if analysis.get("educational", {}).get("educational_value"):
                    educational_values.append(analysis["educational"]["educational_value"])
                if analysis.get("brand_safety", {}).get("brand_safety_score"):
                    brand_safety_scores.append(analysis["brand_safety"]["brand_safety_score"])

        return {
            "total": total,
            "analyzed": analyzed,
            "failed": failed,
            "by_source": by_source,
            "avg_hook_strength": sum(hook_strengths) / len(hook_strengths) if hook_strengths else 0,
            "avg_educational_value": sum(educational_values) / len(educational_values) if educational_values else 0,
            "avg_brand_safety": sum(brand_safety_scores) / len(brand_safety_scores) if brand_safety_scores else 0,
        }
