-- Analytics views for dashboard
-- Run these in Supabase SQL Editor or via migration

-- Hook analysis aggregation
CREATE OR REPLACE VIEW hook_trends AS
SELECT
    analysis->'hook'->>'hook_type' as hook_type,
    analysis->'hook'->>'hook_technique' as hook_technique,
    AVG((analysis->'hook'->>'hook_strength')::int) as avg_strength,
    COUNT(*) as video_count
FROM posts
WHERE analysis IS NOT NULL
  AND analysis->'hook'->>'hook_type' IS NOT NULL
GROUP BY 1, 2
ORDER BY video_count DESC;

-- Audio trends
CREATE OR REPLACE VIEW audio_trends AS
SELECT
    analysis->'audio'->>'sound_category' as category,
    (analysis->'audio'->>'is_trending_sound')::boolean as is_trending,
    COUNT(*) as count
FROM posts
WHERE analysis IS NOT NULL
  AND analysis->'audio'->>'sound_category' IS NOT NULL
GROUP BY 1, 2
ORDER BY count DESC;

-- Visual style distribution
CREATE OR REPLACE VIEW visual_trends AS
SELECT
    analysis->'visual'->>'visual_style' as style,
    analysis->'visual'->>'setting_type' as setting,
    COUNT(*) as count
FROM posts
WHERE analysis IS NOT NULL
  AND analysis->'visual'->>'visual_style' IS NOT NULL
GROUP BY 1, 2
ORDER BY count DESC;

-- Viral potential distribution
CREATE OR REPLACE VIEW viral_trends AS
SELECT
    (analysis->'trends'->>'viral_potential_score')::int as viral_score,
    analysis->'trends'->>'trend_lifecycle_stage' as lifecycle_stage,
    COUNT(*) as count
FROM posts
WHERE analysis IS NOT NULL
  AND analysis->'trends'->>'viral_potential_score' IS NOT NULL
GROUP BY 1, 2
ORDER BY viral_score DESC;

-- Replicability leaderboard (top videos to replicate)
CREATE OR REPLACE VIEW replicability_leaderboard AS
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
  AND (analysis->'replicability'->>'replicability_score')::int >= 6
ORDER BY replicability_score DESC, viral_score DESC
LIMIT 100;

-- Summary stats view
CREATE OR REPLACE VIEW analytics_summary AS
SELECT
    COUNT(*) as total_videos,
    COUNT(CASE WHEN analysis IS NOT NULL THEN 1 END) as analyzed_videos,
    AVG((analysis->'hook'->>'hook_strength')::int) as avg_hook_strength,
    AVG((analysis->'trends'->>'viral_potential_score')::int) as avg_viral_potential,
    AVG((analysis->'replicability'->>'replicability_score')::int) as avg_replicability,
    MIN(scraped_at) as first_scraped,
    MAX(scraped_at) as last_scraped
FROM posts;

-- Top viral factors (extracted from array)
CREATE OR REPLACE VIEW viral_factors_breakdown AS
SELECT
    factor,
    COUNT(*) as count
FROM posts,
     jsonb_array_elements_text(analysis->'trends'->'viral_factors') as factor
WHERE analysis IS NOT NULL
GROUP BY factor
ORDER BY count DESC;
