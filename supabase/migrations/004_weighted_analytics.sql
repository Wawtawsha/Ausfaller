-- Weighted analytics views with time decay
-- Formula: weight = (views / max(age_in_days, 1)) * POWER(0.5, age_in_days / 90)
-- - views/age_in_days: favors videos that accumulated views faster
-- - POWER(0.5, age/90): 90-day half-life decay (recent content matters more)
--   - Today: 100% weight
--   - 90 days ago: 50% weight
--   - 180 days ago: 25% weight
--   - 1 year ago: ~6% weight

-- Drop existing views to allow column changes
DROP VIEW IF EXISTS analytics_summary CASCADE;
DROP VIEW IF EXISTS niche_analytics CASCADE;
DROP VIEW IF EXISTS hashtag_performance CASCADE;
DROP VIEW IF EXISTS hook_trends CASCADE;

-- Weighted summary stats with time decay
CREATE OR REPLACE VIEW analytics_summary AS
SELECT
    COUNT(*) as total_videos,
    COUNT(CASE WHEN analysis IS NOT NULL THEN 1 END) as analyzed_videos,

    -- Simple averages (for reference)
    AVG((analysis->'hook'->>'hook_strength')::numeric) as avg_hook_strength,
    AVG((analysis->'trends'->>'viral_potential_score')::numeric) as avg_viral_potential,
    AVG((analysis->'replicability'->>'replicability_score')::numeric) as avg_replicability,

    -- Weighted averages with time decay
    CASE
        WHEN SUM(
            CASE WHEN posted_at IS NOT NULL AND views > 0
                 AND analysis->'hook'->>'hook_strength' IS NOT NULL
            THEN (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                 * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
            ELSE 0 END
        ) > 0
        THEN SUM(
            CASE WHEN posted_at IS NOT NULL AND views > 0
                 AND analysis->'hook'->>'hook_strength' IS NOT NULL
            THEN (analysis->'hook'->>'hook_strength')::numeric
                 * (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                 * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
            ELSE 0 END
        ) / SUM(
            CASE WHEN posted_at IS NOT NULL AND views > 0
                 AND analysis->'hook'->>'hook_strength' IS NOT NULL
            THEN (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                 * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
            ELSE 0 END
        )
        ELSE NULL
    END as weighted_avg_hook_strength,

    CASE
        WHEN SUM(
            CASE WHEN posted_at IS NOT NULL AND views > 0
                 AND analysis->'trends'->>'viral_potential_score' IS NOT NULL
            THEN (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                 * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
            ELSE 0 END
        ) > 0
        THEN SUM(
            CASE WHEN posted_at IS NOT NULL AND views > 0
                 AND analysis->'trends'->>'viral_potential_score' IS NOT NULL
            THEN (analysis->'trends'->>'viral_potential_score')::numeric
                 * (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                 * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
            ELSE 0 END
        ) / SUM(
            CASE WHEN posted_at IS NOT NULL AND views > 0
                 AND analysis->'trends'->>'viral_potential_score' IS NOT NULL
            THEN (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                 * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
            ELSE 0 END
        )
        ELSE NULL
    END as weighted_avg_viral_potential,

    CASE
        WHEN SUM(
            CASE WHEN posted_at IS NOT NULL AND views > 0
                 AND analysis->'replicability'->>'replicability_score' IS NOT NULL
            THEN (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                 * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
            ELSE 0 END
        ) > 0
        THEN SUM(
            CASE WHEN posted_at IS NOT NULL AND views > 0
                 AND analysis->'replicability'->>'replicability_score' IS NOT NULL
            THEN (analysis->'replicability'->>'replicability_score')::numeric
                 * (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                 * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
            ELSE 0 END
        ) / SUM(
            CASE WHEN posted_at IS NOT NULL AND views > 0
                 AND analysis->'replicability'->>'replicability_score' IS NOT NULL
            THEN (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                 * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
            ELSE 0 END
        )
        ELSE NULL
    END as weighted_avg_replicability,

    SUM(views) as total_views,
    SUM(likes) as total_likes,
    MIN(scraped_at) as first_scraped,
    MAX(scraped_at) as last_scraped
FROM posts;


-- Weighted niche analytics with time decay
CREATE OR REPLACE VIEW niche_analytics AS
SELECT
    niche,
    COUNT(*) as video_count,
    COUNT(*) FILTER (WHERE analysis IS NOT NULL) as analyzed_count,
    AVG((analysis->'hook'->>'hook_strength')::numeric) as avg_hook_strength,
    AVG((analysis->'trends'->>'viral_potential_score')::numeric) as avg_viral_potential,
    AVG((analysis->'replicability'->>'replicability_score')::numeric) as avg_replicability,
    CASE
        WHEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'hook'->>'hook_strength' IS NOT NULL
                 THEN (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                      * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
                 ELSE 0 END) > 0
        THEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'hook'->>'hook_strength' IS NOT NULL
                 THEN (analysis->'hook'->>'hook_strength')::numeric
                      * (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                      * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
                 ELSE 0 END)
             / SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                        AND analysis->'hook'->>'hook_strength' IS NOT NULL
                   THEN (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                        * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
                   ELSE 0 END)
        ELSE NULL
    END as weighted_avg_hook_strength,
    CASE
        WHEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'trends'->>'viral_potential_score' IS NOT NULL
                 THEN (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                      * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
                 ELSE 0 END) > 0
        THEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'trends'->>'viral_potential_score' IS NOT NULL
                 THEN (analysis->'trends'->>'viral_potential_score')::numeric
                      * (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                      * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
                 ELSE 0 END)
             / SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                        AND analysis->'trends'->>'viral_potential_score' IS NOT NULL
                   THEN (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                        * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
                   ELSE 0 END)
        ELSE NULL
    END as weighted_avg_viral_potential,
    CASE
        WHEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'replicability'->>'replicability_score' IS NOT NULL
                 THEN (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                      * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
                 ELSE 0 END) > 0
        THEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'replicability'->>'replicability_score' IS NOT NULL
                 THEN (analysis->'replicability'->>'replicability_score')::numeric
                      * (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                      * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
                 ELSE 0 END)
             / SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                        AND analysis->'replicability'->>'replicability_score' IS NOT NULL
                   THEN (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                        * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
                   ELSE 0 END)
        ELSE NULL
    END as weighted_avg_replicability,
    SUM(views) as total_views,
    SUM(likes) as total_likes
FROM posts
WHERE niche IS NOT NULL
GROUP BY niche
ORDER BY video_count DESC;


-- Weighted hashtag performance with time decay
CREATE OR REPLACE VIEW hashtag_performance AS
SELECT
    niche,
    source_hashtag,
    COUNT(*) as video_count,
    AVG((analysis->'hook'->>'hook_strength')::numeric) as avg_hook_strength,
    AVG((analysis->'trends'->>'viral_potential_score')::numeric) as avg_viral_potential,
    AVG((analysis->'replicability'->>'replicability_score')::numeric) as avg_replicability,
    CASE
        WHEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'hook'->>'hook_strength' IS NOT NULL
                 THEN (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                      * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
                 ELSE 0 END) > 0
        THEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'hook'->>'hook_strength' IS NOT NULL
                 THEN (analysis->'hook'->>'hook_strength')::numeric
                      * (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                      * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
                 ELSE 0 END)
             / SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                        AND analysis->'hook'->>'hook_strength' IS NOT NULL
                   THEN (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                        * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
                   ELSE 0 END)
        ELSE NULL
    END as weighted_avg_hook_strength,
    CASE
        WHEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'trends'->>'viral_potential_score' IS NOT NULL
                 THEN (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                      * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
                 ELSE 0 END) > 0
        THEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'trends'->>'viral_potential_score' IS NOT NULL
                 THEN (analysis->'trends'->>'viral_potential_score')::numeric
                      * (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                      * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
                 ELSE 0 END)
             / SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                        AND analysis->'trends'->>'viral_potential_score' IS NOT NULL
                   THEN (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                        * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
                   ELSE 0 END)
        ELSE NULL
    END as weighted_avg_viral_potential,
    CASE
        WHEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'replicability'->>'replicability_score' IS NOT NULL
                 THEN (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                      * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
                 ELSE 0 END) > 0
        THEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                      AND analysis->'replicability'->>'replicability_score' IS NOT NULL
                 THEN (analysis->'replicability'->>'replicability_score')::numeric
                      * (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                      * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
                 ELSE 0 END)
             / SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                        AND analysis->'replicability'->>'replicability_score' IS NOT NULL
                   THEN (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                        * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
                   ELSE 0 END)
        ELSE NULL
    END as weighted_avg_replicability,
    SUM(views) as total_views,
    SUM(likes) as total_likes
FROM posts
WHERE source_hashtag IS NOT NULL AND analysis IS NOT NULL
GROUP BY niche, source_hashtag
ORDER BY niche, video_count DESC;


-- Weighted hook trends with time decay
CREATE OR REPLACE VIEW hook_trends AS
SELECT
    analysis->'hook'->>'hook_type' as hook_type,
    analysis->'hook'->>'hook_technique' as hook_technique,
    AVG((analysis->'hook'->>'hook_strength')::numeric) as avg_strength,
    CASE
        WHEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                 THEN (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                      * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
                 ELSE 0 END) > 0
        THEN SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                 THEN (analysis->'hook'->>'hook_strength')::numeric
                      * (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                      * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
                 ELSE 0 END)
             / SUM(CASE WHEN posted_at IS NOT NULL AND views > 0
                   THEN (views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))
                        * POWER(0.5, EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 / 90)
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
