-- Expanded Metric Views for Complete Analysis
-- Adds views for all metrics tracked in LATEST_ANALYSIS.md

-- ============================================
-- SETTING PERFORMANCE
-- ============================================
CREATE OR REPLACE VIEW setting_performance AS
SELECT
    analysis->'visual'->>'setting_type' as setting_type,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND analysis->'visual'->>'setting_type' IS NOT NULL
GROUP BY analysis->'visual'->>'setting_type'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- ============================================
-- DURATION PERFORMANCE
-- ============================================
CREATE OR REPLACE VIEW duration_performance AS
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
  AND analysis->'structure'->>'estimated_duration_seconds' IS NOT NULL
GROUP BY duration_bucket
ORDER BY avg_views_per_day DESC NULLS LAST;

-- ============================================
-- EMOTION PERFORMANCE
-- ============================================
CREATE OR REPLACE VIEW emotion_performance AS
SELECT
    analysis->'emotion'->>'primary_emotion' as primary_emotion,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'emotion'->>'relatability_score')::numeric), 2) as avg_relatability
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND analysis->'emotion'->>'primary_emotion' IS NOT NULL
GROUP BY analysis->'emotion'->>'primary_emotion'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- ============================================
-- HUMOR TYPE PERFORMANCE
-- ============================================
CREATE OR REPLACE VIEW humor_performance AS
SELECT
    analysis->'emotion'->>'humor_type' as humor_type,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND analysis->'emotion'->>'humor_type' IS NOT NULL
GROUP BY analysis->'emotion'->>'humor_type'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- ============================================
-- PRODUCTION QUALITY PERFORMANCE
-- ============================================
CREATE OR REPLACE VIEW production_quality_performance AS
SELECT
    analysis->'production'->>'overall_quality' as production_quality,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'replicability'->>'replicability_score')::numeric), 2) as avg_replicability
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND analysis->'production'->>'overall_quality' IS NOT NULL
GROUP BY analysis->'production'->>'overall_quality'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- ============================================
-- CAMERA TYPE PERFORMANCE
-- ============================================
CREATE OR REPLACE VIEW camera_performance AS
SELECT
    analysis->'visual'->>'camera_type' as camera_type,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND analysis->'visual'->>'camera_type' IS NOT NULL
GROUP BY analysis->'visual'->>'camera_type'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- ============================================
-- FACE VISIBILITY PERFORMANCE
-- ============================================
CREATE OR REPLACE VIEW face_visibility_performance AS
SELECT
    analysis->'visual'->>'face_visibility' as face_visibility,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND analysis->'visual'->>'face_visibility' IS NOT NULL
GROUP BY analysis->'visual'->>'face_visibility'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- ============================================
-- NARRATIVE STRUCTURE PERFORMANCE
-- ============================================
CREATE OR REPLACE VIEW narrative_performance AS
SELECT
    analysis->'structure'->>'narrative_structure' as narrative_structure,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND analysis->'structure'->>'narrative_structure' IS NOT NULL
GROUP BY analysis->'structure'->>'narrative_structure'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- ============================================
-- PACING PERFORMANCE
-- ============================================
CREATE OR REPLACE VIEW pacing_performance AS
SELECT
    analysis->'structure'->>'pacing' as pacing,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND analysis->'structure'->>'pacing' IS NOT NULL
GROUP BY analysis->'structure'->>'pacing'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- ============================================
-- LOOP FRIENDLY PERFORMANCE
-- ============================================
CREATE OR REPLACE VIEW loop_performance AS
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
  AND analysis->'structure'->>'loop_friendly' IS NOT NULL
GROUP BY loop_friendly
ORDER BY avg_views_per_day DESC NULLS LAST;

-- ============================================
-- EDITING PACE PERFORMANCE
-- ============================================
CREATE OR REPLACE VIEW editing_pace_performance AS
SELECT
    analysis->'visual'->>'editing_pace' as editing_pace,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day,
    ROUND(AVG((analysis->'trends'->>'viral_potential_score')::numeric), 2) as avg_viral_score
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
  AND analysis->'visual'->>'editing_pace' IS NOT NULL
GROUP BY analysis->'visual'->>'editing_pace'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day DESC NULLS LAST;

-- ============================================
-- WORST COMBINATIONS (Bottom performers)
-- ============================================
CREATE OR REPLACE VIEW worst_combinations AS
SELECT
    analysis->'structure'->>'format_type' as format_type,
    analysis->'hook'->>'hook_technique' as hook_technique,
    analysis->'visual'->>'setting_type' as setting_type,
    COUNT(*) as video_count,
    ROUND(AVG(COALESCE(views, 0) / GREATEST(EXTRACT(EPOCH FROM (NOW() - posted_at)) / 86400, 1))::numeric, 0) as avg_views_per_day
FROM posts
WHERE analysis IS NOT NULL
  AND posted_at IS NOT NULL
GROUP BY
    analysis->'structure'->>'format_type',
    analysis->'hook'->>'hook_technique',
    analysis->'visual'->>'setting_type'
HAVING COUNT(*) >= 3
ORDER BY avg_views_per_day ASC NULLS LAST
LIMIT 15;
