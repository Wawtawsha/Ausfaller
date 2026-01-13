-- Strategic Analysis Automation
-- Pre-aggregated views to reduce context size + versioned storage

-- ============================================
-- STRATEGIC ANALYSES TABLE (Versioned Storage)
-- ============================================

CREATE TABLE IF NOT EXISTS strategic_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version INTEGER NOT NULL,

    -- Metadata
    video_count INTEGER NOT NULL DEFAULT 0,
    analyzed_count INTEGER NOT NULL DEFAULT 0,
    date_range_start TIMESTAMP WITH TIME ZONE,
    date_range_end TIMESTAMP WITH TIME ZONE,

    -- Sections stored as structured JSONB
    sections JSONB NOT NULL DEFAULT '{}',

    -- Full rendered markdown
    full_markdown TEXT,

    -- Generation metadata
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    generation_time_seconds FLOAT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_strategic_analyses_version ON strategic_analyses(version DESC);
CREATE INDEX IF NOT EXISTS idx_strategic_analyses_generated ON strategic_analyses(generated_at DESC);

-- ============================================
-- AGGREGATION VIEWS
-- ============================================

-- Format Performance: Which content formats perform best?
CREATE OR REPLACE VIEW format_performance AS
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
  AND analysis->'structure'->>'format_type' IS NOT NULL
GROUP BY analysis->'structure'->>'format_type'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- Hook Technique Performance: Which hook techniques work best?
CREATE OR REPLACE VIEW hook_technique_performance AS
SELECT
    analysis->'hook'->>'hook_technique' as hook_technique,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'hook'->>'hook_strength')::numeric), 2) as avg_hook_strength,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND analysis->'hook'->>'hook_technique' IS NOT NULL
GROUP BY analysis->'hook'->>'hook_technique'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- Hook Type Performance: Question vs Statement vs Visual etc
CREATE OR REPLACE VIEW hook_type_performance AS
SELECT
    analysis->'hook'->>'hook_type' as hook_type,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'hook'->>'hook_strength')::numeric), 2) as avg_hook_strength
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND analysis->'hook'->>'hook_type' IS NOT NULL
GROUP BY analysis->'hook'->>'hook_type'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- Audio Type Performance
CREATE OR REPLACE VIEW audio_type_performance AS
SELECT
    analysis->'audio'->>'audio_type' as audio_type,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND analysis->'audio'->>'audio_type' IS NOT NULL
GROUP BY analysis->'audio'->>'audio_type'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- Visual Style Performance
CREATE OR REPLACE VIEW visual_style_performance AS
SELECT
    analysis->'visual'->>'visual_style' as visual_style,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND analysis->'visual'->>'visual_style' IS NOT NULL
GROUP BY analysis->'visual'->>'visual_style'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- Top Combinations: Best performing format + hook + setting combos
CREATE OR REPLACE VIEW top_combinations AS
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
GROUP BY
    analysis->'structure'->>'format_type',
    analysis->'hook'->>'hook_technique',
    analysis->'visual'->>'setting_type',
    analysis->'audio'->>'audio_type',
    analysis->'replicability'->>'difficulty'
HAVING COUNT(*) >= 2
ORDER BY avg_views_per_day DESC NULLS LAST
LIMIT 25;

-- Saturation Metrics: Overused techniques that underperform (RED FLAGS)
CREATE OR REPLACE VIEW saturation_metrics AS
WITH overall_stats AS (
    SELECT
        AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)) as avg_views,
        COUNT(*) as total_videos
    FROM posts
    WHERE analysis IS NOT NULL AND posted_at IS NOT NULL
),
hook_saturation AS (
    SELECT
        'hook_technique' as category,
        analysis->'hook'->>'hook_technique' as value,
        COUNT(*) as video_count,
        ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
        ROUND((COUNT(*)::float / (SELECT total_videos FROM overall_stats) * 100)::numeric, 1) as market_share_pct
    FROM posts
    WHERE analysis IS NOT NULL AND posted_at IS NOT NULL
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
    WHERE analysis IS NOT NULL AND posted_at IS NOT NULL
    GROUP BY analysis->'structure'->>'format_type'
    HAVING COUNT(*) >= 10
       AND AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)) < (SELECT avg_views FROM overall_stats)
)
SELECT * FROM hook_saturation
UNION ALL
SELECT * FROM format_saturation
ORDER BY video_count DESC;

-- Gap Opportunities: Underrepresented but high-performing (OPPORTUNITIES)
CREATE OR REPLACE VIEW gap_opportunities AS
WITH overall_stats AS (
    SELECT
        AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)) as avg_views,
        COUNT(*) as total_videos
    FROM posts
    WHERE analysis IS NOT NULL AND posted_at IS NOT NULL
),
format_gaps AS (
    SELECT
        'format_type' as category,
        analysis->'structure'->>'format_type' as value,
        COUNT(*) as video_count,
        ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
        ROUND((AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1)) / NULLIF((SELECT avg_views FROM overall_stats), 0) * 100)::numeric, 0) as performance_vs_avg_pct
    FROM posts
    WHERE analysis IS NOT NULL AND posted_at IS NOT NULL
    GROUP BY analysis->'structure'->>'format_type'
    HAVING COUNT(*) BETWEEN 3 AND 30  -- Low representation
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
    WHERE analysis IS NOT NULL AND posted_at IS NOT NULL
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
    WHERE analysis IS NOT NULL AND posted_at IS NOT NULL
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

-- Overall Dataset Stats (for summary)
CREATE OR REPLACE VIEW strategic_summary AS
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
WHERE posted_at IS NOT NULL;
