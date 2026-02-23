import os
import sys

import requests

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
if not DISCORD_WEBHOOK_URL:
    print("Error: DISCORD_WEBHOOK_URL environment variable is not set.")
    sys.exit(1)


def send_discord_notification(listing):
    lines = [f"**New listing: {listing['title']}**"]
    if listing["location"]:
        lines.append(f"Location: {listing['location']}")
    if listing["date"]:
        lines.append(f"Date: {listing['date']}")
    if listing["description"]:
        lines.append(f"Description: {listing['description'][:120]}")
    lines.append(listing["url"])

    payload = {"content": "\n".join(lines)}
    resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
    resp.raise_for_status()
