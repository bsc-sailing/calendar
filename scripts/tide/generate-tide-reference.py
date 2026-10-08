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
    python3 generate-tide-reference.py --data-dir ../../data --months-ahead 24 --out ../../data/tides.json
"""
import argparse
import glob
import json
import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))
from tidefit import fit, hours_since_epoch, EPOCH, CONSTITUENTS
from tide_predict import height_at, predict_day, day_peaks
from daytime import choose


def load_all_programme_points(data_dir):
    """Every Programme-sourced (Date, High water, Tide height) row, pooled
    across every programme-*.csv in the data folder — not just one season."""
    paths = sorted(glob.glob(os.path.join(data_dir, "programme-*.csv")))
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


def load_official(data_dir):
    """Official (ADMIRALTY) daytime high waters collected by fetch-official-tides.py."""
    path = os.path.join(data_dir, "tides-official.csv")
    if not os.path.exists(path):
        return []
    import csv
    out = []
    for r in csv.DictReader(open(path, encoding="utf-8-sig")):
        if r.get("Date") and r.get("High water") and r.get("Tide height (m)"):
            out.append(r)
    return out


def to_min(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m


def from_min(mins):
    mins = int(round(mins)) % (24 * 60)
    return f"{mins // 60:02d}:{mins % 60:02d}"


def median(xs):
    xs = sorted(xs); n = len(xs)
    return (xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2) if n else None


def station_offset(official, real_by_date, min_overlap):
    """How the official station differs from the club's printed tide table, from
    dates that appear in both: median minutes and metres (programme minus official).
    The official station is never exactly where the club's table is referenced,
    so its raw figures are shifted by this before being trained on or shown."""
    dt, dh = [], []
    for r in official:
        p = real_by_date.get(r["Date"])
        if p:
            dt.append(to_min(p[0]) - to_min(r["High water"]))
            dh.append(float(p[1]) - float(r["Tide height (m)"]))
    if len(dt) < min_overlap:
        return {"known": False, "n_overlap": len(dt), "needed": min_overlap}
    return {"known": True, "n_overlap": len(dt), "minutes": round(median(dt), 1), "metres": round(median(dh), 2),
            "spread_minutes": round(max(dt) - min(dt), 1)}


def adjusted(r, off):
    return from_min(to_min(r["High water"]) + off["minutes"]), round(float(r["Tide height (m)"]) + off["metres"], 1)


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
    ap.add_argument("--data-dir", default="../../data", help="folder containing the programme-*.csv files")
    ap.add_argument("--months-ahead", type=int, default=24)
    ap.add_argument("--out", default="../../data/tides.json")
    args = ap.parse_args()

    points, files_used = load_all_programme_points(args.data_dir)
    programme_points = list(points)
    cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "official-tides.json")
    cfg = json.load(open(cfg_path)) if os.path.exists(cfg_path) else {}
    official = load_official(args.data_dir)
    real_prog = {d_: (hw_, ht_) for _, ht_, d_, hw_ in points}
    offset = station_offset(official, real_prog, int(cfg.get("min_overlap_days", 3))) if official else None
    # Official points join the training data only once the station offset is
    # known, and never on a date the programme already prints.
    official_used, official_alt = {}, {}
    if offset and offset["known"]:
        for r in official:
            if r["Date"] not in real_prog:
                if r.get("Other high water") and r.get("Other height (m)"):
                    a_hw, a_ht = adjusted({"High water": r["Other high water"], "Tide height (m)": r["Other height (m)"]}, offset)
                    official_alt[r["Date"]] = {"time": a_hw, "height": a_ht}
                hw, ht = adjusted(r, offset)
                official_used[r["Date"]] = (hw, ht)
                points.append((hours_since_epoch(r["Date"], hw), ht, r["Date"], hw))
        points.sort()
        if official_used:
            files_used.append(f"tides-official.csv ({len(official_used)} points, station offset {offset['minutes']:+} min, {offset['metres']:+} m)")
    if len(points) < 20:
        sys.exit(f"Only {len(points)} known points found across all programme-*.csv files — too few to fit.")

    model, resid = build_model(points)
    rms = (sum(r * r for r in resid) / len(resid)) ** 0.5

    # Real printed values win, always — a date this model was trained on gets
    # its OWN real value in the output, not a re-prediction of it. This is
    # what keeps this screen and the programme's own day view from ever
    # showing two different tides for the same date: real data is reused
    # verbatim, not approximated a second time.
    real_by_date = real_prog
    show_official = bool(cfg.get("show_in_app")) and bool(official_used)

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
        elif show_official and date_str in official_used:
            hw, ht = official_used[date_str]
            rec = {"date": date_str, "time": hw, "height": ht, "source": "Forecast"}
            if date_str in official_alt:
                rec["alt"] = official_alt[date_str]
            tides.append(rec)
            n_real += 1
        else:
            best, alt = choose(date_str, day_peaks(model, date_str))
            if best:
                hw, ht = best
                rec = {"date": date_str, "time": hw, "height": ht, "source": "Estimated"}
                if alt:   # two high waters about equally far from midday: show both
                    rec["alt"] = {"time": alt[0], "height": alt[1]}
                tides.append(rec)
                n_modelled += 1
        d += timedelta(days=1)

    # Accuracy check, run every time this generates: how well would the model
    # have predicted the real points it was just trained on? (Not a health
    # check of the fit's own residual — that only measures height at a known
    # time. This checks predicted TIMING too, the harder and more relevant
    # question for what the app actually shows. See TIDES.md, "Accuracy".)
    t_errs, h_errs = [], []
    for t_h, height, d_, hw_ in programme_points:
        res = predict_day(model, d_, near=hw_)
        if not res:
            continue
        pred_hw, pred_ht = res
        a, b = map(int, pred_hw.split(":")); c, dd = map(int, hw_.split(":"))
        t_errs.append((a * 60 + b) - (c * 60 + dd))
        h_errs.append(pred_ht - height)
    t_rms = (sum(x * x for x in t_errs) / len(t_errs)) ** 0.5 if t_errs else None
    h_rms = (sum(x * x for x in h_errs) / len(h_errs)) ** 0.5 if h_errs else None

    # The honest check: official high waters against what we had estimated for
    # those dates BEFORE the official figure was known (recorded at first fetch).
    forecast_check = None
    if official:
        ft, fh = [], []
        for r in official:
            e_t, e_h = r.get("Estimate at first fetch"), r.get("Estimate height at first fetch (m)")
            if not e_t:
                continue
            o_t, o_h = (adjusted(r, offset) if offset and offset["known"] else (r["High water"], float(r["Tide height (m)"])))
            ft.append(to_min(e_t) - to_min(o_t)); fh.append(float(e_h) - float(o_h))
        if ft:
            forecast_check = {
                "n_days": len(ft),
                "time_rms_minutes": round((sum(x * x for x in ft) / len(ft)) ** 0.5, 1),
                "time_mean_minutes": round(sum(ft) / len(ft), 1),
                "time_max_abs_minutes": max(abs(x) for x in ft),
                "height_rms_m": round((sum(x * x for x in fh) / len(fh)) ** 0.5, 3),
                "compared_with": "official, offset-adjusted" if offset and offset["known"] else "official, raw (station offset not known yet)",
            }

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
        "official_station_offset": offset,
        "official_points_used": len(official_used),
        "official_shown_in_app": show_official,
        "forecast_note": cfg.get("attribution", "") if show_official else "",
        "estimate_vs_official": forecast_check,
        "n_modelled": n_modelled,
        "tides": tides,
    }
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    json.dump(out, open(args.out, "w"), indent=2)
    print(f"Fitted to {len(points)} points from {len(files_used)} file(s): {', '.join(files_used)}")
    print(f"Fit RMS: {rms:.3f} m")
    print(f"Wrote {len(tides)} days ({out['window'][0]} to {out['window'][1]}) -> {args.out}")
    print(f"  {n_real} from real data (programme, or official where shown), {n_modelled} modelled")
    if offset:
        print("Official station offset: " + (f"{offset['minutes']:+} min, {offset['metres']:+} m from {offset['n_overlap']} overlapping dates (spread {offset['spread_minutes']} min)"
              if offset["known"] else f"not known yet ({offset['n_overlap']} of {offset['needed']} overlapping dates)"))
    if forecast_check:
        print(f"Estimate vs official over {forecast_check['n_days']} days ({forecast_check['compared_with']}): time RMS {forecast_check['time_rms_minutes']} min, "
              f"mean {forecast_check['time_mean_minutes']:+} min, worst {forecast_check['time_max_abs_minutes']} min; height RMS {forecast_check['height_rms_m']} m")
    if t_rms is not None:
        print(f"Accuracy check vs the {len(t_errs)} training points: time RMS {t_rms:.1f} min, height RMS {h_rms:.3f} m")


if __name__ == "__main__":
    main()
