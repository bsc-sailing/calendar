#!/usr/bin/env python3
"""Check the season data files before they're published.

Runs the same checks as the app's ?check page, on every programme-YEAR.csv
and extras-YEAR.csv, and stops a deploy (or marks a pull request with a red
cross) if a file would show wrongly in the app. Each problem names the file
and line, so it shows on that line in a pull request's "Files changed" tab.

    python3 scripts/check-data.py            # checks every season file in data/
    python3 scripts/check-data.py some.csv   # checks just that file

Problems (fail): missing columns, dates that aren't YYYY-MM-DD, start times
that aren't HH:MM or TBC, start orders that aren't 1-9, racing rows with no
start time, GP weekend values that aren't TRUE/FALSE, rows on one day that
disagree about the tide.
Also fails: a cell starting with = + @ or a tab, which a spreadsheet would run
as a formula when someone opens the CSV ("CSV injection"); a file over 2 MB.
Warnings (don't fail): days with no tide, dates outside the file's year.
"""
import csv
import glob
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEED = ["Date", "High water", "Tide height (m)", "Start time", "Fleet", "Race start order", "Event",
        "Training", "GP weekend", "Race / series", "Race no(s)", "Detail"]


def check(path):
    errors, warnings = [], []
    name = os.path.basename(path)
    m = re.fullmatch(r"(?:programme|extras)-(\d{4})\.csv", name)
    year = int(m.group(1)) if m else None
    if os.path.getsize(path) > 2_000_000:
        return [(0, f"The file is {os.path.getsize(path) // 1000} KB; a season should be well under 2 MB. Is it the right file?")], []
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
        cols = [c.strip() for c in (rows[0].keys() if rows else [])]
    if not rows:
        return [(1, "The file has no rows under the headings.")], []
    missing = [c for c in NEED if c not in cols]
    if missing:
        return [(1, "Missing columns: " + ", ".join(missing))], []
    tides = defaultdict(set)
    for i, raw in enumerate(rows, start=2):           # line 1 is the headings
        r = {k.strip(): (v or "").strip() for k, v in raw.items() if k}
        d, st, o, g = r["Date"], r["Start time"], r["Race start order"], r["GP weekend"]
        if not any(r.values()):
            continue
        for k, v in r.items():
            if v[:1] in ("=", "+", "@", "\t"):
                errors.append((i, f"{k} starts with '{v[:1]}', which a spreadsheet would treat as a formula. Remove it or reword the cell"))
        if not re.fullmatch(r"\d{4}-\d\d-\d\d", d):
            errors.append((i, f"Date '{d}' isn't YYYY-MM-DD"))
            continue
        if st and not re.fullmatch(r"(\d\d:\d\d|TBC)", st):
            errors.append((i, f"Start time '{st}' isn't HH:MM or TBC"))
        if o and not re.fullmatch(r"[1-9]", o):
            errors.append((i, f"Race start order '{o}' isn't a number from 1 to 9"))
        if o and not re.fullmatch(r"\d\d:\d\d", st):
            errors.append((i, "Racing row (it has a start order) with no HH:MM start time"))
        if g and g.upper() not in ("TRUE", "FALSE"):
            errors.append((i, f"GP weekend '{g}' isn't TRUE or FALSE"))
        hw = r["High water"]
        if hw and not re.fullmatch(r"\d\d:\d\d", hw):
            errors.append((i, f"High water '{hw}' isn't HH:MM"))
        if year and int(d[:4]) != year:
            warnings.append((i, f"Date {d} is outside {year} (fine for coaching or events, but check it's intended)"))
        tides[d].add((hw, r["Tide height (m)"]))
    for d, t in sorted(tides.items()):
        if len(t) > 1:
            errors.append((0, f"{d}: rows disagree about the tide ({', '.join(sorted(f'{a or '-'} {b or '-'}' for a, b in t))})"))
        elif t == {("", "")} and name.startswith("programme"):
            warnings.append((0, f"{d}: no high water or tide height (the app will use an estimate)"))
    return errors, warnings


def main():
    if len(sys.argv) > 1:
        paths = sys.argv[1:]
    else:
        data = os.path.join(ROOT, "data")
        paths = sorted(p for pat in ("programme-*.csv", "extras-*.csv") for p in glob.glob(os.path.join(data, pat))
                       )
    failed = False
    for path in paths:
        rel = os.path.relpath(path, ROOT)
        errors, warnings = check(path)
        print(f"{rel}: {len(errors)} problem(s), {len(warnings)} warning(s)")
        for line, msg in errors:
            print(f"::error file={rel}" + (f",line={line}" if line else "") + f"::{msg}")
        for line, msg in warnings[:20]:
            print(f"::warning file={rel}" + (f",line={line}" if line else "") + f"::{msg}")
        if len(warnings) > 20:
            print(f"  ... and {len(warnings) - 20} more warnings")
        failed = failed or bool(errors)
    if not paths:
        print("No programme or extras files found.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
