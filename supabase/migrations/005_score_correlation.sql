-- Score correlation analysis views for auto-recalibration
-- Tracks relationship between AI-predicted scores and actual engagement

-- Main correlation view: Links scores to engagement metrics
CREATE OR REPLACE VIEW score_engagement_correlation AS
SELECT
    id,
    video_url,
    niche,
    views,
    likes,
    comments,
    shares,
    posted_at,
    scraped_at,

    -- Engagement velocity (views per day, time-decay adjusted)
    CASE
        WHEN posted_at IS NOT NULL AND views > 0
        THEN views::numeric / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)
        ELSE NULL
    END as views_per_day,

    -- Weighted engagement rate (industry formula: shares×7 + comments×5 + likes×1)
    CASE
        WHEN views > 0
        THEN ((COALESCE(shares, 0) * 7) + (COALESCE(comments, 0) * 5) + (COALESCE(likes, 0))) * 100.0 / views
        ELSE NULL
    END as weighted_engagement_rate,

    -- Simple engagement rate
    CASE
        WHEN views > 0
        THEN (COALESCE(likes, 0) + COALESCE(comments, 0) + COALESCE(shares, 0)) * 100.0 / views
        ELSE NULL
    END as simple_engagement_rate,

    -- AI Scores
    (analysis->'hook'->>'hook_strength')::int as hook_score,
    (analysis->'trends'->>'viral_potential_score')::int as viral_score,
    (analysis->'replicability'->>'replicability_score')::int as replicability_score,
    (analysis->'emotion'->>'relatability_score')::int as relatability_score,

    -- Performance tier (for calibration grouping)
    CASE
        WHEN views >= 1000000 THEN 'viral'
        WHEN views >= 100000 THEN 'high'
        WHEN views >= 10000 THEN 'moderate'
        WHEN views >= 1000 THEN 'low'
        ELSE 'minimal'
    END as performance_tier,

    -- Video age in days
    EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400 as age_days

FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND views > 0;


-- Score calibration view: Shows average scores by performance tier
-- Use this to identify if scoring is calibrated correctly
CREATE OR REPLACE VIEW score_calibration AS
SELECT
    performance_tier,
    COUNT(*) as video_count,
    ROUND(AVG(hook_score), 2) as avg_hook,
    ROUND(STDDEV(hook_score), 2) as stddev_hook,
    ROUND(AVG(viral_score), 2) as avg_viral,
    ROUND(STDDEV(viral_score), 2) as stddev_viral,
    ROUND(AVG(replicability_score), 2) as avg_replicability,
    ROUND(AVG(relatability_score), 2) as avg_relatability,
    ROUND(AVG(weighted_engagement_rate), 2) as avg_engagement_rate,
    ROUND(AVG(views_per_day), 0) as avg_views_per_day,
    ROUND(AVG(views), 0) as avg_views
FROM score_engagement_correlation
GROUP BY performance_tier
ORDER BY avg_views_per_day DESC NULLS LAST;


-- Score distribution view: Shows score distributions
CREATE OR REPLACE VIEW score_distribution AS
SELECT
    hook_score as score,
    'hook' as metric,
    COUNT(*) as count,
    ROUND(AVG(views_per_day), 0) as avg_views_per_day,
    ROUND(AVG(weighted_engagement_rate), 2) as avg_engagement_rate
FROM score_engagement_correlation
WHERE hook_score IS NOT NULL
GROUP BY hook_score

UNION ALL

SELECT
    viral_score as score,
    'viral' as metric,
    COUNT(*) as count,
    ROUND(AVG(views_per_day), 0) as avg_views_per_day,
    ROUND(AVG(weighted_engagement_rate), 2) as avg_engagement_rate
FROM score_engagement_correlation
WHERE viral_score IS NOT NULL
GROUP BY viral_score

UNION ALL

SELECT
    replicability_score as score,
    'replicability' as metric,
    COUNT(*) as count,
    ROUND(AVG(views_per_day), 0) as avg_views_per_day,
    ROUND(AVG(weighted_engagement_rate), 2) as avg_engagement_rate
FROM score_engagement_correlation
WHERE replicability_score IS NOT NULL
GROUP BY replicability_score

ORDER BY metric, score;


-- Niche calibration: Shows score performance by niche
CREATE OR REPLACE VIEW niche_score_calibration AS
SELECT
    niche,
    COUNT(*) as video_count,
    ROUND(AVG(hook_score), 2) as avg_hook,
    ROUND(AVG(viral_score), 2) as avg_viral,
    ROUND(AVG(replicability_score), 2) as avg_replicability,
    ROUND(AVG(views_per_day), 0) as avg_views_per_day,
    ROUND(AVG(weighted_engagement_rate), 2) as avg_engagement_rate,
    -- Correlation hints
    ROUND(AVG(CASE WHEN performance_tier = 'viral' THEN hook_score ELSE NULL END), 2) as viral_tier_avg_hook,
    ROUND(AVG(CASE WHEN performance_tier = 'low' THEN hook_score ELSE NULL END), 2) as low_tier_avg_hook
FROM score_engagement_correlation
WHERE niche IS NOT NULL
GROUP BY niche
HAVING COUNT(*) >= 5
ORDER BY avg_views_per_day DESC NULLS LAST;
