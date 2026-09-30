#!/usr/bin/env python3
"""
generate-tide-reference.py — refit the tide model against every real
(Programme-sourced) high-water point from every programme-*.csv in the
repo, then predict a high water for every day in a rolling window (today
to N months ahead), writing tides.json.

This is what lets the app show an estimated tide for ANY date — not just
the specific "extra" dates a particular season's file happens to include —
and it means tide estimates stay current without anyone needing to
remember to run anything each season: as more programme-YEAR.csv files
accumulate over the years, this script automatically pools all of them,
so the fit is trained on more real data (and more of the calendar year)
each time it runs, not just whatever one season's file covers.

See TIDES.md for the method itself; this script only handles: (a) finding
and pooling training data across seasons, and (b) the rolling-window
output. The actual harmonic fit and prediction logic is unchanged, reused
directly from tidefit.py / tide_predict.py in this folder.

Run:
    python3 generate-tide-reference.py --repo-root ../.. --months-ahead 24 --out ../../tides.json
"""
import argparse
import glob
import json
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))
from tidefit import fit, hours_since_epoch, EPOCH, CONSTITUENTS
from tide_predict import height_at, predict_day


def load_all_programme_points(repo_root):
    """Every Programme-sourced (Date, High water, Tide height) row, pooled
    across every programme-*.csv in the repo root — not just one season."""
    paths = sorted(glob.glob(os.path.join(repo_root, "programme-*.csv")))
    pts, seen, files_used = [], set(), []
    import csv
    for path in paths:
        fname = os.path.basename(path)
        if fname == "programme-template.csv":
            continue
        count_here = 0
        for row in csv.DictReader(open(path, encoding="utf-8-sig")):
            if row.get("Tide source") != "Programme":
                continue
            d, hw, ht = row.get("Date"), row.get("High water"), row.get("Tide height (m)")
            if not (d and hw and ht) or d in seen:
                continue
            seen.add(d); count_here += 1
            pts.append((hours_since_epoch(d, hw), float(ht), d, hw))
        if count_here:
            files_used.append(f"{fname} ({count_here} points)")
    pts.sort()
    return pts, files_used


def build_model(points):
    coeffs, resid, pred = fit(points)
    return {
        "epoch": EPOCH.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "epoch_dt": EPOCH,
        "constituent_speeds_deg_per_hour": CONSTITUENTS,
        "coefficients": coeffs,
    }, resid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default="../..", help="folder containing the programme-*.csv files")
    ap.add_argument("--months-ahead", type=int, default=24)
    ap.add_argument("--out", default="../../tides.json")
    args = ap.parse_args()

    points, files_used = load_all_programme_points(args.repo_root)
    if len(points) < 20:
        sys.exit(f"Only {len(points)} known points found across all programme-*.csv files — too few to fit.")

    model, resid = build_model(points)
    rms = (sum(r * r for r in resid) / len(resid)) ** 0.5

    # Real printed values win, always — a date this model was trained on gets
    # its OWN real value in the output, not a re-prediction of it. This is
    # what keeps this screen and the programme's own day view from ever
    # showing two different tides for the same date: real data is reused
    # verbatim, not approximated a second time.
    real_by_date = {d_: (hw_, ht_) for _, ht_, d_, hw_ in points}

    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    end = today + timedelta(days=int(args.months_ahead * 30.44))  # a calendar month, averaged

    tides = []
    n_real, n_modelled = 0, 0
    d = today
    while d < end:
        date_str = d.strftime("%Y-%m-%d")
        if date_str in real_by_date:
            hw, ht = real_by_date[date_str]
            tides.append({"date": date_str, "time": hw, "height": ht, "source": "Programme"})
            n_real += 1
        else:
            res = predict_day(model, date_str)
            if res:
                hw, ht = res
                tides.append({"date": date_str, "time": hw, "height": ht, "source": "Estimated"})
                n_modelled += 1
        d += timedelta(days=1)

    # Accuracy check, run every time this generates: how well would the model
    # have predicted the real points it was just trained on? (Not a health
    # check of the fit's own residual — that only measures height at a known
    # time. This checks predicted TIMING too, the harder and more relevant
    # question for what the app actually shows. See TIDES.md, "Accuracy".)
    t_errs, h_errs = [], []
    for t_h, height, d_, hw_ in points:
        res = predict_day(model, d_, near=hw_)
        if not res:
            continue
        pred_hw, pred_ht = res
        a, b = map(int, pred_hw.split(":")); c, dd = map(int, hw_.split(":"))
        t_errs.append((a * 60 + b) - (c * 60 + dd))
        h_errs.append(pred_ht - height)
    t_rms = (sum(x * x for x in t_errs) / len(t_errs)) ** 0.5 if t_errs else None
    h_rms = (sum(x * x for x in h_errs) / len(h_errs)) ** 0.5 if h_errs else None

    out = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "method": "harmonic tide model — see scripts/tide/TIDES.md",
        "fit_rms_m": round(rms, 3),
        "accuracy_check_against_training_points": {
            "time_rms_minutes": round(t_rms, 1) if t_rms is not None else None,
            "height_rms_m": round(h_rms, 3) if h_rms is not None else None,
            "n_points": len(t_errs),
        },
        "fitted_from": files_used,
        "n_training_points": len(points),
        "window": [today.strftime("%Y-%m-%d"), (end - timedelta(days=1)).strftime("%Y-%m-%d")],
        "n_real": n_real,
        "n_modelled": n_modelled,
        "tides": tides,
    }
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(out, open(args.out, "w"), indent=2)
    print(f"Fitted to {len(points)} points from {len(files_used)} file(s): {', '.join(files_used)}")
    print(f"Fit RMS: {rms:.3f} m")
    print(f"Wrote {len(tides)} days ({out['window'][0]} to {out['window'][1]}) -> {args.out}")
    print(f"  {n_real} from real programme data, {n_modelled} modelled")
    if t_rms is not None:
        print(f"Accuracy check vs the {len(t_errs)} training points: time RMS {t_rms:.1f} min, height RMS {h_rms:.3f} m")


if __name__ == "__main__":
    main()
