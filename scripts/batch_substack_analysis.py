"""
Batch Substack Analysis - Step through posts in Claude conversation.

This script helps Claude analyze Substack posts in manageable chunks.
Run commands:
    python scripts/batch_substack_analysis.py status     # Check progress
    python scripts/batch_substack_analysis.py next       # Get next chunk to analyze
    python scripts/batch_substack_analysis.py save       # Save analysis (reads from stdin)
    python scripts/batch_substack_analysis.py summary    # Show analysis summary
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# Config
SUBSTACK_DIR = Path(r'C:\Users\steph\.social-scraper\cache\substack')
RESULTS_DIR = Path(r'C:\Users\steph\.social-scraper\cache\substack\analysis')
PROGRESS_FILE = RESULTS_DIR / 'progress.json'
CHUNK_SIZE = 20  # Posts per chunk for Claude to analyze

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_posts():
    """Load latest scraped posts."""
    files = list(SUBSTACK_DIR.glob('substack_posts_*.json'))
    if not files:
        return []
    latest = max(files, key=lambda f: f.stat().st_mtime)
    with open(latest, encoding='utf-8') as f:
        data = json.load(f)
    return data.get('posts', [])


def load_progress():
    """Load analysis progress."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {'analyzed_indices': [], 'last_updated': None}


def save_progress(progress):
    """Save analysis progress."""
    progress['last_updated'] = datetime.now().isoformat()
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)


def get_status():
    """Show current analysis status."""
    posts = load_posts()
    progress = load_progress()
    analyzed = len(progress['analyzed_indices'])
    total = len(posts)
    remaining = total - analyzed

    print("=" * 60)
    print("SUBSTACK ANALYSIS PROGRESS")
    print("=" * 60)
    print(f"Total posts:     {total}")
    print(f"Analyzed:        {analyzed}")
    print(f"Remaining:       {remaining}")
    print(f"Progress:        {analyzed/total*100:.1f}%" if total > 0 else "N/A")
    print(f"Chunks remaining: {(remaining + CHUNK_SIZE - 1) // CHUNK_SIZE}")
    print("=" * 60)

    # Show results files
    result_files = list(RESULTS_DIR.glob('analysis_chunk_*.json'))
    if result_files:
        print(f"\nResult files: {len(result_files)}")
        for f in sorted(result_files):
            with open(f) as fp:
                data = json.load(fp)
            print(f"  {f.name}: {len(data)} posts")


def get_next_chunk():
    """Get next chunk of posts to analyze."""
    posts = load_posts()
    progress = load_progress()
    analyzed_set = set(progress['analyzed_indices'])

    # Find next unanalyzed posts
    chunk = []
    chunk_indices = []
    for i, post in enumerate(posts):
        if i not in analyzed_set:
            chunk.append(post)
            chunk_indices.append(i)
            if len(chunk) >= CHUNK_SIZE:
                break

    if not chunk:
        print("All posts analyzed!")
        return

    chunk_num = len(progress['analyzed_indices']) // CHUNK_SIZE + 1
    total_chunks = (len(posts) + CHUNK_SIZE - 1) // CHUNK_SIZE

    print(f"# CHUNK {chunk_num}/{total_chunks} ({len(chunk)} posts)")
    print(f"# Indices: {chunk_indices[0]}-{chunk_indices[-1]}")
    print()
    print("Analyze these posts and return JSON array. Use this format:")
    print('{"index": N, "title": "...", "publication": "...", "analysis": {...}, "summary": "..."}')
    print()
    print("=" * 60)

    import re
    for i, post in enumerate(chunk):
        idx = chunk_indices[i]
        content = post.get('content_html', '') or post.get('description', '')
        content = re.sub(r'<[^>]+>', ' ', content)
        content = re.sub(r'\s+', ' ', content).strip()[:1500]

        print(f"\n## [{idx}] {post.get('title', 'Untitled')}")
        print(f"Publication: {post.get('publication_title', post.get('publication', '?'))}")
        print(f"Author: {post.get('author', '?')}")
        print(f"URL: {post.get('url', '')}")
        print(f"Date: {post.get('published_at', '?')}")
        print(f"\n{content}...")

    print("\n" + "=" * 60)
    print(f"\nAfter analyzing, run: python scripts/batch_substack_analysis.py save")
    print("Then paste the JSON array.")


def save_results():
    """Save analysis results from stdin."""
    print("Paste JSON array of analysis results, then press Ctrl+Z (Windows) or Ctrl+D (Unix) and Enter:")

    try:
        input_text = sys.stdin.read()
        results = json.loads(input_text)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return
    except KeyboardInterrupt:
        print("\nCancelled.")
        return

    if not isinstance(results, list):
        print("Expected JSON array")
        return

    # Update progress
    progress = load_progress()
    for r in results:
        if 'index' in r:
            if r['index'] not in progress['analyzed_indices']:
                progress['analyzed_indices'].append(r['index'])

    progress['analyzed_indices'].sort()
    save_progress(progress)

    # Save results to chunk file
    chunk_num = len(list(RESULTS_DIR.glob('analysis_chunk_*.json'))) + 1
    result_file = RESULTS_DIR / f'analysis_chunk_{chunk_num:03d}.json'
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {len(results)} results to {result_file}")
    print(f"Progress: {len(progress['analyzed_indices'])} posts analyzed")


def show_summary():
    """Show summary of all analyzed posts."""
    result_files = sorted(RESULTS_DIR.glob('analysis_chunk_*.json'))
    if not result_files:
        print("No results yet.")
        return

    all_results = []
    for f in result_files:
        with open(f) as fp:
            all_results.extend(json.load(fp))

    # Aggregate stats
    content_types = {}
    skill_levels = {}
    ms_stack_count = 0
    platforms = {}
    total_clarity = 0
    total_practical = 0

    for r in all_results:
        a = r.get('analysis', {})

        ct = a.get('content_type', 'unknown')
        content_types[ct] = content_types.get(ct, 0) + 1

        sl = a.get('skill_level', 'unknown')
        skill_levels[sl] = skill_levels.get(sl, 0) + 1

        if a.get('microsoft_stack'):
            ms_stack_count += 1

        cp = a.get('cloud_platform', 'unknown')
        platforms[cp] = platforms.get(cp, 0) + 1

        total_clarity += a.get('explanation_clarity', 0)
        total_practical += a.get('practical_applicability', 0)

    n = len(all_results)

    print("=" * 60)
    print(f"SUBSTACK ANALYSIS SUMMARY ({n} posts)")
    print("=" * 60)

    print(f"\nAvg Clarity:      {total_clarity/n:.1f}/10")
    print(f"Avg Practical:    {total_practical/n:.1f}/10")
    print(f"MS Stack:         {ms_stack_count}/{n} ({ms_stack_count/n*100:.0f}%)")

    print("\nContent Types:")
    for ct, count in sorted(content_types.items(), key=lambda x: -x[1]):
        print(f"  {ct}: {count}")

    print("\nSkill Levels:")
    for sl, count in sorted(skill_levels.items(), key=lambda x: -x[1]):
        print(f"  {sl}: {count}")

    print("\nCloud Platforms:")
    for cp, count in sorted(platforms.items(), key=lambda x: -x[1]):
        print(f"  {cp}: {count}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python batch_substack_analysis.py <command>")
        print("Commands: status, next, save, summary")
        return

    cmd = sys.argv[1].lower()

    if cmd == 'status':
        get_status()
    elif cmd == 'next':
        get_next_chunk()
    elif cmd == 'save':
        save_results()
    elif cmd == 'summary':
        show_summary()
    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
