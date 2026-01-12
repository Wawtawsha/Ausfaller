-- Add niche tracking to posts table
-- This allows grouping videos by business vertical for better analytics

-- Add niche column (broad category like "dj_nightlife", "bars_restaurants", "events_parties")
ALTER TABLE posts ADD COLUMN IF NOT EXISTS niche VARCHAR(100);

-- Add source_hashtag column (the specific hashtag used to find this video)
ALTER TABLE posts ADD COLUMN IF NOT EXISTS source_hashtag VARCHAR(255);

-- Create index for niche filtering
CREATE INDEX IF NOT EXISTS idx_posts_niche ON posts(niche);

-- Create index for source_hashtag filtering
CREATE INDEX IF NOT EXISTS idx_posts_source_hashtag ON posts(source_hashtag);

-- Create analytics view grouped by niche
CREATE OR REPLACE VIEW niche_analytics AS
SELECT
    niche,
    COUNT(*) as video_count,
    COUNT(*) FILTER (WHERE analysis IS NOT NULL) as analyzed_count,
    AVG((analysis->'hook'->>'hook_strength')::numeric) as avg_hook_strength,
    AVG((analysis->'trends'->>'viral_potential_score')::numeric) as avg_viral_potential,
    AVG((analysis->'replicability'->>'replicability_score')::numeric) as avg_replicability
FROM posts
WHERE niche IS NOT NULL
GROUP BY niche
ORDER BY video_count DESC;

-- Create view for hashtag performance within niches
CREATE OR REPLACE VIEW hashtag_performance AS
SELECT
    niche,
    source_hashtag,
    COUNT(*) as video_count,
    AVG((analysis->'hook'->>'hook_strength')::numeric) as avg_hook_strength,
    AVG((analysis->'trends'->>'viral_potential_score')::numeric) as avg_viral_potential,
    AVG((analysis->'replicability'->>'replicability_score')::numeric) as avg_replicability
FROM posts
WHERE source_hashtag IS NOT NULL AND analysis IS NOT NULL
GROUP BY niche, source_hashtag
ORDER BY niche, video_count DESC;
