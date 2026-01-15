-- ============================================================
-- Migration 009: Niche Mode Separation
-- ============================================================
-- This migration properly separates entertainment and data_engineering content
-- by adding niche_mode filters to all analytics views.

-- ============================================================
-- PART 1: BACKFILL niche_mode COLUMN
-- ============================================================

-- Ensure niche_mode column exists (may already exist from migration 008)
ALTER TABLE posts ADD COLUMN IF NOT EXISTS niche_mode VARCHAR(50) DEFAULT 'entertainment';
CREATE INDEX IF NOT EXISTS idx_posts_niche_mode ON posts(niche_mode);

-- 1a. Platform-based backfill (100% accurate for youtube_shorts and substack)
UPDATE posts SET niche_mode = 'data_engineering'
WHERE platform IN ('youtube_shorts', 'substack')
  AND (niche_mode IS NULL OR niche_mode = 'entertainment');

-- 1b. TikTok hashtag-based backfill
UPDATE posts SET niche_mode = 'data_engineering'
WHERE platform = 'tiktok'
  AND (niche_mode IS NULL OR niche_mode = 'entertainment')
  AND (
    source_hashtag ILIKE '%dataengineering%'
    OR source_hashtag ILIKE '%microsoftfabric%'
    OR source_hashtag ILIKE '%powerbi%'
    OR source_hashtag ILIKE '%databricks%'
    OR source_hashtag ILIKE '%azuredatafactory%'
    OR source_hashtag ILIKE '%dataengineer%'
    OR source_hashtag ILIKE '%snowflake%'
    OR source_hashtag ILIKE '%techtok%'
    OR source_hashtag ILIKE '%coding%'
    OR source_hashtag ILIKE '%python%'
    OR source_hashtag ILIKE '%dbt%'
    OR source_hashtag ILIKE '%sql%'
    OR source_hashtag ILIKE '%medallion%'
    OR source_hashtag ILIKE '%datawarehouse%'
    OR source_hashtag ILIKE '%etl%'
    OR niche = 'data_engineering'
  );

-- 1c. Ensure remaining posts are explicitly entertainment
UPDATE posts SET niche_mode = 'entertainment'
WHERE niche_mode IS NULL;

-- Add composite index for common query patterns
CREATE INDEX IF NOT EXISTS idx_posts_niche_mode_analyzed
ON posts(niche_mode, analyzed_at)
WHERE analyzed_at IS NOT NULL;

-- ============================================================
-- PART 2: DROP AND RECREATE ENTERTAINMENT VIEWS
-- ============================================================
-- All views now include: AND niche_mode = 'entertainment'

-- Hook analysis aggregation
DROP VIEW IF EXISTS hook_trends CASCADE;
CREATE VIEW hook_trends AS
SELECT
    analysis->'hook'->>'hook_type' as hook_type,
    analysis->'hook'->>'hook_technique' as hook_technique,
    AVG((analysis->'hook'->>'hook_strength')::int) as avg_strength,
    COUNT(*) as video_count
FROM posts
WHERE analysis IS NOT NULL
  AND niche_mode = 'entertainment'
  AND analysis->'hook'->>'hook_type' IS NOT NULL
GROUP BY 1, 2
ORDER BY video_count DESC;

-- Audio trends
DROP VIEW IF EXISTS audio_trends CASCADE;
CREATE VIEW audio_trends AS
SELECT
    analysis->'audio'->>'sound_category' as category,
    (analysis->'audio'->>'is_trending_sound')::boolean as is_trending,
    COUNT(*) as count
FROM posts
WHERE analysis IS NOT NULL
  AND niche_mode = 'entertainment'
  AND analysis->'audio'->>'sound_category' IS NOT NULL
GROUP BY 1, 2
ORDER BY count DESC;

-- Visual style distribution
DROP VIEW IF EXISTS visual_trends CASCADE;
CREATE VIEW visual_trends AS
SELECT
    analysis->'visual'->>'visual_style' as style,
    analysis->'visual'->>'setting_type' as setting,
    COUNT(*) as count
FROM posts
WHERE analysis IS NOT NULL
  AND niche_mode = 'entertainment'
  AND analysis->'visual'->>'visual_style' IS NOT NULL
GROUP BY 1, 2
ORDER BY count DESC;

-- Viral potential distribution
DROP VIEW IF EXISTS viral_trends CASCADE;
CREATE VIEW viral_trends AS
SELECT
    (analysis->'trends'->>'viral_potential_score')::int as viral_score,
    analysis->'trends'->>'trend_lifecycle_stage' as lifecycle_stage,
    COUNT(*) as count
FROM posts
WHERE analysis IS NOT NULL
  AND niche_mode = 'entertainment'
  AND analysis->'trends'->>'viral_potential_score' IS NOT NULL
GROUP BY 1, 2
ORDER BY viral_score DESC;

-- Replicability leaderboard (top videos to replicate)
DROP VIEW IF EXISTS replicability_leaderboard CASCADE;
CREATE VIEW replicability_leaderboard AS
SELECT
    id,
    platform,
    platform_id,
    video_url,
    author_username,
    (analysis->'replicability'->>'replicability_score')::int as replicability_score,
    analysis->'replicability'->>'difficulty_level' as difficulty,
    (analysis->'trends'->>'viral_potential_score')::int as viral_score,
    analysis->>'why_it_works' as why_it_works,
    scraped_at
FROM posts
WHERE analysis IS NOT NULL
  AND niche_mode = 'entertainment'
  AND (analysis->'replicability'->>'replicability_score')::int >= 6
ORDER BY replicability_score DESC, viral_score DESC
LIMIT 100;

-- Summary stats view
DROP VIEW IF EXISTS analytics_summary CASCADE;
CREATE VIEW analytics_summary AS
SELECT
    COUNT(*) as total_videos,
    COUNT(CASE WHEN analysis IS NOT NULL THEN 1 END) as analyzed_videos,
    COUNT(DISTINCT author_username) as unique_creators,
    AVG((analysis->'hook'->>'hook_strength')::int) as avg_hook_strength,
    AVG((analysis->'trends'->>'viral_potential_score')::int) as avg_viral_potential,
    AVG((analysis->'replicability'->>'replicability_score')::int) as avg_replicability,
    MIN(scraped_at) as first_scraped,
    MAX(scraped_at) as last_scraped,
    SUM(file_size_bytes) as total_video_bytes,
    'entertainment' as niche_mode
FROM posts
WHERE niche_mode = 'entertainment';

-- Top viral factors (extracted from array)
DROP VIEW IF EXISTS viral_factors_breakdown CASCADE;
CREATE VIEW viral_factors_breakdown AS
SELECT
    factor,
    COUNT(*) as count
FROM posts,
     jsonb_array_elements_text(analysis->'trends'->'viral_factors') as factor
WHERE analysis IS NOT NULL
  AND niche_mode = 'entertainment'
GROUP BY factor
ORDER BY count DESC;

-- ============================================================
-- NICHE TRACKING VIEWS (From migration 003)
-- ============================================================

-- Analytics grouped by business niche (within entertainment)
DROP VIEW IF EXISTS niche_analytics CASCADE;
CREATE VIEW niche_analytics AS
SELECT
    niche,
    COUNT(*) as video_count,
    COUNT(*) FILTER (WHERE analysis IS NOT NULL) as analyzed_count,
    AVG((analysis->'hook'->>'hook_strength')::numeric) as avg_hook_strength,
    AVG((analysis->'trends'->>'viral_potential_score')::numeric) as avg_viral_potential,
    AVG((analysis->'replicability'->>'replicability_score')::numeric) as avg_replicability
FROM posts
WHERE niche IS NOT NULL
  AND niche_mode = 'entertainment'
GROUP BY niche
ORDER BY video_count DESC;

-- Hashtag performance within entertainment niche
DROP VIEW IF EXISTS hashtag_performance CASCADE;
CREATE VIEW hashtag_performance AS
SELECT
    niche,
    source_hashtag,
    COUNT(*) as video_count,
    AVG((analysis->'hook'->>'hook_strength')::numeric) as avg_hook_strength,
    AVG((analysis->'trends'->>'viral_potential_score')::numeric) as avg_viral_potential,
    AVG((analysis->'replicability'->>'replicability_score')::numeric) as avg_replicability
FROM posts
WHERE source_hashtag IS NOT NULL
  AND analysis IS NOT NULL
  AND niche_mode = 'entertainment'
GROUP BY niche, source_hashtag
ORDER BY niche, video_count DESC;

-- ============================================================
-- STRATEGIC ANALYSIS VIEWS (From migration 006)
-- ============================================================

-- Format Performance
DROP VIEW IF EXISTS format_performance CASCADE;
CREATE VIEW format_performance AS
SELECT
    analysis->'structure'->>'format_type' as format_type,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score,
    ROUND(AVG((analysis->'replicability'->>'replicability_score')::numeric), 2) as avg_replicability,
    ROUND(AVG((analysis->'hook'->>'hook_strength')::numeric), 2) as avg_hook_strength
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND niche_mode = 'entertainment'
  AND analysis->'structure'->>'format_type' IS NOT NULL
GROUP BY analysis->'structure'->>'format_type'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- Hook Technique Performance
DROP VIEW IF EXISTS hook_technique_performance CASCADE;
CREATE VIEW hook_technique_performance AS
SELECT
    analysis->'hook'->>'hook_technique' as hook_technique,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'hook'->>'hook_strength')::numeric), 2) as avg_hook_strength,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND niche_mode = 'entertainment'
  AND analysis->'hook'->>'hook_technique' IS NOT NULL
GROUP BY analysis->'hook'->>'hook_technique'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- Hook Type Performance
DROP VIEW IF EXISTS hook_type_performance CASCADE;
CREATE VIEW hook_type_performance AS
SELECT
    analysis->'hook'->>'hook_type' as hook_type,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'hook'->>'hook_strength')::numeric), 2) as avg_hook_strength
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND niche_mode = 'entertainment'
  AND analysis->'hook'->>'hook_type' IS NOT NULL
GROUP BY analysis->'hook'->>'hook_type'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- Audio Type Performance
DROP VIEW IF EXISTS audio_type_performance CASCADE;
CREATE VIEW audio_type_performance AS
SELECT
    analysis->'audio'->>'audio_type' as audio_type,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND niche_mode = 'entertainment'
  AND analysis->'audio'->>'audio_type' IS NOT NULL
GROUP BY analysis->'audio'->>'audio_type'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- Visual Style Performance
DROP VIEW IF EXISTS visual_style_performance CASCADE;
CREATE VIEW visual_style_performance AS
SELECT
    analysis->'visual'->>'visual_style' as visual_style,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND niche_mode = 'entertainment'
  AND analysis->'visual'->>'visual_style' IS NOT NULL
GROUP BY analysis->'visual'->>'visual_style'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- Top Combinations
DROP VIEW IF EXISTS top_combinations CASCADE;
CREATE VIEW top_combinations AS
SELECT
    analysis->'structure'->>'format_type' as format_type,
    analysis->'hook'->>'hook_technique' as hook_technique,
    analysis->'visual'->>'setting_type' as setting_type,
    analysis->'audio'->>'audio_type' as audio_type,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'replicability'->>'replicability_score')::numeric), 2) as avg_replicability,
    analysis->'replicability'->>'difficulty' as typical_difficulty
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND niche_mode = 'entertainment'
GROUP BY
    analysis->'structure'->>'format_type',
    analysis->'hook'->>'hook_technique',
    analysis->'visual'->>'setting_type',
    analysis->'audio'->>'audio_type',
    analysis->'replicability'->>'difficulty'
HAVING COUNT(*) >= 2
ORDER BY avg_views_per_day DESC NULLS LAST
LIMIT 25;

-- Saturation Metrics (RED FLAGS - overused techniques)
DROP VIEW IF EXISTS saturation_metrics CASCADE;
CREATE VIEW saturation_metrics AS
WITH overall_stats AS (
    SELECT
        AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)) as avg_views,
        COUNT(*) as total_videos
    FROM posts
    WHERE analysis IS NOT NULL AND posted_at IS NOT NULL AND niche_mode = 'entertainment'
),
hook_saturation AS (
    SELECT
        'hook_technique' as category,
        analysis->'hook'->>'hook_technique' as value,
        COUNT(*) as video_count,
        ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
        ROUND((COUNT(*)::float / (SELECT total_videos FROM overall_stats) * 100)::numeric, 1) as market_share_pct
    FROM posts
    WHERE analysis IS NOT NULL AND posted_at IS NOT NULL AND niche_mode = 'entertainment'
    GROUP BY analysis->'hook'->>'hook_technique'
    HAVING COUNT(*) >= 10
       AND AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)) < (SELECT avg_views FROM overall_stats)
),
format_saturation AS (
    SELECT
        'format_type' as category,
        analysis->'structure'->>'format_type' as value,
        COUNT(*) as video_count,
        ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
        ROUND((COUNT(*)::float / (SELECT total_videos FROM overall_stats) * 100)::numeric, 1) as market_share_pct
    FROM posts
    WHERE analysis IS NOT NULL AND posted_at IS NOT NULL AND niche_mode = 'entertainment'
    GROUP BY analysis->'structure'->>'format_type'
    HAVING COUNT(*) >= 10
       AND AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)) < (SELECT avg_views FROM overall_stats)
)
SELECT * FROM hook_saturation
UNION ALL
SELECT * FROM format_saturation
ORDER BY video_count DESC;

-- Gap Opportunities (OPPORTUNITIES - underrepresented but high-performing)
DROP VIEW IF EXISTS gap_opportunities CASCADE;
CREATE VIEW gap_opportunities AS
WITH overall_stats AS (
    SELECT
        AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)) as avg_views,
        COUNT(*) as total_videos
    FROM posts
    WHERE analysis IS NOT NULL AND posted_at IS NOT NULL AND niche_mode = 'entertainment'
),
format_gaps AS (
    SELECT
        'format_type' as category,
        analysis->'structure'->>'format_type' as value,
        COUNT(*) as video_count,
        ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
        ROUND((AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)) / NULLIF((SELECT avg_views FROM overall_stats), 0) * 100)::numeric, 0) as performance_vs_avg_pct
    FROM posts
    WHERE analysis IS NOT NULL AND posted_at IS NOT NULL AND niche_mode = 'entertainment'
    GROUP BY analysis->'structure'->>'format_type'
    HAVING COUNT(*) BETWEEN 3 AND 30
       AND AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)) > (SELECT avg_views FROM overall_stats) * 1.25
),
hook_gaps AS (
    SELECT
        'hook_technique' as category,
        analysis->'hook'->>'hook_technique' as value,
        COUNT(*) as video_count,
        ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
        ROUND((AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)) / NULLIF((SELECT avg_views FROM overall_stats), 0) * 100)::numeric, 0) as performance_vs_avg_pct
    FROM posts
    WHERE analysis IS NOT NULL AND posted_at IS NOT NULL AND niche_mode = 'entertainment'
    GROUP BY analysis->'hook'->>'hook_technique'
    HAVING COUNT(*) BETWEEN 3 AND 30
       AND AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)) > (SELECT avg_views FROM overall_stats) * 1.25
),
audio_gaps AS (
    SELECT
        'audio_type' as category,
        analysis->'audio'->>'audio_type' as value,
        COUNT(*) as video_count,
        ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
        ROUND((AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)) / NULLIF((SELECT avg_views FROM overall_stats), 0) * 100)::numeric, 0) as performance_vs_avg_pct
    FROM posts
    WHERE analysis IS NOT NULL AND posted_at IS NOT NULL AND niche_mode = 'entertainment'
    GROUP BY analysis->'audio'->>'audio_type'
    HAVING COUNT(*) BETWEEN 3 AND 30
       AND AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)) > (SELECT avg_views FROM overall_stats) * 1.25
)
SELECT * FROM format_gaps
UNION ALL
SELECT * FROM hook_gaps
UNION ALL
SELECT * FROM audio_gaps
ORDER BY performance_vs_avg_pct DESC NULLS LAST;

-- Strategic Summary
DROP VIEW IF EXISTS strategic_summary CASCADE;
CREATE VIEW strategic_summary AS
SELECT
    COUNT(*) as total_videos,
    COUNT(*) FILTER (WHERE analysis IS NOT NULL) as analyzed_videos,
    MIN(posted_at) as earliest_video,
    MAX(posted_at) as latest_video,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'hook'->>'hook_strength')::numeric), 2) as avg_hook_strength,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_potential,
    ROUND(AVG((analysis->'replicability'->>'replicability_score')::numeric), 2) as avg_replicability
FROM posts
WHERE posted_at IS NOT NULL
  AND niche_mode = 'entertainment';

-- ============================================================
-- EXPANDED METRIC VIEWS (From migration 007)
-- ============================================================

-- Setting Performance
DROP VIEW IF EXISTS setting_performance CASCADE;
CREATE VIEW setting_performance AS
SELECT
    analysis->'visual'->>'setting_type' as setting_type,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND niche_mode = 'entertainment'
  AND analysis->'visual'->>'setting_type' IS NOT NULL
GROUP BY analysis->'visual'->>'setting_type'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- Duration Performance
DROP VIEW IF EXISTS duration_performance CASCADE;
CREATE VIEW duration_performance AS
SELECT
    CASE
        WHEN (analysis->'structure'->>'estimated_duration_seconds')::numeric <= 15 THEN '0-15s'
        WHEN (analysis->'structure'->>'estimated_duration_seconds')::numeric <= 30 THEN '15-30s'
        WHEN (analysis->'structure'->>'estimated_duration_seconds')::numeric <= 60 THEN '30-60s'
        WHEN (analysis->'structure'->>'estimated_duration_seconds')::numeric <= 120 THEN '60-120s'
        ELSE '120s+'
    END as duration_bucket,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND niche_mode = 'entertainment'
  AND analysis->'structure'->>'estimated_duration_seconds' IS NOT NULL
GROUP BY duration_bucket
ORDER BY avg_views_per_day DESC NULLS LAST;

-- Emotion Performance
DROP VIEW IF EXISTS emotion_performance CASCADE;
CREATE VIEW emotion_performance AS
SELECT
    analysis->'emotion'->>'primary_emotion' as primary_emotion,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'emotion'->>'relatability_score')::numeric), 2) as avg_relatability
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND niche_mode = 'entertainment'
  AND analysis->'emotion'->>'primary_emotion' IS NOT NULL
GROUP BY analysis->'emotion'->>'primary_emotion'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- Humor Type Performance
DROP VIEW IF EXISTS humor_performance CASCADE;
CREATE VIEW humor_performance AS
SELECT
    analysis->'emotion'->>'humor_type' as humor_type,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND niche_mode = 'entertainment'
  AND analysis->'emotion'->>'humor_type' IS NOT NULL
GROUP BY analysis->'emotion'->>'humor_type'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- Production Quality Performance
DROP VIEW IF EXISTS production_quality_performance CASCADE;
CREATE VIEW production_quality_performance AS
SELECT
    analysis->'production'->>'overall_quality' as production_quality,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'replicability'->>'replicability_score')::numeric), 2) as avg_replicability
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND niche_mode = 'entertainment'
  AND analysis->'production'->>'overall_quality' IS NOT NULL
GROUP BY analysis->'production'->>'overall_quality'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- Camera Type Performance
DROP VIEW IF EXISTS camera_performance CASCADE;
CREATE VIEW camera_performance AS
SELECT
    analysis->'visual'->>'camera_type' as camera_type,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND niche_mode = 'entertainment'
  AND analysis->'visual'->>'camera_type' IS NOT NULL
GROUP BY analysis->'visual'->>'camera_type'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- Face Visibility Performance
DROP VIEW IF EXISTS face_visibility_performance CASCADE;
CREATE VIEW face_visibility_performance AS
SELECT
    analysis->'visual'->>'face_visibility' as face_visibility,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND niche_mode = 'entertainment'
  AND analysis->'visual'->>'face_visibility' IS NOT NULL
GROUP BY analysis->'visual'->>'face_visibility'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- Narrative Structure Performance
DROP VIEW IF EXISTS narrative_performance CASCADE;
CREATE VIEW narrative_performance AS
SELECT
    analysis->'structure'->>'narrative_structure' as narrative_structure,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND niche_mode = 'entertainment'
  AND analysis->'structure'->>'narrative_structure' IS NOT NULL
GROUP BY analysis->'structure'->>'narrative_structure'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- Pacing Performance
DROP VIEW IF EXISTS pacing_performance CASCADE;
CREATE VIEW pacing_performance AS
SELECT
    analysis->'structure'->>'pacing' as pacing,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND niche_mode = 'entertainment'
  AND analysis->'structure'->>'pacing' IS NOT NULL
GROUP BY analysis->'structure'->>'pacing'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- Loop Friendly Performance
DROP VIEW IF EXISTS loop_performance CASCADE;
CREATE VIEW loop_performance AS
SELECT
    CASE
        WHEN (analysis->'structure'->>'loop_friendly')::boolean THEN 'Yes'
        ELSE 'No'
    END as loop_friendly,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND niche_mode = 'entertainment'
  AND analysis->'structure'->>'loop_friendly' IS NOT NULL
GROUP BY loop_friendly
ORDER BY avg_views_per_day DESC NULLS LAST;

-- Editing Pace Performance
DROP VIEW IF EXISTS editing_pace_performance CASCADE;
CREATE VIEW editing_pace_performance AS
SELECT
    analysis->'visual'->>'editing_pace' as editing_pace,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND niche_mode = 'entertainment'
  AND analysis->'visual'->>'editing_pace' IS NOT NULL
GROUP BY analysis->'visual'->>'editing_pace'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- Worst Combinations (Bottom performers)
DROP VIEW IF EXISTS worst_combinations CASCADE;
CREATE VIEW worst_combinations AS
SELECT
    analysis->'structure'->>'format_type' as format_type,
    analysis->'hook'->>'hook_technique' as hook_technique,
    analysis->'visual'->>'setting_type' as setting_type,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND niche_mode = 'entertainment'
GROUP BY
    analysis->'structure'->>'format_type',
    analysis->'hook'->>'hook_technique',
    analysis->'visual'->>'setting_type'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day ASC NULLS LAST
LIMIT 15;

-- ============================================================
-- ACCOUNT ANALYSIS VIEWS (From migration 005)
-- ============================================================

-- Account summary with latest stats (entertainment only)
DROP VIEW IF EXISTS account_summary CASCADE;
CREATE VIEW account_summary AS
SELECT
    a.id,
    a.platform,
    a.username,
    a.display_name,
    a.follower_count,
    a.following_count,
    a.post_count,
    a.is_verified,
    a.is_private,
    a.status,
    a.last_scraped_at,
    a.last_analyzed_at,
    a.created_at,
    COUNT(p.id) as scraped_video_count,
    COUNT(p.id) FILTER (WHERE p.analysis IS NOT NULL) as analyzed_video_count,
    AVG((p.analysis->'hook'->>'hook_strength')::numeric) as avg_hook,
    AVG((p.analysis->'trends'->>'viral_potential_score')::numeric) as avg_viral,
    AVG((p.analysis->'replicability'->>'replicability_score')::numeric) as avg_replicability
FROM accounts a
LEFT JOIN posts p ON p.account_id = a.id AND p.niche_mode = 'entertainment'
GROUP BY a.id;

-- Account comparison view (entertainment only)
DROP VIEW IF EXISTS account_vs_dataset CASCADE;
CREATE VIEW account_vs_dataset AS
WITH dataset_avgs AS (
    SELECT
        AVG((analysis->'hook'->>'hook_strength')::numeric) as dataset_hook,
        AVG((analysis->'trends'->>'viral_potential_score')::numeric) as dataset_viral,
        AVG((analysis->'replicability'->>'replicability_score')::numeric) as dataset_replicate,
        COUNT(*) as dataset_count
    FROM posts
    WHERE analysis IS NOT NULL
      AND niche_mode = 'entertainment'
)
SELECT
    a.id as account_id,
    a.platform,
    a.username,
    AVG((p.analysis->'hook'->>'hook_strength')::numeric) as account_hook,
    AVG((p.analysis->'trends'->>'viral_potential_score')::numeric) as account_viral,
    AVG((p.analysis->'replicability'->>'replicability_score')::numeric) as account_replicate,
    COUNT(p.id) FILTER (WHERE p.analysis IS NOT NULL) as account_video_count,
    d.dataset_hook,
    d.dataset_viral,
    d.dataset_replicate,
    d.dataset_count,
    AVG((p.analysis->'hook'->>'hook_strength')::numeric) - d.dataset_hook as hook_diff,
    AVG((p.analysis->'trends'->>'viral_potential_score')::numeric) - d.dataset_viral as viral_diff,
    AVG((p.analysis->'replicability'->>'replicability_score')::numeric) - d.dataset_replicate as replicate_diff
FROM accounts a
LEFT JOIN posts p ON p.account_id = a.id AND p.niche_mode = 'entertainment'
CROSS JOIN dataset_avgs d
GROUP BY a.id, a.platform, a.username, d.dataset_hook, d.dataset_viral, d.dataset_replicate, d.dataset_count;

-- ============================================================
-- PART 3: DATA ENGINEERING VIEWS
-- ============================================================
-- Fix views to filter on niche_mode instead of niche column

-- Educational Metrics (for data engineering content)
DROP VIEW IF EXISTS educational_metrics CASCADE;
CREATE VIEW educational_metrics AS
SELECT
    COUNT(*) as total_videos,
    COUNT(*) FILTER (WHERE analysis IS NOT NULL) as analyzed_videos,
    COUNT(DISTINCT author_username) as unique_creators,
    AVG((analysis->'educational'->>'explanation_clarity')::numeric) as avg_clarity,
    AVG((analysis->'educational'->>'technical_depth')::numeric) as avg_depth,
    AVG((analysis->'educational'->>'educational_value')::numeric) as avg_edu_value,
    AVG((analysis->'educational'->>'practical_applicability')::numeric) as avg_practical
FROM posts
WHERE niche_mode = 'data_engineering';

-- Tool Coverage (which tools are mentioned most)
DROP VIEW IF EXISTS tool_coverage CASCADE;
CREATE VIEW tool_coverage AS
SELECT
    tool,
    COUNT(*) as mention_count,
    AVG((analysis->'educational'->>'educational_value')::numeric) as avg_edu_value
FROM posts,
     jsonb_array_elements_text(analysis->'educational'->'tools_mentioned') as tool
WHERE analysis IS NOT NULL
  AND niche_mode = 'data_engineering'
GROUP BY tool
ORDER BY mention_count DESC;

-- Content Type Distribution
DROP VIEW IF EXISTS content_type_distribution CASCADE;
CREATE VIEW content_type_distribution AS
SELECT
    analysis->'educational'->>'content_type' as content_type,
    COUNT(*) as video_count,
    AVG((analysis->'educational'->>'educational_value')::numeric) as avg_edu_value
FROM posts
WHERE analysis IS NOT NULL
  AND niche_mode = 'data_engineering'
  AND analysis->'educational'->>'content_type' IS NOT NULL
GROUP BY analysis->'educational'->>'content_type'
ORDER BY video_count DESC;

-- Teaching Techniques
DROP VIEW IF EXISTS teaching_techniques CASCADE;
CREATE VIEW teaching_techniques AS
SELECT
    technique,
    COUNT(*) as video_count,
    AVG((analysis->'educational'->>'explanation_clarity')::numeric) as avg_clarity
FROM posts,
     jsonb_array_elements_text(analysis->'educational'->'teaching_techniques') as technique
WHERE analysis IS NOT NULL
  AND niche_mode = 'data_engineering'
GROUP BY technique
ORDER BY video_count DESC;

-- Skill Level Distribution
DROP VIEW IF EXISTS skill_level_distribution CASCADE;
CREATE VIEW skill_level_distribution AS
SELECT
    analysis->'educational'->>'skill_level' as skill_level,
    COUNT(*) as video_count,
    AVG((analysis->'educational'->>'educational_value')::numeric) as avg_edu_value
FROM posts
WHERE analysis IS NOT NULL
  AND niche_mode = 'data_engineering'
  AND analysis->'educational'->>'skill_level' IS NOT NULL
GROUP BY analysis->'educational'->>'skill_level'
ORDER BY video_count DESC;

-- Data Engineering Context
DROP VIEW IF EXISTS data_engineering_context CASCADE;
CREATE VIEW data_engineering_context AS
SELECT
    analysis->'data_engineering'->>'cloud_platform' as cloud_platform,
    analysis->'data_engineering'->>'data_layer' as data_layer,
    COUNT(*) as video_count
FROM posts
WHERE analysis IS NOT NULL
  AND niche_mode = 'data_engineering'
  AND (analysis->'data_engineering'->>'cloud_platform' IS NOT NULL
       OR analysis->'data_engineering'->>'data_layer' IS NOT NULL)
GROUP BY
    analysis->'data_engineering'->>'cloud_platform',
    analysis->'data_engineering'->>'data_layer'
ORDER BY video_count DESC;

-- Data Engineering Summary (parallel to strategic_summary for entertainment)
DROP VIEW IF EXISTS data_engineering_summary CASCADE;
CREATE VIEW data_engineering_summary AS
SELECT
    COUNT(*) as total_videos,
    COUNT(*) FILTER (WHERE analysis IS NOT NULL) as analyzed_videos,
    MIN(posted_at) as earliest_video,
    MAX(posted_at) as latest_video,
    ROUND(AVG((analysis->'educational'->>'explanation_clarity')::numeric), 2) as avg_clarity,
    ROUND(AVG((analysis->'educational'->>'technical_depth')::numeric), 2) as avg_depth,
    ROUND(AVG((analysis->'educational'->>'educational_value')::numeric), 2) as avg_edu_value,
    ROUND(AVG((analysis->'educational'->>'practical_applicability')::numeric), 2) as avg_practical
FROM posts
WHERE niche_mode = 'data_engineering';

-- ============================================================
-- VERIFICATION QUERIES (run after migration)
-- ============================================================
-- SELECT niche_mode, COUNT(*) as count FROM posts GROUP BY niche_mode;
-- SELECT * FROM analytics_summary;  -- Should show only entertainment data
-- SELECT * FROM educational_metrics;  -- Should show only data_engineering data
