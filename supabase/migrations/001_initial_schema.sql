-- Social Scraper Schema
-- Run this in Supabase SQL Editor

-- Enable vector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- Platform enum
CREATE TYPE platform_type AS ENUM ('tiktok', 'instagram');

-- Content type enum
CREATE TYPE content_type AS ENUM ('video', 'image', 'carousel', 'reel');

-- Main posts table
CREATE TABLE posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform platform_type NOT NULL,
    platform_id VARCHAR(255) NOT NULL,
    content_type content_type NOT NULL DEFAULT 'video',

    -- Source info
    video_url TEXT NOT NULL,
    author_username VARCHAR(255),
    author_followers INTEGER,

    -- Content
    caption TEXT,
    hashtags TEXT[],

    -- Engagement metrics
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,4),

    -- Media
    thumbnail_url TEXT,
    local_file_path TEXT,
    file_size_bytes BIGINT,
    duration_seconds FLOAT,

    -- Timestamps
    posted_at TIMESTAMP WITH TIME ZONE,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Gemini analysis (stored as JSONB for flexibility)
    analysis JSONB,
    analyzed_at TIMESTAMP WITH TIME ZONE,

    -- For semantic search (optional)
    embedding vector(768),

    UNIQUE(platform, platform_id)
);

-- Clients table (for multi-tenant support)
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(255),
    target_audience TEXT,
    competitors TEXT[],
    tracked_hashtags TEXT[],
    tracked_accounts TEXT[],
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Scrape jobs (for tracking pipeline runs)
CREATE TABLE scrape_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),

    -- Job config
    platform platform_type NOT NULL,
    hashtag VARCHAR(255) NOT NULL,
    target_count INTEGER DEFAULT 30,

    -- Status
    status VARCHAR(50) DEFAULT 'pending',

    -- Results
    videos_found INTEGER DEFAULT 0,
    videos_downloaded INTEGER DEFAULT 0,
    videos_analyzed INTEGER DEFAULT 0,

    -- Timing
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,

    error TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Trends table (aggregated insights)
CREATE TABLE trends (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform platform_type NOT NULL,
    trend_type VARCHAR(50) NOT NULL, -- 'hashtag', 'sound', 'format', 'topic'
    name VARCHAR(255) NOT NULL,

    -- Metrics
    post_count INTEGER DEFAULT 0,
    avg_engagement DECIMAL(10,2),
    growth_rate DECIMAL(5,2),

    -- Timing
    first_seen TIMESTAMP WITH TIME ZONE,
    last_seen TIMESTAMP WITH TIME ZONE,

    -- Analysis
    analysis TEXT,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(platform, trend_type, name)
);

-- Indexes for performance
CREATE INDEX idx_posts_platform ON posts(platform);
CREATE INDEX idx_posts_scraped_at ON posts(scraped_at DESC);
CREATE INDEX idx_posts_hashtags ON posts USING GIN(hashtags);
CREATE INDEX idx_posts_author ON posts(author_username);
CREATE INDEX idx_posts_analyzed ON posts(analyzed_at) WHERE analyzed_at IS NOT NULL;

CREATE INDEX idx_scrape_jobs_status ON scrape_jobs(status);
CREATE INDEX idx_scrape_jobs_created ON scrape_jobs(created_at DESC);

CREATE INDEX idx_trends_platform ON trends(platform, trend_type);
CREATE INDEX idx_trends_updated ON trends(updated_at DESC);

-- Row Level Security (enable for production)
-- ALTER TABLE posts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE scrape_jobs ENABLE ROW LEVEL SECURITY;

-- Functions

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER clients_updated_at
    BEFORE UPDATE ON clients
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trends_updated_at
    BEFORE UPDATE ON trends
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
