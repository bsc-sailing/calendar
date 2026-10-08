#!/usr/bin/env python3
"""Assemble the published website from the repo, and check nothing is missing.

The repo keeps the app, its images and the data in separate folders, but the
live site serves every file from one place, at the same addresses it always
has (https://bsc-sailing.github.io/calendar/index.html, .../programme-2026.csv
and so on). So bookmarks, home-screen installs and the offline copy never see
the repo's folders move. This script copies each folder's files into one
output folder, which the deploy workflow then publishes.

    python3 scripts/build-site.py              # builds into _site/
    python3 scripts/build-site.py --out /tmp/x

Run by .github/workflows/deploy.yml on every push to main (and, check-only,
on every pull request). Exits non-zero if two folders would publish a file
with the same name, or if a file the app asks for isn't in the output.
"""
import argparse
import json
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Folders whose files are published at the top level of the site, in order.
# Only the files directly inside each folder are copied (not subfolders).
PUBLISH_DIRS = ["app", "app/assets", "data", "templates", "docs"]

def sources():
    """(published name, source path) for every file to publish."""
    for d in PUBLISH_DIRS:
        folder = os.path.join(ROOT, d)
        if not os.path.isdir(folder):
            continue
        for name in sorted(os.listdir(folder)):
            path = os.path.join(folder, name)
            if os.path.isfile(path) and not name.startswith("."):
                yield name, path


def required_files(site):
    """Files the app itself asks for: the service worker's offline list, the
    manifest's icons, and the fixed file names in CONFIG in index.html."""
    need = set()
    sw = open(os.path.join(site, "sw.js"), encoding="utf-8").read()
    m = re.search(r"const FILES = \[(.*?)\]", sw, re.S)
    if m:
        need.update(f for f in re.findall(r'"([^"]+)"', m.group(1)) if f != "./")
    manifest = json.load(open(os.path.join(site, "manifest.webmanifest"), encoding="utf-8"))
    need.update(i["src"] for i in manifest.get("icons", []))
    index = open(os.path.join(site, "index.html"), encoding="utf-8").read()
    for key in ("coursesFile", "chartImage", "eventsFile", "tidesFile"):
        m = re.search(key + r':\s*"([^"]+)"', index)
        if m:
            need.add(m.group(1))
    # Local files linked or fetched from any published page (guide.html, racecard.html ...)
    for page in os.listdir(site):
        if page.endswith(".html"):
            html = open(os.path.join(site, page), encoding="utf-8").read()
            need.update(re.findall(r'(?:href|src)="([\w.-]+\.(?:png|jpg|webmanifest|html|csv|xlsx|md))"', html))
            need.update(re.findall(r'fetch\("([\w.-]+\.(?:csv|json|md))"', html))
    return need


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=os.path.join(ROOT, "_site"))
    args = ap.parse_args()

    if os.path.isdir(args.out):
        shutil.rmtree(args.out)
    os.makedirs(args.out)

    seen, problems = {}, []
    for name, path in sources():
        rel = os.path.relpath(path, ROOT)
        if name in seen:
            problems.append(f"{rel} and {seen[name]} would both be published as {name}. Rename one.")
            continue
        seen[name] = rel
        shutil.copy2(path, os.path.join(args.out, name))
    # Tell GitHub Pages to serve files as they are (no Jekyll processing).
    open(os.path.join(args.out, ".nojekyll"), "w").close()

    for f in ("index.html", "sw.js", "manifest.webmanifest"):
        if f not in seen:
            problems.append(f"{f} is missing, so there's no app to publish.")
    if not problems:
        for f in sorted(required_files(args.out)):
            if f not in seen:
                problems.append(f"The app asks for {f}, but no folder contains it.")

    print(f"Published {len(seen)} files into {os.path.relpath(args.out, ROOT)}/:")
    for name, rel in sorted(seen.items()):
        print(f"  {name:32} from {rel}")
    if problems:
        print("\nProblems:")
        for p in problems:
            print(f"::error::{p}")
        sys.exit(1)


if __name__ == "__main__":
    main()
