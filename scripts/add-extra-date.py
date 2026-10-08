#!/usr/bin/env python3
"""
add-extra-date.py: turn an "Add an extra date" issue (GitHub issue form) into
a row in extras-YEAR.csv. Run by .github/workflows/extra-date.yml.

Everything in the issue is treated as untrusted text: each field is checked
against what it should look like, and anything that doesn't fit is reported
back on the issue rather than guessed at. The app shows all of it as plain
text, never as HTML.

Re-running for the same issue (after an edit) replaces that issue's row, so a
request never ends up in the file twice.

Outputs (for the workflow): ok=true|false, file=<path>; plus
add-extra-date-message.md (what to fix) or add-extra-date-pr.md (PR body).
"""
import argparse
import csv
import json
import os
import re
from datetime import date, datetime

COLUMNS = ["Date", "High water", "Tide height (m)", "Tide source", "Start time", "Fleet", "Race start order",
           "Event", "Training", "GP weekend", "Race / series", "Race no(s)", "Detail", "Request"]
KINDS = {"Informal race": "race", "Social or other event": "event", "Training": "train"}
WHERE = {"On the lake", "On the river", "Ashore"}


def fields_from_body(body):
    """Issue forms render as '### Label' followed by the answer."""
    out, label = {}, None
    for line in (body or "").splitlines():
        m = re.match(r"^###\s+(.*?)\s*$", line)
        if m:
            label = m.group(1); out[label] = []
        elif label is not None:
            out[label].append(line)
    clean = {}
    for k, v in out.items():
        text = "\n".join(v).strip()
        clean[k] = "" if text == "_No response_" else text
    return clean


def tidy(text, limit):
    text = re.sub(r"[\x00-\x1f\x7f]+", " ", text or "")      # no control characters or line breaks
    text = re.sub(r"\s+", " ", text.replace("|", "/")).strip()
    return text[:limit].strip()


def parse_date(s):
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    return None


def parse_start(s):
    s = s.strip().upper().replace(".", ":")
    if s == "TBC":
        return "TBC"
    m = re.fullmatch(r"(\d{1,2}):?(\d{2})", s)
    if m and int(m.group(1)) < 24 and int(m.group(2)) < 60:
        return f"{int(m.group(1)):02d}:{m.group(2)}"
    return None


def tide_for(data_dir, iso):
    try:
        for t in json.load(open(os.path.join(data_dir, "tides.json"))).get("tides", []):
            if t["date"] == iso:
                return t["time"], str(t["height"]), "Programme" if t.get("source") == "Programme" else "Estimated"
    except (OSError, ValueError, KeyError):
        pass
    return "", "", ""


def set_output(**kw):
    path = os.environ.get("GITHUB_OUTPUT")
    lines = [f"{k}={v}" for k, v in kw.items()]
    if path:
        with open(path, "a") as f:
            f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--event", required=True)
    ap.add_argument("--data-dir", default="data", help="folder holding extras-YEAR.csv and tides.json")
    ap.add_argument("--today", help="for testing")
    args = ap.parse_args()

    issue = json.load(open(args.event))["issue"]
    num = int(issue["number"])
    f = fields_from_body(issue.get("body"))
    today = date.fromisoformat(args.today) if args.today else date.today()
    problems = []

    d = parse_date(f.get("Date", ""))
    if not d:
        problems.append("**Date** should look like `2026-10-16`.")
    elif d < today:
        problems.append("**Date** is in the past.")
    elif d.year > today.year + 1:
        problems.append("**Date** is more than a year ahead. Is the year right?")
    name = tidy(f.get("Name", ""), 60)
    if not name:
        problems.append("**Name** is missing.")
    kind = next((v for k, v in KINDS.items() if f.get("Type", "").startswith(k)), None)
    if not kind:
        problems.append("**Type** should be one of the options in the form.")
    start = parse_start(f.get("Start time", ""))
    if not start:
        problems.append("**Start time** should be 24-hour `HH:MM` (for example `09:30`) or `TBC`.")
    where = f.get("Where", "").strip()
    if where not in WHERE:
        problems.append("**Where** should be one of the options in the form.")
    who = tidy(f.get("Who can take part", ""), 80) or "All classes welcome"
    notes = tidy(f.get("Anything else (optional)", ""), 200)

    if problems:
        open("add-extra-date-message.md", "w").write(
            "This request couldn't be added yet:\n\n" + "\n".join("- " + p for p in problems) +
            "\n\nEdit the issue to fix it and it will be checked again automatically.")
        set_output(ok="false")
        return

    iso = d.isoformat()
    detail = " – ".join([where, who]) + "."
    if kind == "race":
        detail += " Not part of any series."
    if notes:
        detail += " " + notes
    hw, ht, src = tide_for(args.data_dir, iso)
    row = {c: "" for c in COLUMNS}
    row.update({"Date": iso, "High water": hw, "Tide height (m)": ht, "Tide source": src, "Start time": start,
                "GP weekend": "FALSE", "Detail": detail, "Request": f"#{num}"})
    if kind == "race":
        row.update({"Event": "Informal race", "Race / series": name})
    elif kind == "event":
        row["Event"] = name
    else:
        row["Training"] = name

    path = os.path.join(args.data_dir, f"extras-{d.year}.csv")
    rows = []
    if os.path.exists(path):
        rows = [r for r in csv.DictReader(open(path, encoding="utf-8-sig")) if r.get("Request") != f"#{num}"]
    # this issue's row may have moved year after an edit: remove it from the other files too
    for other in os.listdir(args.data_dir):
        if re.fullmatch(r"extras-\d{4}\.csv", other) and os.path.join(args.data_dir, other) != path:
            op = os.path.join(args.data_dir, other)
            before = list(csv.DictReader(open(op, encoding="utf-8-sig")))
            keep = [r for r in before if r.get("Request") != f"#{num}"]
            if len(keep) == len(before):
                continue
            with open(op, "w", newline="", encoding="utf-8-sig") as fh:
                w = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\r\n", extrasaction="ignore")
                w.writeheader(); w.writerows(keep)
    rows.append(row)
    rows.sort(key=lambda r: (r["Date"], r["Start time"]))
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS, lineterminator="\r\n", extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

    tide_txt = f"≈{hw}, {ht} m (estimated; the app uses the latest tide data automatically)" if src == "Estimated" else (f"{hw}, {ht} m (printed in programme)" if hw else "none available")
    open("add-extra-date-pr.md", "w").write(
        f"Adds an extra date requested in #{num}. Merging closes the request.\n\n"
        f"| | |\n| --- | --- |\n| Date | {iso} |\n| Name | {name} |\n| Type | {f.get('Type', '')} |\n"
        f"| Start | {start} |\n| Detail | {detail} |\n| High water | {tide_txt} |\n\n"
        f"Closes #{num}\n")
    open("add-extra-date-title.txt", "w").write(f"Extra date: {iso} {name}")
    set_output(ok="true", file=os.path.relpath(path, args.data_dir))


if __name__ == "__main__":
    main()
