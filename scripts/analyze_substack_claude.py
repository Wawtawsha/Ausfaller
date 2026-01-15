"""
Prepare Substack posts for Claude analysis.

This script loads scraped Substack data and outputs:
1. Formatted post data
2. Analysis prompt for Claude

Usage:
    python scripts/analyze_substack_claude.py
    python scripts/analyze_substack_claude.py --file substack_posts_20260115.json
    python scripts/analyze_substack_claude.py --output analysis_input.md
"""
import json
import sys
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path(r'C:\Users\steph\.social-scraper\cache\substack')

CLAUDE_ANALYSIS_PROMPT = '''
# Substack Content Analysis - Data Engineering Niche

You are analyzing newsletter posts from data engineering Substack publications. Analyze each post and provide structured insights.

## Analysis Framework

For each post, evaluate:

### 1. Content Classification
- **content_type**: tutorial | opinion | news | case_study | career_advice | tool_review | architecture_deep_dive | interview
- **skill_level**: beginner | intermediate | advanced | all_levels
- **estimated_read_time**: minutes (based on content length)

### 2. Technical Relevance (Data Engineering)
- **microsoft_stack**: true/false - Does it cover Microsoft Fabric, Azure Data Factory, Power BI, Synapse, etc.?
- **cloud_platform**: azure | aws | gcp | databricks | snowflake | multi_cloud | agnostic
- **data_layer**: ingestion | transformation | storage | orchestration | visualization | governance | multiple
- **tools_mentioned**: List specific tools (dbt, Airflow, Spark, Fabric, etc.)
- **architecture_patterns**: List patterns discussed (medallion, data mesh, lakehouse, etc.)

### 3. Educational Quality
- **explanation_clarity**: 1-10 (How well does it explain concepts?)
- **practical_applicability**: 1-10 (Can readers apply this immediately?)
- **code_examples**: true/false (Does it include code?)
- **diagrams_visuals**: true/false (Does it include architecture diagrams?)

### 4. Engagement Signals
- **headline_strength**: 1-10 (Is the title compelling?)
- **hook_quality**: 1-10 (Does the intro pull you in?)
- **actionable_takeaways**: List 1-3 key takeaways

### 5. Brand Safety & Sponsorship Fit
- **brand_safety_score**: 1-10 (Suitable for professional/enterprise audiences?)
- **sponsorship_categories**: List fitting sponsor types (cloud_vendors, data_tools, training_platforms, etc.)
- **tone**: professional | casual | academic | provocative

## Output Format

Return JSON array with analysis for each post:

```json
[
  {
    "post_id": "<url or index>",
    "title": "<post title>",
    "publication": "<substack name>",
    "analysis": {
      "content_type": "tutorial",
      "skill_level": "intermediate",
      "estimated_read_time": 8,
      "microsoft_stack": true,
      "cloud_platform": "azure",
      "data_layer": ["transformation", "orchestration"],
      "tools_mentioned": ["Microsoft Fabric", "dbt", "Dataflow Gen2"],
      "architecture_patterns": ["medallion"],
      "explanation_clarity": 8,
      "practical_applicability": 7,
      "code_examples": true,
      "diagrams_visuals": true,
      "headline_strength": 7,
      "hook_quality": 6,
      "actionable_takeaways": [
        "Use Dataflow Gen2 for incremental loads",
        "Medallion architecture fits Fabric well"
      ],
      "brand_safety_score": 9,
      "sponsorship_categories": ["cloud_vendors", "data_tools"],
      "tone": "professional"
    },
    "summary": "<2-3 sentence summary of the post>"
  }
]
```

## Posts to Analyze

'''


def load_latest_scrape():
    """Load the most recent Substack scrape."""
    files = list(OUTPUT_DIR.glob('substack_posts_*.json'))
    if not files:
        return None
    latest = max(files, key=lambda f: f.stat().st_mtime)
    with open(latest, encoding='utf-8') as f:
        return json.load(f), latest


def format_posts_for_claude(data: dict, max_posts: int = 50) -> str:
    """Format posts for Claude analysis input."""
    posts = data.get('posts', [])[:max_posts]

    formatted = []
    for i, post in enumerate(posts, 1):
        # Strip HTML from content, keep first 2000 chars
        content = post.get('content_html', '') or post.get('description', '')
        # Simple HTML stripping
        import re
        content = re.sub(r'<[^>]+>', ' ', content)
        content = re.sub(r'\s+', ' ', content).strip()[:2000]

        formatted.append(f"""
---
## Post {i}: {post.get('title', 'Untitled')}

**Publication:** {post.get('publication_title', post.get('publication', 'Unknown'))}
**Author:** {post.get('author', 'Unknown')}
**URL:** {post.get('url', '')}
**Published:** {post.get('published_at', 'Unknown')}

**Content Preview:**
{content}...

**Embedded Videos:** {len(post.get('embedded_videos', []))}
""")

    return '\n'.join(formatted)


def generate_analysis_input(output_file: str = None, max_posts: int = 50):
    """Generate the full analysis input for Claude."""
    result = load_latest_scrape()
    if not result:
        print("No Substack scrape found. Run scrape_substack.py first.")
        return

    data, source_file = result
    posts_formatted = format_posts_for_claude(data, max_posts)

    full_input = f"""# Substack Analysis Input
Generated: {datetime.now().isoformat()}
Source: {source_file.name}
Total posts available: {data.get('total_posts', 0)}
Posts included: {min(max_posts, len(data.get('posts', [])))}

{CLAUDE_ANALYSIS_PROMPT}

{posts_formatted}

---
# END OF POSTS

Please analyze each post according to the framework above and return the JSON array.
"""

    if output_file:
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_input)
        print(f"Analysis input saved to: {output_path}")
        print(f"Copy this file content to Claude for analysis.")
    else:
        print(full_input)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Prepare Substack data for Claude analysis')
    parser.add_argument('--file', type=str, help='Specific scrape file to use')
    parser.add_argument('--output', type=str, help='Output file path (default: print to stdout)')
    parser.add_argument('--max-posts', type=int, default=50, help='Max posts to include')
    args = parser.parse_args()

    generate_analysis_input(args.output, args.max_posts)


if __name__ == "__main__":
    main()
