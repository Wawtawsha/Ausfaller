"""
Live metrics for Gemini batch analysis.
Run: python analysis_metrics.py
"""
import json
import re
from pathlib import Path
from datetime import datetime

# Files
LOG_FILE = Path('batch_analysis_output.log')
RESULTS_DIR = Path(r'C:\Users\steph\.social-scraper\cache\batch')

def get_metrics():
    # Find latest results file
    results_files = list(RESULTS_DIR.glob('combined_analysis_*_results.jsonl'))
    results_file = max(results_files, key=lambda f: f.stat().st_mtime) if results_files else None

    # Count completed
    completed = 0
    if results_file and results_file.exists():
        with open(results_file) as f:
            completed = sum(1 for _ in f)

    # Parse log
    total = 11761
    current = 0
    last_video = ''
    start_time = None

    if LOG_FILE.exists():
        with open(LOG_FILE, encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        for line in lines:
            if 'Starting analysis of' in line:
                start_time = line[:19]
            match = re.search(r'\[(\d+)/(\d+)\]', line)
            if match:
                current = int(match.group(1))
                total = int(match.group(2))
            if 'Analyzing:' in line:
                last_video = line.split('Analyzing:')[-1].strip()[:60]

    # Calculate
    pct = (current / total * 100) if total > 0 else 0
    remaining = total - current
    eta_hours = remaining * 12 / 3600

    # Parse results for quality metrics
    clarity_scores, depth_scores, value_scores = [], [], []
    ms_stack_count = 0
    platforms = {'tiktok': 0, 'youtube_shorts': 0}
    authors = set()

    if results_file and results_file.exists():
        with open(results_file) as f:
            for line in f:
                try:
                    r = json.loads(line)
                    analysis = r.get('analysis', {})
                    edu = analysis.get('educational', {})
                    de = analysis.get('data_engineering', {})

                    if edu.get('explanation_clarity'):
                        clarity_scores.append(edu['explanation_clarity'])
                    if edu.get('technical_depth'):
                        depth_scores.append(edu['technical_depth'])
                    if edu.get('educational_value'):
                        value_scores.append(edu['educational_value'])
                    if de.get('microsoft_stack'):
                        ms_stack_count += 1

                    source = r.get('source', '')
                    if source in platforms:
                        platforms[source] += 1
                    authors.add(r.get('author', 'unknown'))
                except:
                    pass

    # Display
    print('=' * 60)
    print('GEMINI BATCH ANALYSIS - LIVE METRICS')
    print(f'  {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 60)
    print()
    print(f'PROGRESS: {current:,} / {total:,} ({pct:.1f}%)')
    bar = '#' * int(pct/2) + '-' * (50-int(pct/2))
    print(f'[{bar}]')
    print()
    print(f'  Completed:  {completed:,} results saved')
    print(f'  Remaining:  {remaining:,}')
    print(f'  ETA:        ~{eta_hours:.1f} hours')
    print()
    print(f'Last: {last_video}')
    print()
    print('-' * 60)
    print('QUALITY METRICS')
    print('-' * 60)
    n = len(clarity_scores)
    if n > 0:
        print(f'  Clarity:    {sum(clarity_scores)/n:.1f}/10 (avg)')
        print(f'  Depth:      {sum(depth_scores)/n:.1f}/10 (avg)') if depth_scores else None
        print(f'  Edu Value:  {sum(value_scores)/len(value_scores):.1f}/10 (avg)') if value_scores else None
        print(f'  MS Stack:   {ms_stack_count}/{n} ({ms_stack_count/n*100:.0f}%)')
        print()
        print(f'  Platforms:  YouTube={platforms["youtube_shorts"]}, TikTok={platforms["tiktok"]}')
        print(f'  Authors:    {len(authors)} unique')
    print('=' * 60)

if __name__ == '__main__':
    get_metrics()
