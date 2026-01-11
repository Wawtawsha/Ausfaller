# n8n Workflow Examples

Import these workflows into n8n to integrate with the Social Scraper API.

## Prerequisites

1. Social Scraper API running at `http://localhost:8080`
2. n8n running (local Docker or Cloud)

## Workflows

### 1. Scheduled Scrape (`scheduled_scrape.json`)

Automatically scrapes a hashtag every 6 hours.

**How it works:**
1. Triggers every 6 hours
2. Calls `/pipeline` to start extraction → download → analysis
3. Polls `/pipeline/{job_id}` until complete
4. Outputs summary

**Customization:**
- Change `hoursInterval` for different schedule
- Modify `hashtag` and `platform` in Start Pipeline node
- Add Slack/Email notification at the end

### 2. Webhook Triggered (`webhook_scrape.json`)

On-demand scraping via HTTP webhook.

**Usage:**
```bash
curl -X POST https://your-n8n.com/webhook/scrape \
  -H "Content-Type: application/json" \
  -d '{"platform": "tiktok", "hashtag": "nightlife", "count": 20}'
```

**Response:**
Returns the job_id immediately. Poll `/pipeline/{job_id}` for results.

## Configuration

Update the API URL in each workflow if not running locally:
- Find "Start Pipeline" and "Check Job Status" nodes
- Change `http://localhost:8080` to your deployed API URL

## Adding to n8n

1. Open n8n
2. Click Import Workflow
3. Paste JSON or upload file
4. Activate the workflow

## Extending Workflows

Ideas for additional nodes:
- **Supabase**: Store results directly in database
- **Slack**: Send notifications when analysis is complete
- **Google Sheets**: Export trending content to spreadsheet
- **Email**: Weekly digest of top-performing content
- **AI nodes**: Additional processing with Claude/GPT
