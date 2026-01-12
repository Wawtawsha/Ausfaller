-- Weighted analytics views
-- Weights scores by views-per-day to favor videos that performed well quickly
-- Formula: weight = views / max(age_in_days, 1)
-- This gives higher weight to videos that accumulated views faster

-- Drop existing views to allow column changes
DROP VIEW IF EXISTS analytics_summary CASCADE;
DROP VIEW IF EXISTS niche_analytics CASCADE;
DROP VIEW IF EXISTS hashtag_performance CASCADE;
DROP VIEW IF EXISTS hook_trends CASCADE;

-- Weighted summary stats (includes both simple and engagement-weighted averages)
CREATE OR REPLACE VIEW analytics_summary AS
SELECT
    COUNT(*) as total_videos,
    COUNT(CASE WHEN analysis IS NOT NULL THEN 1 END) as analyzed_videos,

    -- Simple averages (for reference)
    AVG((analysis->'hook'->>'hook_strength')::numeric) as avg_hook_strength,
    AVG((analysis->'trends'->>'viral_potential_score')::numeric) as avg_viral_potential,
    AVG((analysis->'replicability'->>'replicability_score')::numeric) as avg_replicability,

    -- Weighted averages (by views per day)
    -- Formula: SUM(score * weight) / SUM(weight) where weight = views / age_in_days
    CASE
        WHEN SUM(
            CASE WHEN posted_at IS NOT NULL AND views > 0
                 AND analysis->'hook'->>'hook_strength' IS NOT NULL
            THEN views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)
            ELSE 0 END
        ) > 0
        THEN SUM(
            CASE WHEN posted_at IS NOT NULL AND views > 0
                 AND analysis->'hook'->>'hook_strength' IS NOT NULL
            THEN (analysis->'hook'->>'hook_strength')::numeric
                 * (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
            ELSE 0 END
        ) / SUM(
            CASE WHEN posted_at IS NOT NULL AND views > 0
                 AND analysis->'hook'->>'hook_strength' IS NOT NULL
            THEN views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)
            ELSE 0 END
        )
        ELSE NULL
    END as weighted_avg_hook_strength,

    CASE
        WHEN SUM(
            CASE WHEN posted_at IS NOT NULL AND views > 0
                 AND analysis->'trends'->>'viral_potential_score' IS NOT NULL
            THEN views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)
            ELSE 0 END
        ) > 0
        THEN SUM(
            CASE WHEN posted_at IS NOT NULL AND views > 0
                 AND analysis->'trends'->>'viral_potential_score' IS NOT NULL
            THEN (analysis->'trends'->>'viral_potential_score')::numeric
                 * (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
            ELSE 0 END
        ) / SUM(
            CASE WHEN posted_at IS NOT NULL AND views > 0
                 AND analysis->'trends'->>'viral_potential_score' IS NOT NULL
            THEN views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)
            ELSE 0 END
        )
        ELSE NULL
    END as weighted_avg_viral_potential,

    CASE
        WHEN SUM(
            CASE WHEN posted_at IS NOT NULL AND views > 0
                 AND analysis->'replicability'->>'replicability_score' IS NOT NULL
            THEN views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)
            ELSE 0 END
        ) > 0
        THEN SUM(
            CASE WHEN posted_at IS NOT NULL AND views > 0
                 AND analysis->'replicability'->>'replicability_score' IS NOT NULL
            THEN (analysis->'replicability'->>'replicability_score')::numeric
                 * (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
            ELSE 0 END
        ) / SUM(
            CASE WHEN posted_at IS NOT NULL AND views > 0
                 AND analysis->'replicability'->>'replicability_score' IS NOT NULL
            THEN views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)
            ELSE 0 END
        )
        ELSE NULL
    END as weighted_avg_replicability,

    -- Engagement totals
    SUM(views) as total_views,
    SUM(likes) as total_likes,

    MIN(scraped_at) as first_scraped,
    MAX(scraped_at) as last_scraped
FROM posts;


-- Weighted niche analytics
CREATE OR REPLACE VIEW niche_analytics AS
SELECT
    niche,
    COUNT(*) as video_count,
    COUNT(*) FILTER (WHERE analysis IS NOT NULL) as analyzed_count,

    -- Simple averages
    AVG((analysis->'hook'->>'hook_strength')::numeric) as avg_hook_strength,
    AVG((analysis->'trends'->>'viral_potential_score')::numeric) as avg_viral_potential,
    AVG((analysis->'replicability'->>'replicability_score')::numeric) as avg_replicability,

    -- Weighted averages
    CASE
        WHEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'hook'->>'hook_strength' IS NOT NULL
                 THEN views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)
                 ELSE 0 END) > 0
        THEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'hook'->>'hook_strength' IS NOT NULL
                 THEN (analysis->'hook'->>'hook_strength')::numeric
                      * (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                 ELSE 0 END)
             / SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                        AND analysis->'hook'->>'hook_strength' IS NOT NULL
                   THEN views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)
                   ELSE 0 END)
        ELSE NULL
    END as weighted_avg_hook_strength,

    CASE
        WHEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'trends'->>'viral_potential_score' IS NOT NULL
                 THEN views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)
                 ELSE 0 END) > 0
        THEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'trends'->>'viral_potential_score' IS NOT NULL
                 THEN (analysis->'trends'->>'viral_potential_score')::numeric
                      * (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                 ELSE 0 END)
             / SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                        AND analysis->'trends'->>'viral_potential_score' IS NOT NULL
                   THEN views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)
                   ELSE 0 END)
        ELSE NULL
    END as weighted_avg_viral_potential,

    CASE
        WHEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'replicability'->>'replicability_score' IS NOT NULL
                 THEN views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)
                 ELSE 0 END) > 0
        THEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'replicability'->>'replicability_score' IS NOT NULL
                 THEN (analysis->'replicability'->>'replicability_score')::numeric
                      * (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                 ELSE 0 END)
             / SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                        AND analysis->'replicability'->>'replicability_score' IS NOT NULL
                   THEN views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)
                   ELSE 0 END)
        ELSE NULL
    END as weighted_avg_replicability,

    -- Engagement totals
    SUM(views) as total_views,
    SUM(likes) as total_likes
FROM posts
WHERE niche IS NOT NULL
GROUP BY niche
ORDER BY video_count DESC;


-- Weighted hashtag performance
CREATE OR REPLACE VIEW hashtag_performance AS
SELECT
    niche,
    source_hashtag,
    COUNT(*) as video_count,

    -- Simple averages
    AVG((analysis->'hook'->>'hook_strength')::numeric) as avg_hook_strength,
    AVG((analysis->'trends'->>'viral_potential_score')::numeric) as avg_viral_potential,
    AVG((analysis->'replicability'->>'replicability_score')::numeric) as avg_replicability,

    -- Weighted averages
    CASE
        WHEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'hook'->>'hook_strength' IS NOT NULL
                 THEN views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)
                 ELSE 0 END) > 0
        THEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'hook'->>'hook_strength' IS NOT NULL
                 THEN (analysis->'hook'->>'hook_strength')::numeric
                      * (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                 ELSE 0 END)
             / SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                        AND analysis->'hook'->>'hook_strength' IS NOT NULL
                   THEN views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)
                   ELSE 0 END)
        ELSE NULL
    END as weighted_avg_hook_strength,

    CASE
        WHEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'trends'->>'viral_potential_score' IS NOT NULL
                 THEN views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)
                 ELSE 0 END) > 0
        THEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'trends'->>'viral_potential_score' IS NOT NULL
                 THEN (analysis->'trends'->>'viral_potential_score')::numeric
                      * (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                 ELSE 0 END)
             / SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                        AND analysis->'trends'->>'viral_potential_score' IS NOT NULL
                   THEN views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)
                   ELSE 0 END)
        ELSE NULL
    END as weighted_avg_viral_potential,

    CASE
        WHEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'replicability'->>'replicability_score' IS NOT NULL
                 THEN views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)
                 ELSE 0 END) > 0
        THEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'replicability'->>'replicability_score' IS NOT NULL
                 THEN (analysis->'replicability'->>'replicability_score')::numeric
                      * (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                 ELSE 0 END)
             / SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                        AND analysis->'replicability'->>'replicability_score' IS NOT NULL
                   THEN views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)
                   ELSE 0 END)
        ELSE NULL
    END as weighted_avg_replicability,

    -- Engagement totals
    SUM(views) as total_views,
    SUM(likes) as total_likes
FROM posts
WHERE source_hashtag IS NOT NULL AND analysis IS NOT NULL
GROUP BY niche, source_hashtag
ORDER BY niche, video_count DESC;


-- Weighted hook trends
CREATE OR REPLACE VIEW hook_trends AS
SELECT
    analysis->'hook'->>'hook_type' as hook_type,
    analysis->'hook'->>'hook_technique' as hook_technique,

    -- Simple average
    AVG((analysis->'hook'->>'hook_strength')::numeric) as avg_strength,

    -- Weighted average
    CASE
        WHEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                 THEN views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)
                 ELSE 0 END) > 0
        THEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                 THEN (analysis->'hook'->>'hook_strength')::numeric
                      * (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                 ELSE 0 END)
             / SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                   THEN views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)
                   ELSE 0 END)
        ELSE NULL
    END as weighted_avg_strength,

    COUNT(*) as video_count,
    SUM(views) as total_views
FROM posts
WHERE analysis IS NOT NULL
  AND analysis->'hook'->>'hook_type' IS NOT NULL
GROUP BY 1, 2
ORDER BY video_count DESC;
