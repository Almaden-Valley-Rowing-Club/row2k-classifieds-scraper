# row2k Classifieds Scraper

## What this project does

Scrapes the [row2k boats-for-sale classifieds](https://www.row2k.com/classifieds/index.cfm?view_cat&cat=boats-for-sale) page, detects new listings, and prints notifications for new California listings. Runs on a schedule via GitHub Actions.

## Project structure

- `main.py` — Scraper script
- `notifications.py` — Discord webhook notification logic
- `seen_listings.json` — Persisted state tracking seen listings (committed to git, auto-created on first run)
- `pyproject.toml` — Project metadata and dependencies
- `.github/workflows/scrape.yml` — GitHub Actions workflow (hourly cron + manual dispatch)

## How it works

1. Fetches the row2k boats-for-sale category page
2. Parses listings from `<article class="article">` elements inside `div.article-feed`
3. Extracts listing ID, title, location, date, description, and URL
4. Compares against `seen_listings.json` — any listing ID not already in state is new
5. Prints and sends a Discord notification for new listings located in California (`, CA` in location)
6. All new listings (regardless of location) are added to state to avoid re-triggering
7. State is capped at 50 entries (`MAX_SEEN_LISTINGS`), oldest by `first_seen` evicted first

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `DISCORD_WEBHOOK_URL` | Yes | Discord webhook URL for posting new listing notifications |

## Running locally

```sh
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
uv run main.py
```

## Dependencies

- Python >= 3.14
- `requests` — HTTP client
- `beautifulsoup4` — HTML parsing

## Key constants in main.py

- `CATEGORY_URL` — The row2k classifieds category page URL
- `MAX_SEEN_LISTINGS` — Cap on state file entries (default: 50)
- `STATE_FILE` — Path to `seen_listings.json`

## GitHub Actions workflow

- Runs every hour and on manual dispatch
- Uses `astral-sh/setup-uv` for fast dependency installation
- `DISCORD_WEBHOOK_URL` must be set as a repository secret
- Commits and pushes `seen_listings.json` if it changed

## HTML selectors (row2k page structure)

- Container: `div.article-feed`
- Each listing: `article.article`
- Title/link: `span.midhead-feat > a[href]` (href contains `listing=XXXXX`)
- Location: `<span>` with `font-size` in style attribute (but not `font-style`)
- Date: `<span>` with `font-style` in style attribute
- Description: `p.wraptext`
