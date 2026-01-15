#!/usr/bin/env python3
"""
Aggregate Gemini video analysis results from Supabase.
Outputs JSON with aggregated insights for dashboard population.
"""

import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from supabase import create_client


def get_supabase_client():
    """Create Supabase client."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY required")
    return create_client(url, key)


def fetch_all_analyzed_posts(client):
    """Fetch all posts with analysis data."""
    # Fetch in batches due to Supabase limits
    all_posts = []
    limit = 1000
    offset = 0

    while True:
        result = (
            client.table("posts")
            .select("id, platform, platform_id, author_username, video_url, analysis, views, likes, comments, shares, scraped_at, analyzed_at, niche, source_hashtag")
            .not_.is_("analysis", "null")
            .order("analyzed_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        if not result.data:
            break

        all_posts.extend(result.data)
        print(f"Fetched {len(all_posts)} posts...", file=sys.stderr)

        if len(result.data) < limit:
            break
        offset += limit

    return all_posts


def safe_get(d, *keys, default=None):
    """Safely get nested dictionary values."""
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key, default)
        else:
            return default
    return d if d is not None else default


def aggregate_analysis(posts):
    """Aggregate analysis data from all posts."""
    # Counters for various fields
    hook_types = Counter()
    hook_techniques = Counter()
    audio_categories = Counter()
    visual_styles = Counter()
    visual_settings = Counter()
    viral_factors = Counter()
    content_categories = Counter()

    # Score aggregators
    hook_scores = []
    viral_scores = []
    replicability_scores = []

    # Top performers for leaderboard
    top_replicable = []
    top_viral = []

    # Platform breakdown
    platform_stats = defaultdict(lambda: {"count": 0, "views": 0, "likes": 0})

    # Niche breakdown
    niche_stats = defaultdict(lambda: {"count": 0, "analyzed": 0})

    # Creator stats
    creator_stats = defaultdict(lambda: {"count": 0, "total_views": 0, "total_likes": 0})

    for post in posts:
        analysis = post.get("analysis", {})
        if isinstance(analysis, str):
            try:
                analysis = json.loads(analysis)
            except:
                continue

        if not analysis:
            continue

        # Hook analysis
        hook = analysis.get("hook", {})
        if isinstance(hook, dict):
            if hook.get("hook_type"):
                hook_types[hook["hook_type"]] += 1
            if hook.get("hook_technique"):
                hook_techniques[hook["hook_technique"]] += 1
            if hook.get("hook_strength"):
                try:
                    hook_scores.append(float(hook["hook_strength"]))
                except:
                    pass

        # Audio analysis
        audio = analysis.get("audio", {})
        if isinstance(audio, dict) and audio.get("category"):
            audio_categories[audio["category"]] += 1

        # Visual analysis
        visual = analysis.get("visual", {})
        if isinstance(visual, dict):
            if visual.get("style"):
                visual_styles[visual["style"]] += 1
            if visual.get("setting"):
                visual_settings[visual["setting"]] += 1

        # Viral factors
        trends = analysis.get("trends", {})
        if isinstance(trends, dict):
            if trends.get("viral_potential_score"):
                try:
                    viral_scores.append(float(trends["viral_potential_score"]))
                except:
                    pass
            factors = trends.get("viral_factors", [])
            if isinstance(factors, list):
                for factor in factors:
                    if factor:
                        viral_factors[factor] += 1

        # Content category
        if analysis.get("content_category"):
            content_categories[analysis["content_category"]] += 1

        # Replicability
        replicability = analysis.get("replicability", {})
        if isinstance(replicability, dict):
            score = replicability.get("replicability_score")
            if score:
                try:
                    score = float(score)
                    replicability_scores.append(score)

                    # Track for leaderboard
                    if score >= 7:
                        top_replicable.append({
                            "author": post.get("author_username", "unknown"),
                            "platform": post.get("platform"),
                            "video_url": post.get("video_url"),
                            "score": score,
                            "difficulty": replicability.get("difficulty", "unknown"),
                            "why_it_works": replicability.get("why_it_works", "")
                        })
                except:
                    pass

        # Platform stats
        platform = post.get("platform", "unknown")
        platform_stats[platform]["count"] += 1
        platform_stats[platform]["views"] += post.get("views") or 0
        platform_stats[platform]["likes"] += post.get("likes") or 0

        # Niche stats
        niche = post.get("niche") or "default"
        niche_stats[niche]["count"] += 1
        niche_stats[niche]["analyzed"] += 1

        # Creator stats
        author = post.get("author_username", "unknown")
        creator_stats[author]["count"] += 1
        creator_stats[author]["total_views"] += post.get("views") or 0
        creator_stats[author]["total_likes"] += post.get("likes") or 0

    # Sort top replicable
    top_replicable.sort(key=lambda x: x["score"], reverse=True)

    # Calculate averages
    avg_hook = sum(hook_scores) / len(hook_scores) if hook_scores else 0
    avg_viral = sum(viral_scores) / len(viral_scores) if viral_scores else 0
    avg_replicability = sum(replicability_scores) / len(replicability_scores) if replicability_scores else 0

    # Get top creators by engagement
    top_creators = sorted(
        [
            {"author": k, **v, "avg_views": v["total_views"] / v["count"] if v["count"] > 0 else 0}
            for k, v in creator_stats.items()
            if v["count"] >= 2  # At least 2 videos
        ],
        key=lambda x: x["avg_views"],
        reverse=True
    )[:20]

    return {
        "summary": {
            "total_analyzed": len(posts),
            "avg_hook_strength": round(avg_hook, 2),
            "avg_viral_potential": round(avg_viral, 2),
            "avg_replicability": round(avg_replicability, 2),
        },
        "hook_types": dict(hook_types.most_common(10)),
        "hook_techniques": dict(hook_techniques.most_common(10)),
        "audio_categories": dict(audio_categories.most_common(10)),
        "visual_styles": dict(visual_styles.most_common(10)),
        "visual_settings": dict(visual_settings.most_common(10)),
        "viral_factors": dict(viral_factors.most_common(15)),
        "content_categories": dict(content_categories.most_common(10)),
        "platform_breakdown": dict(platform_stats),
        "niche_breakdown": dict(niche_stats),
        "top_replicable": top_replicable[:20],
        "top_creators": top_creators,
        "generated_at": datetime.utcnow().isoformat()
    }


def main():
    """Main entry point."""
    print("Connecting to Supabase...", file=sys.stderr)
    client = get_supabase_client()

    print("Fetching analyzed posts...", file=sys.stderr)
    posts = fetch_all_analyzed_posts(client)
    print(f"Found {len(posts)} analyzed posts", file=sys.stderr)

    if not posts:
        print("No analyzed posts found", file=sys.stderr)
        return

    print("Aggregating analysis...", file=sys.stderr)
    aggregated = aggregate_analysis(posts)

    # Output JSON to stdout
    print(json.dumps(aggregated, indent=2))


if __name__ == "__main__":
    main()
