#!/usr/bin/env python3
"""
tidefit.py — fit a harmonic tidal model to the high-water points printed in
the club's own programme, so tide-estimate.py can predict high water for
dates the programme doesn't print (coaching days, Friday RYA courses,
Wednesdays, etc).

WHY THIS EXISTS
The only tide data we have is what's printed on the club's programme: a high
water TIME and HEIGHT for ~113 days across the season, not a continuous
water-level record. Real harbour-authority tide tables are built from a
proper tidal-constituent analysis of continuous gauge data (which we don't
have, and don't have permission to reproduce — see note on copyright in
README.md, "Adding a new season"). This is a lighter-weight approximation:
it fits a small, standard set of tidal constituents against the printed
high-water points using ordinary linear least squares, then uses the
resulting model to predict a plausible high water time and height for any
other date in roughly the same season. It is NOT a substitute for a proper
tide table and every value it produces is marked "Estimated" with a ≈ in
the app — this script exists to make that approximation reproducible and
documented, not to claim more accuracy than it has.

METHOD
For a fixed set of known tidal frequencies (constituent speeds, in degrees
per hour — these are astronomical facts, not something to fit), the height
of the tide at time t is modelled as:

    height(t) = Z0 + sum_i [ a_i * cos(speed_i * t) + b_i * sin(speed_i * t) ]

which is LINEAR in the unknowns (Z0, a_i, b_i) once the speeds are fixed —
so this is solved with ordinary least squares, not an iterative optimiser.
Each known high-water point (time, height) from the programme is one
training row; t is hours since EPOCH below.

Constituents used (the standard "short list" appropriate for a single
season of sparse data — see NOTES.md for why a longer list was NOT used):
    M2  principal lunar semi-diurnal      28.9841042 deg/hr
    S2  principal solar semi-diurnal      30.0000000 deg/hr
    N2  larger lunar elliptic semi-diurnal 28.4397295 deg/hr
    K2  lunisolar semi-diurnal            30.0821373 deg/hr
    K1  lunisolar diurnal                 15.0410686 deg/hr
    O1  principal lunar diurnal           13.9430356 deg/hr
    P1  principal solar diurnal           14.9589314 deg/hr
    M4  shallow-water overtide (2×M2)     57.9682084 deg/hr
M4 is included because the Blackwater is a shallow, funnel-shaped estuary;
shallow water typically distorts the tide curve away from a pure sine wave
(a visibly faster rise than fall, or vice versa), and M2 alone can't
represent that.

Run:
    python3 tidefit.py programme-2026.csv tide-model.json
"""
import csv
import json
import sys
import numpy as np
# NOTE: an earlier version of this script used 8 constituents (adding K2, P1,
# M4). It fit the 113 known points just as well (RMS 0.059 m) but produced
# heights over 10 m on other days — a textbook overfitting/ill-conditioning
# result from including near-duplicate frequencies with sparse, peaks-only
# data. See the comment above CONSTITUENTS for the full explanation.
from datetime import datetime, timezone

EPOCH = datetime(2026, 1, 1, tzinfo=timezone.utc)

CONSTITUENTS = {
    "M2": 28.9841042, "S2": 30.0000000, "N2": 28.4397295,
    "K1": 15.0410686, "O1": 13.9430356,
}
# Deliberately NOT the full harmonic set. K2 sits within 0.08 deg/hr of S2, and
# P1 within 0.08 deg/hr of K1 — telling those pairs apart needs a long,
# continuous, evenly-sampled water-level record (the normal input to a proper
# harmonic analysis). All we have is ~113 isolated daily high-water peaks, not
# a continuous curve, so including K2/P1 (tried first — see NOTES.md) let the
# least-squares fit push those near-duplicate terms to large, almost-cancelling
# values that matched the 113 training points closely (RMS ~0.06 m) but swung
# to physically impossible heights (>10 m, at a site with a ~2-3.6 m range)
# on days in between. Condition number of the design matrix confirms this:
# 1023 with the full 8-constituent set, 41 with just these 5. M4 (shallow-
# water overtide) was dropped for the same reason — a plausible real effect
# in a shallow estuary, but not reliably resolvable from this little data.


def hours_since_epoch(date_str: str, time_str: str) -> float:
    d = datetime.strptime(date_str + " " + time_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
    return (d - EPOCH).total_seconds() / 3600.0


def load_known_points(csv_path):
    pts = []
    seen = set()
    for row in csv.DictReader(open(csv_path, encoding="utf-8-sig")):
        if row.get("Tide source") != "Programme":
            continue
        d, hw, ht = row["Date"], row["High water"], row["Tide height (m)"]
        if not (d and hw and ht) or d in seen:
            continue
        seen.add(d)
        pts.append((hours_since_epoch(d, hw), float(ht), d, hw))
    pts.sort()
    return pts


def design_matrix(t_hours):
    """One row per time, columns [1, cos(M2*t), sin(M2*t), cos(S2*t), sin(S2*t), ...]."""
    cols = [np.ones_like(t_hours)]
    names = ["Z0"]
    for name, speed in CONSTITUENTS.items():
        rad = np.deg2rad(speed) * t_hours
        cols.append(np.cos(rad)); names.append(name + "_cos")
        cols.append(np.sin(rad)); names.append(name + "_sin")
    return np.column_stack(cols), names


def fit(points):
    t = np.array([p[0] for p in points])
    h = np.array([p[1] for p in points])
    X, names = design_matrix(t)
    coeffs, residuals, rank, sv = np.linalg.lstsq(X, h, rcond=None)
    pred = X @ coeffs
    resid = h - pred
    return dict(zip(names, coeffs.tolist())), resid, pred


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "programme-2026.csv"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "tide-model.json"

    points = load_known_points(csv_path)
    if len(points) < 20:
        sys.exit(f"Only {len(points)} known (Programme-sourced) HW points found — too few to fit reliably.")

    coeffs, resid, pred = fit(points)

    model = {
        "epoch": EPOCH.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "constituent_speeds_deg_per_hour": CONSTITUENTS,
        "coefficients": coeffs,
        "fitted_from": csv_path,
        "n_training_points": len(points),
        "training_date_range": [points[0][2], points[-1][2]],
        "residual_rms_m": float(np.sqrt(np.mean(resid ** 2))),
        "residual_max_abs_m": float(np.max(np.abs(resid))),
    }
    json.dump(model, open(out_path, "w"), indent=2)

    print(f"Fitted to {len(points)} known high-water points "
          f"({points[0][2]} to {points[-1][2]}).")
    print(f"Height residual: RMS {model['residual_rms_m']:.3f} m, "
          f"max {model['residual_max_abs_m']:.3f} m.")
    print(f"Model written to {out_path}")


if __name__ == "__main__":
    main()
