#!/usr/bin/env python3
"""
tide_predict.py — use a model fitted by tidefit.py to estimate high water
for a date the club's programme doesn't cover.

This finds every local high-water peak in the target day (usually two) and
returns the one closest to --near (default midday, since the sailing
programme's own high waters are always the daytime one). It does NOT
extrapolate indefinitely — the further a date is from the training window
(see tide-model.json's training_date_range), the less this should be
trusted; see README.md ("Adding a new season") for how this fits into the
yearly workflow.

Single date:
    python3 tide_predict.py tide-model.json 2026-01-03
    python3 tide_predict.py tide-model.json 2026-01-03 --near 12:30

Batch, from a CSV of dates needing an estimate (one column "Date"):
    python3 tide_predict.py tide-model.json --dates-from needs-tide.csv --out estimates.csv
"""
import argparse
import csv
import json
import numpy as np
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

LOCAL_TZ = ZoneInfo("Europe/London")   # dates and times in and out are UK clock time


def load_model(path):
    m = json.load(open(path))
    m["epoch_dt"] = datetime.strptime(m["epoch"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return m


def height_at(model, t_hours):
    speeds = model["constituent_speeds_deg_per_hour"]
    c = model["coefficients"]
    h = c["Z0"]
    for name, speed in speeds.items():
        rad = np.deg2rad(speed) * t_hours
        h = h + c[name + "_cos"] * np.cos(rad) + c[name + "_sin"] * np.sin(rad)
    return h


def predict_day(model, date_str, near="12:00", step_minutes=1):
    day0 = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=LOCAL_TZ).astimezone(timezone.utc)
    t0 = (day0 - model["epoch_dt"]).total_seconds() / 3600.0
    n = int(24 * 60 / step_minutes) + 1
    t = t0 + np.arange(n) * (step_minutes / 60.0)
    h = height_at(model, t)
    # local maxima: a point higher than both neighbours
    is_peak = np.r_[False, (h[1:-1] > h[:-2]) & (h[1:-1] > h[2:]), False]
    peak_idx = np.where(is_peak)[0]
    if len(peak_idx) == 0:
        return None
    near_dt = datetime.strptime(date_str + " " + near, "%Y-%m-%d %H:%M").replace(tzinfo=LOCAL_TZ).astimezone(timezone.utc)
    near_t = (near_dt - model["epoch_dt"]).total_seconds() / 3600.0
    best = peak_idx[np.argmin(np.abs(t[peak_idx] - near_t))]
    peak_time = (model["epoch_dt"] + timedelta(hours=float(t[best]))).astimezone(LOCAL_TZ)
    return peak_time.strftime("%H:%M"), round(float(h[best]), 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("date", nargs="?")
    ap.add_argument("--near", default="12:00")
    ap.add_argument("--dates-from")
    ap.add_argument("--fill-csv", help="A programme-YYYY.csv to fill blank tide rows in directly, once per unique date.")
    ap.add_argument("--out")
    args = ap.parse_args()

    model = load_model(args.model)

    if args.dates_from:
        rows = list(csv.DictReader(open(args.dates_from, encoding="utf-8-sig")))
        out_rows = []
        for r in rows:
            res = predict_day(model, r["Date"], near=r.get("Near", "12:00") or "12:00")
            hw, ht = res if res else ("", "")
            out_rows.append({"Date": r["Date"], "High water": hw, "Tide height (m)": ht})
        with open(args.out or "estimates.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["Date", "High water", "Tide height (m)"])
            w.writeheader(); w.writerows(out_rows)
        print(f"Wrote {len(out_rows)} estimates to {args.out or 'estimates.csv'}")
        return

    if args.fill_csv:
        # The practical yearly workflow: take a programme-YYYY.csv that already has
        # the printed grid dates filled in (Tide source = Programme), but has blank
        # High water / Tide height / Tide source on the extra rows (Wednesdays,
        # coaching days, RYA Friday courses, etc) — fill just those in, once per
        # unique date (a date usually appears on several rows, one per fleet/event),
        # and mark them Tide source = Estimated. Rows that already have a High
        # water value are left completely untouched.
        rows = list(csv.DictReader(open(args.fill_csv, encoding="utf-8-sig")))
        fieldnames = list(rows[0].keys())
        cache = {}
        filled = 0
        for r in rows:
            if r.get("High water", "").strip():
                continue  # already has a real printed value — never overwrite
            d = r["Date"]
            if not d:
                continue
            if d not in cache:
                cache[d] = predict_day(model, d, near=args.near)
            res = cache[d]
            if res:
                r["High water"], r["Tide height (m)"] = res
                r["Tide source"] = "Estimated"
                filled += 1
        out_path = args.out or args.fill_csv
        with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader(); w.writerows(rows)
        print(f"Filled {filled} rows ({len(cache)} unique dates) -> {out_path}")
        return

    res = predict_day(model, args.date, near=args.near)
    if res:
        print(f"{args.date}: HW {res[0]}, {res[1]} m")
    else:
        print(f"{args.date}: no peak found")


if __name__ == "__main__":
    main()
