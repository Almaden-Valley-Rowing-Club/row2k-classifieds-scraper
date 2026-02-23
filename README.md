# row2k Classifieds Scraper

Scrapes the [row2k boats-for-sale classifieds](https://www.row2k.com/classifieds/index.cfm?view_cat&cat=boats-for-sale) page, detects new listings, and prints notifications for new California listings.

Runs hourly via GitHub Actions. State is persisted in `seen_listings.json` (committed to git) so new listings are only reported once.

## Usage

```sh
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
uv run main.py
```

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `DISCORD_WEBHOOK_URL` | Yes | Discord webhook URL for posting new listing notifications |

## How it works

1. Fetches the row2k boats-for-sale category page
2. Parses listing ID, title, location, date, description, and URL from each listing
3. Compares against `seen_listings.json` to identify new listings
4. Prints and sends a Discord notification for new listings in California
5. Saves updated state (capped at 50 entries, oldest evicted first)

## License

[BSD 3-Clause](LICENSE)
