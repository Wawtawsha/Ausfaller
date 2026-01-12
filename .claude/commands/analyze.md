---
allowed-tools: Read, Grep, Glob, mcp__plugin_supabase_supabase__execute_sql
description: Generate strategic trend analysis from aggregated video data
---

# /analyze - Strategic Trend Analysis

Generate a comprehensive strategic analysis of the video dataset using pre-aggregated statistics.

## Overview

This skill generates a multi-section strategic analysis by:
1. Fetching pre-aggregated statistics from Supabase views (NOT raw posts)
2. Generating each section independently to avoid context overflow
3. Storing the complete analysis to the database with versioning

## Step 1: Fetch Aggregated Data

Query each aggregation view to get the statistical foundation:

```sql
-- Get overall summary
SELECT * FROM strategic_summary;

-- Get format performance (which content formats work best)
SELECT * FROM format_performance;

-- Get hook technique performance
SELECT * FROM hook_technique_performance;

-- Get hook type performance
SELECT * FROM hook_type_performance;

-- Get audio type performance
SELECT * FROM audio_type_performance;

-- Get visual style performance
SELECT * FROM visual_style_performance;

-- Get setting performance
SELECT * FROM setting_performance;

-- Get duration performance
SELECT * FROM duration_performance;

-- Get emotion performance
SELECT * FROM emotion_performance;

-- Get humor type performance
SELECT * FROM humor_performance;

-- Get production quality performance
SELECT * FROM production_quality_performance;

-- Get camera type performance
SELECT * FROM camera_performance;

-- Get face visibility performance
SELECT * FROM face_visibility_performance;

-- Get narrative structure performance
SELECT * FROM narrative_performance;

-- Get pacing performance
SELECT * FROM pacing_performance;

-- Get loop friendliness performance
SELECT * FROM loop_performance;

-- Get editing pace performance
SELECT * FROM editing_pace_performance;

-- Get top combinations (format + hook + setting)
SELECT * FROM top_combinations LIMIT 15;

-- Get worst combinations (to avoid)
SELECT * FROM worst_combinations LIMIT 10;

-- Get saturation metrics (RED FLAGS - overused but underperforming)
SELECT * FROM saturation_metrics;

-- Get gap opportunities (OPPORTUNITIES - underrepresented but high performing)
SELECT * FROM gap_opportunities;
```

## Step 2: Generate Analysis Sections

Generate each section based on the aggregated data. Each section should be actionable and data-driven.

### Section 1: Executive Summary
- Total videos analyzed
- Date range of data
- Key finding highlights (1-2 sentences each):
  - Top performing format
  - Most effective hook technique
  - Best setting (may contradict expectations)
  - Optimal duration
  - Biggest myth busted (e.g., loop performance, production quality)
  - Biggest opportunity gap
  - Main red flag to avoid

### Section 2: Complete Metric Breakdown

For EACH of the following categories, create a table showing:
- Value name
- Video count
- Avg views/day
- % vs average (calculated)

Categories to cover:
1. **Format Type** (from format_performance)
2. **Hook Type** (from hook_type_performance)
3. **Hook Technique** (from hook_technique_performance)
4. **Setting** (from setting_performance)
5. **Visual Style** (from visual_style_performance)
6. **Audio Category** (from audio_type_performance)
7. **Duration** (from duration_performance)
8. **Primary Emotion** (from emotion_performance)
9. **Humor Type** (from humor_performance)
10. **Production Quality** (from production_quality_performance)
11. **Camera Type** (from camera_performance)
12. **Face Visibility** (from face_visibility_performance)
13. **Narrative Structure** (from narrative_performance)
14. **Pacing** (from pacing_performance)
15. **Loop Friendly** (from loop_performance)
16. **Editing Pace** (from editing_pace_performance)

For each category, add a brief "Critical Finding" statement highlighting the biggest insight.

### Section 3: Content Templates (Replicable Playbook)

For the top 5 combinations from `top_combinations`, create detailed templates:

For each template:
- **Template Name**: Creative descriptive name (e.g., "The Kitchen Confessional", "The Outdoor Story Arc")
- **Format**: The format_type from data
- **Hook Technique**: The hook_technique from data
- **Setting**: The setting_type from data
- **Audio**: Recommended audio based on audio_type_performance
- **Duration**: Recommended duration based on duration_performance
- **Performance**: avg_views_per_day
- **Difficulty**: Based on typical_difficulty or inferred from combination complexity
- **Why It Works**: 2-3 sentences explaining the psychology/mechanics of why this combination succeeds
- **How to Replicate**: 4-5 step-by-step instructions for creating content using this template
- **Example Hook Script**: Write a sample opening line/hook

### Section 4: Top Performing Combinations
From `top_combinations` view, show the top 10:
- Format + Hook Technique + Setting
- Video count
- Avg views/day
- Why this combination likely works

### Section 5: Worst Performing Combinations (Avoid)
From `worst_combinations` view, show the bottom 10:
- Format + Hook Technique + Setting
- Video count
- Avg views/day
- Why to avoid

### Section 6: The Complete Winning Formula
Create a summary table showing:
- For each metric category: Best choice vs Worst choice with views/day for each
- This is the quick-reference guide

### Section 7: Key Insights
Numbered list of 10-15 actionable insights distilled from the data, formatted as:
- **Bold action statement.** Supporting data and reasoning.

Examples:
- **Tell stories, don't teach.** Storytime is 26x better than tutorials.
- **Create curiosity, not relatability.** Open loops beat relatable pain by 16x.

### Section 8: Gaps & Opportunities (BLUE OCEAN)
From `gap_opportunities` view - these are underrepresented but high-performing areas:

For each gap, provide:
- **Category**: (format, hook, audio, setting, etc.)
- **Value**: The specific underused technique
- **Video Count**: Shows it's underrepresented (small sample)
- **Performance vs Average**: Shows it outperforms (high %)
- **Opportunity Score**: Performance % / Video count (higher = better opportunity)
- **How to Exploit**: Specific, actionable recommendation for using this gap

Format as a table plus detailed recommendations.

### Section 9: Red Flags (Saturated/Overused) - AVOID
From `saturation_metrics` view - these are overused AND underperforming:

For each red flag, provide:
- **Category**: (format, hook, etc.)
- **Value**: The saturated technique
- **Market Share %**: How common it is
- **Performance vs Average**: How badly it underperforms
- **Saturation Score**: Market share % / Performance ratio (higher = more saturated)
- **Why It's Failing**: Analysis of why this technique no longer works
- **How to Differentiate**: If you must use it, how to stand out

Format as a table plus detailed analysis.

## Step 3: Store to Database

After generating all sections, store the analysis:

```sql
-- Get next version number
SELECT COALESCE(MAX(version), 0) + 1 as next_version FROM strategic_analyses;

-- Insert the analysis
INSERT INTO strategic_analyses (
    version,
    video_count,
    analyzed_count,
    date_range_start,
    date_range_end,
    sections,
    full_markdown,
    generation_time_seconds
) VALUES (
    <next_version>,
    <video_count from summary>,
    <analyzed_count from summary>,
    <earliest_video from summary>,
    <latest_video from summary>,
    '<sections as JSON>',
    '<full markdown>',
    <generation_time>
);
```

## Step 4: Save to File

Write the analysis to `analysis/LATEST_ANALYSIS.md` so it can be committed to git.

## Output Format

The final analysis should be rendered as markdown with clear headers:

```markdown
# TikTok Bar/Bartender Content Trend Analysis
**Generated: {timestamp} (Analysis {version} - COMPREHENSIVE TIME-NORMALIZED)**

---

## Executive Summary

- **{KEY FINDING 1}** {details}
- **{KEY FINDING 2}** {details}
...

---

## Dataset Overview

| Metric | Value |
|--------|-------|
| Total Posts | {count} |
| Analyzed Posts | {count} |
| Posts with Engagement + Date | {count} |
| Date Range | {range} |
| Average Views/Day | {avg} |

---

## FORMAT TYPE (Biggest Differentiator)

| Format | Count | Views/Day | vs. Average |
|--------|-------|-----------|-------------|
...

**Critical Finding:** {insight}

---

[Continue for all 16 metric categories...]

---

## CONTENT TEMPLATES (Replicable Playbook)

### Template 1: {Creative Name}
- **Format**: {format_type}
- **Hook Technique**: {hook_technique}
- **Setting**: {setting_type}
- **Audio**: {recommended audio}
- **Duration**: {recommended duration}
- **Performance**: {avg_views_per_day} views/day
- **Difficulty**: {difficulty level}

**Why It Works**: {2-3 sentences on psychology/mechanics}

**How to Replicate**:
1. {Step 1}
2. {Step 2}
3. {Step 3}
4. {Step 4}

**Example Hook Script**: "{sample opening line}"

[Repeat for top 5 templates]

---

## TOP PERFORMING COMBINATIONS

| Format | Technique | Setting | Count | Views/Day |
...

---

## WORST PERFORMING COMBINATIONS (Avoid)

| Format | Technique | Setting | Count | Views/Day |
...

---

## THE COMPLETE WINNING FORMULA

| Element | Best Choice | Views/Day | Worst Choice | Views/Day |
...

---

## KEY INSIGHTS

1. **{Insight}** {Supporting data}
...

---

## GAPS & OPPORTUNITIES (Blue Ocean)

| Category | Value | Count | Performance vs Avg | Opportunity |
|----------|-------|-------|-------------------|-------------|
...

### How to Exploit These Gaps:
{Detailed recommendations for each gap}

---

## RED FLAGS (Saturated - Avoid)

| Category | Value | Market Share | Performance vs Avg | Risk |
|----------|-------|--------------|-------------------|------|
...

### Why These Are Failing:
{Analysis of each red flag with differentiation strategies}

---

## Methodology

- {total} total posts scraped from TikTok
- {analyzed} posts analyzed by Gemini AI
- {with_data} posts with engagement data and posting dates
- Date range: {range}
- Primary metric: Views per day since posting
- Formula: `views / days_since_posting`

This normalizes for the unfair advantage older content has in accumulating views.

---

*Analysis {version} based on {count} videos with comprehensive time-normalized metrics, {date}.*
```

## Important Notes

- NEVER fetch raw posts - always use the aggregation views
- Each section should be self-contained and actionable
- Include specific numbers and percentages
- Focus on "what to do" not just "what the data shows"
- Calculate "vs. Average" percentages using the overall avg_views_per_day from strategic_summary
- Highlight counter-intuitive findings (e.g., bar is worst setting for bar content)
- Store both structured sections (JSON) and full_markdown for flexibility
- Write to `analysis/LATEST_ANALYSIS.md` for version control
