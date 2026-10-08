#!/usr/bin/env python3
"""
update-events.py — fetch the club's public events RSS feed and turn it into
a small JSON file the app can load as a same-origin static file (no CORS
problem, unlike fetching the RSS directly from the browser).

Runs stdlib-only so the GitHub Action needs no pip install step.
"""
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape

FEED_URL = "https://blackwatersailingclub.org.uk/events/RSS"
OUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "events.json")
MAX_EVENTS = 12          # don't let the app screen grow unbounded
EXCERPT_LEN = 220        # characters of plain-text summary kept per event


def strip_html(raw: str) -> str:
    """A short plain-text excerpt, not a reproduction of the full write-up."""
    text = re.sub(r"<[^>]+>", " ", raw or "")
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > EXCERPT_LEN:
        text = text[:EXCERPT_LEN].rsplit(" ", 1)[0] + "…"
    return text


def strip_date_suffix(title: str) -> str:
    """The feed repeats the date in the title, e.g. 'Thing (26/09/2026)' —
    the app shows the date itself, so drop the repeated bit."""
    return re.sub(r"\s*\(\d{1,2}/\d{1,2}/\d{4}\)\s*$", "", title or "").strip()


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "bsc-sailing-calendar-bot/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def parse(xml_bytes: bytes) -> list:
    root = ET.fromstring(xml_bytes)
    items = []
    for item in root.findall("./channel/item")[:MAX_EVENTS]:
        title_raw = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if not re.match(r"^https://([\w-]+\.)*blackwatersailingclub\.org\.uk(/|$)", link):
            link = ""  # only ever link to the club's own site, over https
        pub_raw = (item.findtext("pubDate") or "").strip()
        desc_raw = item.findtext("description") or ""
        try:
            dt = parsedate_to_datetime(pub_raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            continue  # skip anything we can't date, rather than guess
        items.append({
            "title": strip_date_suffix(title_raw),
            "date": dt.astimezone(timezone.utc).strftime("%Y-%m-%d"),
            "time": dt.astimezone(timezone.utc).strftime("%H:%M"),
            "hasTime": not (dt.hour == 0 and dt.minute == 0),  # all-day items post at 00:00
            "excerpt": strip_html(desc_raw),
            "link": link,
        })
    items.sort(key=lambda x: (x["date"], x["time"]))
    return items


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else None  # allow a local file for testing
    xml_bytes = open(src, "rb").read() if src else fetch(FEED_URL)
    events = parse(xml_bytes)

    if not events:
        # A feed outage or a change to the club's page structure shouldn't
        # silently wipe what's already shown in the app — leave the existing
        # file alone and flag it loudly in the Action's log instead.
        print("::warning::Parsed 0 events from the feed — leaving events.json unchanged. "
              "Check the feed URL and scripts/update-events.py still match the feed's shape.")
        sys.exit(0)

    out = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "https://blackwatersailingclub.org.uk/events",
        "events": events,
    }
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"Wrote {len(events)} events to {OUT_FILE}")


if __name__ == "__main__":
    main()
