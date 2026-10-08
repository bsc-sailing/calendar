# Security

The calendar is a static website: GitHub Pages serves fixed files, and there's no server, database, login or form that stores anything. That rules out most attacks. What's left is controlling who can change the files, and making sure the data files can only ever be shown as text.

## Who can change what

| Who | What they can do | What stops them going further |
| --- | --- | --- |
| Anyone on the internet | Read the site and the repo. Open an issue, including an **Add an extra date** request. Open a pull request from their own copy of the repo. | Nothing they do reaches the site without a maintainer merging it. Extra-date requests from outsiders do nothing until a maintainer adds the `approved` label. |
| Someone previewing a file (`?preview`, `racecard.html`) | Load a CSV into the app **in their own browser** | The file never leaves their device, and it's shown as text. It can't affect anyone else. |
| Maintainers (`@bsc-sailing/maintainers`, write access) | Merge pull requests, push to `main` | The branch ruleset, and the checks below. |
| The scheduled jobs (`RELEASE_TOKEN`) | Push their own generated files to `main` | The token is limited to this one repo and to file contents; it can't change workflows or settings. |

People who prepare data without a GitHub account (such as the sailing secretary) send it to a maintainer, who uploads it as a pull request.

## Why a data file can't run code

- **The app shows every field as plain text.** Programme, extras, events and tide values are put on the page with `textContent`, never as HTML, so a cell containing `<script>` shows as those characters. The race card and preview do the same.
- **Links are restricted.** The only links built from data are club-event links, and both the events job and the app drop any that aren't `https://` on `blackwatersailingclub.org.uk`.
- **The format guide** renders `docs/data-format.md` from the repo itself, escaping everything and allowing only web or same-site links.
- **CSV injection** (a cell such as `=HYPERLINK(...)` that a spreadsheet runs when someone opens the file) is rejected by `scripts/check-data.py`, along with any file over 2 MB.
- **Extra-date requests** from the issue form are checked field by field, stripped of control characters, length-limited, and never pasted into a shell command (see [automation.md](automation.md)).

## Pull requests from outside

A pull request from someone else's copy of the repo runs the **Build and deploy** check with a read-only token and **no secrets**, and never publishes. GitHub can also hold even that check until a maintainer approves it: set **Settings → Actions → General → Approval for running fork pull request workflows from contributors** to **Require approval for first-time contributors** (or for all outside collaborators).

## Denial of service

- **The site** is served by GitHub Pages' CDN, so traffic floods are GitHub's problem, not ours.
- **Issue spam** would only cost a glance: each request from an outsider stops at "waiting for approval". If it ever happens, **Settings → Moderation options → Interaction limits** restricts issues to existing contributors for a day to six months.
- **The weather forecast** is fetched by each visitor's browser from Open-Meteo, so one visitor can't use up another's allowance.

## Housekeeping

- **`RELEASE_TOKEN`** is a fine-grained token owned by a maintainer: this repo only, **Contents: Read and write**, nothing else. Give it an expiry (a year is fine) and replace it when the scheduled jobs start failing with an authentication error.
- **Keep the maintainers team small,** and remove people who step back.
- **Two-factor authentication** on every maintainer's GitHub account; the org can require it under **Settings → Authentication security**.
- **The Google Sheets template** is shared as view-only; people make their own copy, so nobody can change the original.
- **`data/tides-official.csv` is public.** See `scripts/tide/TIDES.md` about keeping it private if the club prefers.
