"""
Account comparison and analysis logic.

Compares account metrics against the dataset to generate insights and recommendations.
"""

from typing import Optional
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class AccountComparer:
    """Compare account performance against the dataset."""

    def compare_scores(
        self,
        account_posts: list[dict],
        dataset_averages: dict,
        all_scores: Optional[dict] = None,
    ) -> dict:
        """
        Compare account scores against dataset.

        Args:
            account_posts: List of posts with analysis data
            dataset_averages: Dict with hook, viral, replicability averages
            all_scores: Optional dict of all scores for percentile calculation

        Returns:
            {
                "account_averages": {"hook": 7.2, "viral": 6.8, "replicability": 7.5},
                "vs_dataset": {"hook": +0.5, "viral": -0.2, "replicability": +0.8},
                "percentiles": {"hook": 72, "viral": 58, "replicability": 81},
                "video_count": 25,
                "analyzed_count": 20
            }
        """
        # Extract scores from account posts
        hooks = []
        virals = []
        replicabilities = []

        for post in account_posts:
            analysis = post.get("analysis", {})
            if not analysis:
                continue

            hook_val = analysis.get("hook", {}).get("hook_strength")
            viral_val = analysis.get("trends", {}).get("viral_potential_score")
            replicate_val = analysis.get("replicability", {}).get("replicability_score")

            if hook_val is not None:
                hooks.append(float(hook_val))
            if viral_val is not None:
                virals.append(float(viral_val))
            if replicate_val is not None:
                replicabilities.append(float(replicate_val))

        # Calculate account averages
        account_hook = sum(hooks) / len(hooks) if hooks else 0
        account_viral = sum(virals) / len(virals) if virals else 0
        account_replicate = sum(replicabilities) / len(replicabilities) if replicabilities else 0

        # Calculate differences vs dataset
        hook_diff = account_hook - dataset_averages.get("hook", 0)
        viral_diff = account_viral - dataset_averages.get("viral", 0)
        replicate_diff = account_replicate - dataset_averages.get("replicability", 0)

        # Calculate percentiles if we have all scores
        percentiles = {"hook": 50, "viral": 50, "replicability": 50}
        if all_scores:
            if all_scores.get("hooks") and account_hook > 0:
                percentiles["hook"] = self._calculate_percentile(account_hook, all_scores["hooks"])
            if all_scores.get("virals") and account_viral > 0:
                percentiles["viral"] = self._calculate_percentile(account_viral, all_scores["virals"])
            if all_scores.get("replicabilities") and account_replicate > 0:
                percentiles["replicability"] = self._calculate_percentile(
                    account_replicate, all_scores["replicabilities"]
                )

        return {
            "account_averages": {
                "hook": round(account_hook, 2),
                "viral": round(account_viral, 2),
                "replicability": round(account_replicate, 2),
            },
            "vs_dataset": {
                "hook": round(hook_diff, 2),
                "viral": round(viral_diff, 2),
                "replicability": round(replicate_diff, 2),
            },
            "percentiles": percentiles,
            "video_count": len(account_posts),
            "analyzed_count": len(hooks),
        }

    def _calculate_percentile(self, value: float, all_values: list[float]) -> int:
        """Calculate percentile rank of value within all_values."""
        if not all_values:
            return 50
        sorted_values = sorted(all_values)
        count_below = sum(1 for v in sorted_values if v < value)
        percentile = (count_below / len(sorted_values)) * 100
        return int(round(percentile))

    def analyze_patterns(
        self,
        account_posts: list[dict],
        dataset_posts: list[dict],
    ) -> dict:
        """
        Analyze content patterns and compare distributions.

        Returns:
            {
                "account_patterns": {
                    "hook_types": {"question": 5, "visual": 3},
                    "audio_categories": {"voiceover": 4, "trending_audio": 2},
                    "visual_styles": {"casual": 5, "polished": 2}
                },
                "dataset_patterns": {...},
                "pattern_comparison": {
                    "hook_types": {"question": +10%, "visual": -5%},
                    ...
                }
            }
        """
        account_patterns = self._extract_patterns(account_posts)
        dataset_patterns = self._extract_patterns(dataset_posts)

        # Compare pattern distributions
        pattern_comparison = {}

        for category in ["hook_types", "audio_categories", "visual_styles"]:
            account_dist = account_patterns.get(category, {})
            dataset_dist = dataset_patterns.get(category, {})

            # Normalize to percentages
            account_total = sum(account_dist.values()) or 1
            dataset_total = sum(dataset_dist.values()) or 1

            comparison = {}
            all_keys = set(account_dist.keys()) | set(dataset_dist.keys())

            for key in all_keys:
                account_pct = (account_dist.get(key, 0) / account_total) * 100
                dataset_pct = (dataset_dist.get(key, 0) / dataset_total) * 100
                comparison[key] = round(account_pct - dataset_pct, 1)

            pattern_comparison[category] = comparison

        return {
            "account_patterns": account_patterns,
            "dataset_patterns": dataset_patterns,
            "pattern_comparison": pattern_comparison,
        }

    def _extract_patterns(self, posts: list[dict]) -> dict:
        """Extract pattern distributions from posts."""
        hook_types = Counter()
        audio_categories = Counter()
        visual_styles = Counter()

        for post in posts:
            analysis = post.get("analysis", {})
            if not analysis:
                continue

            # Hook type
            hook = analysis.get("hook", {})
            if hook.get("hook_type"):
                hook_types[hook["hook_type"]] += 1

            # Audio
            audio = analysis.get("audio", {})
            if audio.get("audio_type"):
                audio_categories[audio["audio_type"]] += 1

            # Visual style
            visual = analysis.get("visual", {})
            if visual.get("visual_style"):
                visual_styles[visual["visual_style"]] += 1

        return {
            "hook_types": dict(hook_types),
            "audio_categories": dict(audio_categories),
            "visual_styles": dict(visual_styles),
        }

    def identify_gaps(
        self,
        account_patterns: dict,
        top_performer_patterns: dict,
        score_comparison: dict,
    ) -> list[str]:
        """
        Identify gaps between account and top performers.

        Returns list of gap descriptions.
        """
        gaps = []

        # Score-based gaps
        vs_dataset = score_comparison.get("vs_dataset", {})

        if vs_dataset.get("hook", 0) < -0.5:
            gaps.append("Hook strength is below average - opening seconds need more impact")
        if vs_dataset.get("viral", 0) < -0.5:
            gaps.append("Viral potential is below average - content may lack shareability factors")
        if vs_dataset.get("replicability", 0) < -0.5:
            gaps.append("Replicability score is low - format may be too complex or unique")

        # Pattern-based gaps
        account_hooks = account_patterns.get("hook_types", {})
        top_hooks = top_performer_patterns.get("hook_types", {})

        # Find top performer patterns not used by account
        for hook_type, count in top_hooks.items():
            if count > 3 and hook_type not in account_hooks:
                gaps.append(f"Not using '{hook_type}' hooks (popular in top performers)")

        account_audio = account_patterns.get("audio_categories", {})
        top_audio = top_performer_patterns.get("audio_categories", {})

        for audio_type, count in top_audio.items():
            if count > 3 and audio_type not in account_audio:
                gaps.append(f"Not leveraging '{audio_type}' audio strategy")

        return gaps[:5]  # Limit to top 5 gaps

    def generate_recommendations(
        self,
        score_comparison: dict,
        pattern_comparison: dict,
        gaps: list[str],
    ) -> list[str]:
        """
        Generate actionable recommendations based on analysis.

        Returns list of recommendation strings.
        """
        recommendations = []
        vs_dataset = score_comparison.get("vs_dataset", {})
        percentiles = score_comparison.get("percentiles", {})

        # Hook recommendations
        if vs_dataset.get("hook", 0) < 0:
            if percentiles.get("hook", 50) < 40:
                recommendations.append(
                    "Focus on stronger opening hooks - try question hooks or bold statements"
                )
            elif percentiles.get("hook", 50) < 60:
                recommendations.append(
                    "Experiment with more dynamic first-frame visuals to capture attention"
                )

        # Viral potential recommendations
        if vs_dataset.get("viral", 0) < 0:
            recommendations.append(
                "Increase shareability - add relatable moments or surprising elements"
            )

        # Replicability recommendations
        if vs_dataset.get("replicability", 0) > 1:
            recommendations.append(
                "Your format is highly replicable - consider creating a signature series"
            )
        elif vs_dataset.get("replicability", 0) < -1:
            recommendations.append(
                "Simplify production - viewers may not be able to replicate or feel inspired"
            )

        # Pattern-based recommendations
        hook_comparison = pattern_comparison.get("pattern_comparison", {}).get("hook_types", {})
        for hook_type, diff in hook_comparison.items():
            if diff < -15:  # Significantly underusing
                recommendations.append(f"Try more '{hook_type}' style hooks")
                break

        # Strength-based recommendations
        if percentiles.get("hook", 50) > 70:
            recommendations.append(
                "Strong hook game! Focus on maintaining consistency across all videos"
            )
        if percentiles.get("viral", 50) > 70:
            recommendations.append(
                "High viral potential - consider posting more frequently"
            )

        return recommendations[:5]  # Limit to top 5 recommendations

    def generate_full_comparison(
        self,
        account_posts: list[dict],
        dataset_posts: list[dict],
        dataset_averages: dict,
    ) -> dict:
        """
        Generate complete comparison analysis.

        Returns full comparison data including scores, patterns, gaps, and recommendations.
        """
        # Extract all scores for percentile calculation
        all_scores = {"hooks": [], "virals": [], "replicabilities": []}
        for post in dataset_posts:
            analysis = post.get("analysis", {})
            if not analysis:
                continue
            hook_val = analysis.get("hook", {}).get("hook_strength")
            viral_val = analysis.get("trends", {}).get("viral_potential_score")
            replicate_val = analysis.get("replicability", {}).get("replicability_score")
            if hook_val is not None:
                all_scores["hooks"].append(float(hook_val))
            if viral_val is not None:
                all_scores["virals"].append(float(viral_val))
            if replicate_val is not None:
                all_scores["replicabilities"].append(float(replicate_val))

        # Compare scores
        score_comparison = self.compare_scores(account_posts, dataset_averages, all_scores)

        # Analyze patterns
        pattern_analysis = self.analyze_patterns(account_posts, dataset_posts)

        # Get top performer patterns (top 20% by viral score)
        top_posts = [
            p for p in dataset_posts
            if p.get("analysis", {}).get("trends", {}).get("viral_potential_score", 0) >= 7
        ]
        top_performer_patterns = self._extract_patterns(top_posts)

        # Identify gaps
        gaps = self.identify_gaps(
            pattern_analysis["account_patterns"],
            top_performer_patterns,
            score_comparison,
        )

        # Generate recommendations
        recommendations = self.generate_recommendations(
            score_comparison,
            pattern_analysis,
            gaps,
        )

        return {
            "scores": score_comparison,
            "patterns": pattern_analysis,
            "gaps": gaps,
            "recommendations": recommendations,
            "dataset_size": len(dataset_posts),
            "top_performer_count": len(top_posts),
        }
