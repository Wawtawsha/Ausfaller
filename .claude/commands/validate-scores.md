---
allowed-tools: Read, Grep, Glob, mcp__plugin_supabase_supabase__execute_sql
description: Validate and correct AI-generated scores using Claude meta-analysis
---

# /validate-scores - Score Validation via Claude Meta-Analysis

Performs batch validation of Gemini-generated scores by having Claude cross-check scores against observable factors in the analysis data.

## Overview

This command uses Claude (you) to perform meta-analysis of Gemini's scoring, identifying inconsistencies between:
- `hook_strength` vs hook_type, technique, timing
- `viral_potential_score` vs trends, engagement, relatability
- `replicability_score` vs budget, difficulty, time

## Step 1: Fetch Recent Analyses for Validation

Query posts that have analyses but may have inconsistent scores:

```sql
-- Get recent analyses with all relevant fields for validation
SELECT
    id,
    video_url,
    views,
    likes,

    -- Hook data
    analysis->'hook'->>'hook_type' as hook_type,
    analysis->'hook'->>'hook_technique' as hook_technique,
    analysis->'hook'->>'hook_timing_seconds' as hook_timing,
    analysis->'hook'->>'hook_text' as hook_text,
    (analysis->'hook'->>'hook_strength')::int as hook_strength,

    -- Trends data
    analysis->'trends'->>'trend_lifecycle_stage' as lifecycle,
    analysis->'trends'->>'meme_potential' as meme_potential,
    analysis->'trends'->>'remix_potential' as remix_potential,
    analysis->'trends'->>'format_originality' as originality,
    analysis->'trends'->'viral_factors' as viral_factors,
    (analysis->'trends'->>'viral_potential_score')::int as viral_score,

    -- Engagement data
    analysis->'engagement'->'share_triggers' as share_triggers,

    -- Emotion data
    (analysis->'emotion'->>'relatability_score')::int as relatability_score,

    -- Replicability data
    analysis->'replicability'->>'budget_estimate' as budget,
    analysis->'replicability'->>'difficulty_level' as difficulty,
    analysis->'replicability'->>'time_investment' as time_investment,
    (analysis->'replicability'->>'replicability_score')::int as replicability_score

FROM posts
WHERE analysis IS NOT NULL
ORDER BY scraped_at DESC
LIMIT 50;
```

## Step 2: Validation Rules

Apply these validation rules to identify score inconsistencies:

### Hook Strength Rules
| Condition | Expected Score |
|-----------|----------------|
| No hook_type or "none" | Max 3 |
| hook_technique in (open_loop, curiosity_gap, pattern_interrupt, controversy) | Min 6 |
| hook_timing > 3 seconds | Max 5 |
| hook_type = "text" but no hook_text | Max 4 |
| hook_timing <= 1s with technique | Min 5 |

### Viral Potential Rules
| Condition | Expected Score |
|-----------|----------------|
| lifecycle in (declining, dead) | Max 5 |
| lifecycle in (peak, growing) | Min 5 |
| meme_potential AND remix_potential | Min 6 |
| originality = "copy" | Max 4 |
| viral_factors count >= 4 | Min 5 |
| share_triggers count >= 3 | Min 5 |
| viral_score > relatability_score + 3 | Max relatability + 3 |

### Replicability Rules
| Condition | Expected Score |
|-----------|----------------|
| budget in (high, over_200) | Max 4 |
| budget = "free" | Min 7 |
| budget = "low" | Min 6 |
| difficulty = "expert" | Max 3 |
| difficulty = "difficult" | Max 5 |
| difficulty = "easy" | Min 7 |
| difficulty = "moderate" | Max 7 |
| time_investment in (over_8hrs, 8+hrs) | Max 4 |
| time_investment in (3-8hrs) | Max 6 |
| time_investment in (under_1hr, <1hr) | Min 7 |

## Step 3: Generate Validation Report

For each post, check all rules and create a report:

```markdown
## Score Validation Report
**Generated:** {timestamp}
**Posts Analyzed:** {count}

### Summary
- Posts with inconsistencies: {count}
- Hook strength issues: {count}
- Viral potential issues: {count}
- Replicability issues: {count}

### Detailed Findings

#### Post: {video_url}
| Score | Current | Expected | Rule Violated |
|-------|---------|----------|---------------|
| hook_strength | 8 | Max 5 | Late hook (timing > 3s) |
| viral_score | 7 | Max 4 | Direct copy |

---
[Repeat for each post with issues]
```

## Step 4: Apply Corrections (Optional)

If corrections should be applied, generate UPDATE statements:

```sql
-- Update hook_strength for post {id}
UPDATE posts
SET analysis = jsonb_set(
    analysis,
    '{hook,hook_strength}',
    '{new_score}'::jsonb
)
WHERE id = '{id}';

-- Update viral_potential_score for post {id}
UPDATE posts
SET analysis = jsonb_set(
    analysis,
    '{trends,viral_potential_score}',
    '{new_score}'::jsonb
)
WHERE id = '{id}';

-- Update replicability_score for post {id}
UPDATE posts
SET analysis = jsonb_set(
    analysis,
    '{replicability,replicability_score}',
    '{new_score}'::jsonb
)
WHERE id = '{id}';
```

## Step 5: Verify Corrections

After applying corrections, run the score calibration view:

```sql
SELECT * FROM score_calibration;
```

Expected: Higher-performing videos (viral, high tiers) should have higher average scores than lower-performing videos.

## Output

1. **Validation Report** - Markdown showing all inconsistencies found
2. **Correction SQL** - Optional UPDATE statements to fix scores
3. **Calibration Check** - Before/after comparison of score distributions

## Important Notes

- This is a META-ANALYSIS - you (Claude) are reviewing Gemini's work
- No Gemini tokens are used - this is pure Claude reasoning
- Focus on rule violations, not aesthetic judgments
- When in doubt, flag for human review rather than auto-correct
- Track which posts were corrected for audit trail
