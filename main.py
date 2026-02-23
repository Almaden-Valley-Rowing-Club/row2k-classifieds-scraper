import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup

from notifications import send_discord_notification

BASE_URL = "https://www.row2k.com"
CATEGORY_URL = f"{BASE_URL}/classifieds/index.cfm?view_cat&cat=boats-for-sale"
STATE_FILE = Path("seen_listings.json")
MAX_SEEN_LISTINGS = 50

HEADERS = {
    "User-Agent": "row2k-classifieds-scraper/0.1 (+https://github.com)"
}


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def save_state(state):
    if len(state) > MAX_SEEN_LISTINGS:
        sorted_keys = sorted(state, key=lambda k: state[k].get("first_seen", ""))
        excess = len(state) - MAX_SEEN_LISTINGS
        for key in sorted_keys[:excess]:
            del state[key]
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")


def scrape_listings():
    resp = requests.get(CATEGORY_URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    feed = soup.find("div", class_="article-feed")
    if not feed:
        print("Error: Could not find article-feed div. The page structure may have changed.")
        sys.exit(1)

    listings = []
    for article in feed.find_all("article", class_="article"):
        midhead = article.find("span", class_="midhead-feat")
        if not midhead:
            continue
        link = midhead.find("a", href=True)
        if not link:
            continue

        href = link["href"]
        parsed = parse_qs(urlparse(href).query)
        listing_id = parsed.get("listing", [None])[0]
        if not listing_id:
            # Try bare query string (e.g. "index.cfm?listing=12345")
            qs = urlparse(href).query
            if qs.startswith("listing="):
                listing_id = qs.split("=", 1)[1]
        if not listing_id:
            continue

        location = None
        date = None
        for span in article.find_all("span", style=True):
            if span.find_parent("span", class_="midhead-feat"):
                continue
            style = span["style"]
            if "font-style" in style:
                date = span.get_text(strip=True)
            elif "font-size" in style:
                location = span.get_text(strip=True)

        title = link.get_text(strip=True)
        p = article.find("p", class_="wraptext")
        description = p.get_text(strip=True) if p else None
        url = f"{BASE_URL}/classifieds/{href}" if not href.startswith("http") else href

        listings.append({
            "id": listing_id,
            "title": title,
            "location": location,
            "date": date,
            "description": description,
            "url": url,
        })

    return listings


def main():
    state = load_state()
    listings = scrape_listings()

    if not listings:
        print("No listings found on page.")
        return

    new_count = 0
    now = datetime.now(timezone.utc).isoformat()

    for listing in listings:
        lid = listing["id"]
        if lid in state:
            continue

        state[lid] = {
            "title": listing["title"],
            "location": listing["location"],
            "date": listing["date"],
            "first_seen": now,
        }

        location = listing["location"] or ""
        if ", CA" not in location:
            continue

        new_count += 1
        print(f"New listing: {listing['title']}")
        if listing["location"]:
            print(f"  Location: {listing['location']}")
        if listing["date"]:
            print(f"  Date: {listing['date']}")
        if listing["description"]:
            print(f"  Description: {listing['description'][:120]}")
        print(f"  URL: {listing['url']}")
        print()

        send_discord_notification(listing)

    if new_count == 0:
        print("No new listings found.")

    save_state(state)


if __name__ == "__main__":
    main()
