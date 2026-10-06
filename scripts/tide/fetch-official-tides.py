#!/usr/bin/env python3
"""
fetch-official-tides.py: fetch the next 7 days of published high waters and
record them in tides-official.csv at the repo root.

Two sources (official-tides.json, "source"):
  club       (default) the club website's next-7-days table: National
             Oceanography Centre predictions for the BSC pontoon, the same
             source and reference point as the printed programme. No key needed.
  admiralty  the ADMIRALTY UK Tidal API (Discovery tier, free; needs a key).

When the source is "club" and an ADMIRALTY key and station are also set up,
the ADMIRALTY figures are fetched too and recorded alongside, purely so the
two can be compared. Only the primary source is trained on or shown.

Each date is recorded once, along with what our own model estimated for that
date at the moment the official figure was first seen. That "estimate at
first fetch" never changes afterwards, so the file builds up an honest,
out-of-sample record of how good the estimates really are. It isn't
flattered by later refits that have already seen the answer.

generate-tide-reference.py then uses these points (once the station's offset
from the club's tide table is known) to refine the model, and optionally to
show the official figure in the app for the coming week.

Needs:
    UKHO_API_KEY     environment variable (a repo secret in GitHub Actions)
    official-tides.json  (next to this script) with station_id filled in

With no station_id yet, it lists the stations nearest the club instead, so
you can pick one. With no API key, it explains how to get one and exits
without failing, so the scheduled run stays green until it's set up.

Run (from this folder):
    python3 fetch-official-tides.py --repo-root ../..
"""
import argparse
import csv
import json
import math
import os
import sys
import urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

API = "https://admiraltyapi.azure-api.net/uktidalapi/api/V1"
LOCAL_TZ = ZoneInfo("Europe/London")
CLUB = (51.737, 0.715)   # Heybridge Basin, same as CONFIG.forecast in index.html
FIELDS = ["Date", "High water", "Tide height (m)", "Station", "First fetched", "Last fetched",
          "Estimate at first fetch", "Estimate height at first fetch (m)",
          "Admiralty high water", "Admiralty height (m)"]
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
HERE = os.path.dirname(os.path.abspath(__file__))


def summary(text):
    """Print, and add to the GitHub Actions run summary when running there."""
    print(text)
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a") as f:
            f.write(text + "\n")


def fetch_club(url):
    """Parse the club's next-7-days table. It gives weekday names, not dates, and an
    AM and a PM high water per row (either may be --:--). Rows are matched to dates
    starting from today, checking every weekday lines up (allowing the table to be
    a day behind or ahead of us around midnight)."""
    import re
    from datetime import timedelta
    req = urllib.request.Request(url, headers={"User-Agent": "bsc-sailing-calendar"})
    with urllib.request.urlopen(req, timeout=30) as r:
        html = r.read().decode("utf-8", "replace")
    text = re.sub(r"<[^>]+>", " ", html)
    rows = re.findall(r"\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b\s+(\d\d:\d\d|--:--)\s+([\d.]+|--)\s+(\d\d:\d\d|--:--)\s+([\d.]+|--)", text)
    if len(rows) < 3:
        sys.exit(f"Couldn't read the club tide table at {url}: found {len(rows)} rows. Has the page changed?")
    today = datetime.now(LOCAL_TZ).date()
    for shift in (0, -1, 1):
        dates = [today + timedelta(days=shift + i) for i in range(len(rows))]
        if all(DAYS[d.weekday()] == r[0] for d, r in zip(dates, rows)):
            break
    else:
        sys.exit("The club tide table's weekdays don't line up with today's date. Not recording anything.")
    out = {}
    for d, (_, am, amh, pm, pmh) in zip(dates, rows):
        cands = [(t, h) for t, h in ((am, amh), (pm, pmh)) if t != "--:--" and h != "--"]
        if not cands:
            continue
        t, h = min(cands, key=lambda c: abs(int(c[0][:2]) * 60 + int(c[0][3:]) - 12 * 60))
        out[d.isoformat()] = (t, round(float(h), 2))
    return out


def get(path, key):
    req = urllib.request.Request(API + path, headers={"Ocp-Apim-Subscription-Key": key, "User-Agent": "bsc-sailing-calendar"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def parse_utc(s):
    """API times are UTC, e.g. 2026-10-06T14:23:00 or with fractional seconds / Z."""
    s = s.rstrip("Z").split(".")[0]
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)


def daytime_high_waters(events):
    """One high water per UK calendar date: the one nearest midday, matching the
    convention the programme and the model use (the club sails on the daytime tide)."""
    by_date = {}
    for e in events:
        if e.get("EventType") != "HighWater" or e.get("Height") is None or not e.get("DateTime"):
            continue
        local = parse_utc(e["DateTime"]).astimezone(LOCAL_TZ)
        d = local.strftime("%Y-%m-%d")
        dist = abs(local.hour * 60 + local.minute - 12 * 60)
        if d not in by_date or dist < by_date[d][0]:
            by_date[d] = (dist, local.strftime("%H:%M"), round(float(e["Height"]), 2))
    return {d: (t, h) for d, (_, t, h) in by_date.items()}


def list_nearest(key, n=8):
    data = get("/Stations", key)
    feats = data.get("features", data if isinstance(data, list) else [])
    rows = []
    for f in feats:
        p, g = f.get("properties", {}), f.get("geometry", {})
        lon, lat = (g.get("coordinates") or [None, None])[:2]
        if lat is None:
            continue
        dlat, dlon = math.radians(lat - CLUB[0]), math.radians(lon - CLUB[1])
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(CLUB[0])) * math.cos(math.radians(lat)) * math.sin(dlon / 2) ** 2
        rows.append((6371 * 2 * math.asin(math.sqrt(a)), p.get("Id"), p.get("Name")))
    rows.sort()
    summary("### Tide stations nearest the club\n\nPut one of these IDs in `scripts/tide/official-tides.json` as `station_id`:\n")
    summary("| ID | Station | Distance |\n| --- | --- | --- |")
    for km, sid, name in rows[:n]:
        summary(f"| `{sid}` | {name} | {km:.1f} km |")


def load_existing(path):
    if not os.path.exists(path):
        return {}
    return {r["Date"]: r for r in csv.DictReader(open(path, encoding="utf-8-sig"))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default="../..")
    args = ap.parse_args()

    cfg = json.load(open(os.path.join(HERE, "official-tides.json")))
    source = cfg.get("source", "club")
    key = os.environ.get("UKHO_API_KEY", "").strip()
    station = str(cfg.get("station_id") or "").strip()

    admiralty = {}
    if key and station:
        try:
            admiralty = daytime_high_waters(get(f"/Stations/{station}/TidalEvents?duration=7", key))
        except Exception as e:                       # a comparison source failing shouldn't stop the main one
            if source == "admiralty":
                raise
            summary(f"ADMIRALTY comparison skipped: {e}")
    elif key and not station:
        list_nearest(key)

    if source == "club":
        official = fetch_club(cfg["club_url"])
        station_label = "BSC pontoon (club table)"
    else:
        if not key:
            summary("ADMIRALTY source selected but there's no UKHO_API_KEY secret. See scripts/tide/TIDES.md. Nothing fetched.")
            return
        if not station:
            return
        official = admiralty
        station_label = f"{cfg['station_name']} ({station})" if cfg.get("station_name") else station
    if not official:
        sys.exit("No high waters found. Check the source settings in official-tides.json.")

    # Our current estimate for each date, from the tides.json already in the repo
    est = {}
    tj = os.path.join(args.repo_root, "tides.json")
    if os.path.exists(tj):
        for t in json.load(open(tj)).get("tides", []):
            if t.get("source") == "Estimated":
                est[t["date"]] = (t["time"], t["height"])
    prog_dates = set()
    if os.path.exists(tj):
        prog_dates = {t["date"] for t in json.load(open(tj)).get("tides", []) if t.get("source") == "Programme"}

    path = os.path.join(args.repo_root, "tides-official.csv")
    rows = load_existing(path)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = ["| Date | Official HW | Our estimate | Difference |", "| --- | --- | --- | --- |"]
    for d in sorted(official):
        t, h = official[d]
        r = rows.get(d)
        if r is None:
            e = est.get(d)
            r = {"Date": d, "First fetched": now,
                 "Estimate at first fetch": e[0] if e else "",
                 "Estimate height at first fetch (m)": e[1] if e else ""}
            rows[d] = r
        r.update({"High water": t, "Tide height (m)": h, "Station": station_label, "Last fetched": now})
        if d in admiralty and source == "club":
            r["Admiralty high water"], r["Admiralty height (m)"] = admiralty[d]
        if r.get("Estimate at first fetch"):
            eh, em = map(int, r["Estimate at first fetch"].split(":")); oh, om = map(int, t.split(":"))
            diff = (eh * 60 + em) - (oh * 60 + om)
            lines.append(f"| {d} | {t}, {h} m | {r['Estimate at first fetch']}, {r['Estimate height at first fetch (m)']} m | {diff:+d} min |")
        elif d in prog_dates:
            lines.append(f"| {d} | {t}, {h} m | (none: date printed in programme) | |")
        else:
            lines.append(f"| {d} | {t}, {h} m | (no estimate recorded) | |")

    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for d in sorted(rows):
            w.writerow({k: rows[d].get(k, "") for k in FIELDS})

    summary(f"### Published high waters: {station_label}\n")
    summary("\n".join(lines))
    summary("\nDifferences are our estimate minus the published time.")
    if admiralty and source == "club":
        both = [(d, official[d], admiralty[d]) for d in sorted(official) if d in admiralty]
        if both:
            summary("\n### Club table vs ADMIRALTY\n\n| Date | Club | ADMIRALTY | Time diff | Height diff |\n| --- | --- | --- | --- | --- |")
            for d, (ct, ch), (at, ah) in both:
                dm = (int(at[:2]) * 60 + int(at[3:])) - (int(ct[:2]) * 60 + int(ct[3:]))
                summary(f"| {d} | {ct}, {ch} m | {at}, {ah} m | {dm:+d} min | {ah - ch:+.2f} m |")


if __name__ == "__main__":
    main()
