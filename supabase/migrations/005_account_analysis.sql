-- Account Analysis Feature
-- Allows tracking specific accounts, comparing their performance against the dataset

-- ============================================
-- ACCOUNTS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform platform_type NOT NULL,
    username VARCHAR(255) NOT NULL,

    -- Profile metadata (populated on scrape)
    display_name VARCHAR(255),
    bio TEXT,
    profile_picture_url TEXT,
    follower_count INTEGER,
    following_count INTEGER,
    post_count INTEGER,
    is_verified BOOLEAN DEFAULT FALSE,
    is_private BOOLEAN DEFAULT FALSE,

    -- Tracking status
    status VARCHAR(50) DEFAULT 'pending',  -- pending, active, analyzing, error
    last_scraped_at TIMESTAMP WITH TIME ZONE,
    last_analyzed_at TIMESTAMP WITH TIME ZONE,
    scrape_error TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(platform, username)
);

-- Index for quick lookups
CREATE INDEX IF NOT EXISTS idx_accounts_platform_username ON accounts(platform, username);
CREATE INDEX IF NOT EXISTS idx_accounts_status ON accounts(status);

-- ============================================
-- LINK POSTS TO ACCOUNTS
-- ============================================

-- Add account_id to posts table
ALTER TABLE posts ADD COLUMN IF NOT EXISTS account_id UUID REFERENCES accounts(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_posts_account_id ON posts(account_id);

-- ============================================
-- ACCOUNT SNAPSHOTS (Historical tracking)
-- ============================================

CREATE TABLE IF NOT EXISTS account_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    snapshot_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Video counts at time of snapshot
    video_count INTEGER DEFAULT 0,
    analyzed_count INTEGER DEFAULT 0,

    -- Average scores
    avg_hook_strength NUMERIC(4,2),
    avg_viral_potential NUMERIC(4,2),
    avg_replicability NUMERIC(4,2),

    -- Content pattern distributions (JSONB for flexibility)
    hook_types JSONB,           -- {"question": 5, "visual": 3, "statement": 2}
    audio_categories JSONB,     -- {"trending_audio": 4, "voiceover": 3}
    visual_styles JSONB,        -- {"casual": 5, "polished": 2}

    -- Comparison data (vs dataset at snapshot time)
    dataset_comparison JSONB,   -- {"hook_diff": +0.5, "viral_diff": -0.2}
    percentile_ranks JSONB,     -- {"hook": 75, "viral": 60, "replicability": 80}

    -- Generated insights
    recommendations JSONB,      -- ["Try question hooks", "Increase production quality"]
    gaps JSONB                  -- ["Not using trending audio", "Missing curiosity gap hooks"]
);

CREATE INDEX IF NOT EXISTS idx_account_snapshots_account ON account_snapshots(account_id);
CREATE INDEX IF NOT EXISTS idx_account_snapshots_time ON account_snapshots(snapshot_at DESC);

-- ============================================
-- VIEWS
-- ============================================

-- Account summary with latest stats
CREATE OR REPLACE VIEW account_summary AS
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
LEFT JOIN posts p ON p.account_id = a.id
GROUP BY a.id;

-- Account comparison view (joins with dataset averages)
CREATE OR REPLACE VIEW account_vs_dataset AS
WITH dataset_avgs AS (
    SELECT
        AVG((analysis->'hook'->>'hook_strength')::numeric) as dataset_hook,
        AVG((analysis->'trends'->>'viral_potential_score')::numeric) as dataset_viral,
        AVG((analysis->'replicability'->>'replicability_score')::numeric) as dataset_replicate,
        COUNT(*) as dataset_count
    FROM posts
    WHERE analysis IS NOT NULL
)
SELECT
    a.id as account_id,
    a.platform,
    a.username,
    -- Account averages
    AVG((p.analysis->'hook'->>'hook_strength')::numeric) as account_hook,
    AVG((p.analysis->'trends'->>'viral_potential_score')::numeric) as account_viral,
    AVG((p.analysis->'replicability'->>'replicability_score')::numeric) as account_replicate,
    COUNT(p.id) FILTER (WHERE p.analysis IS NOT NULL) as account_video_count,
    -- Dataset averages
    d.dataset_hook,
    d.dataset_viral,
    d.dataset_replicate,
    d.dataset_count,
    -- Differences
    AVG((p.analysis->'hook'->>'hook_strength')::numeric) - d.dataset_hook as hook_diff,
    AVG((p.analysis->'trends'->>'viral_potential_score')::numeric) - d.dataset_viral as viral_diff,
    AVG((p.analysis->'replicability'->>'replicability_score')::numeric) - d.dataset_replicate as replicate_diff
FROM accounts a
LEFT JOIN posts p ON p.account_id = a.id
CROSS JOIN dataset_avgs d
GROUP BY a.id, a.platform, a.username, d.dataset_hook, d.dataset_viral, d.dataset_replicate, d.dataset_count;
