# Updating the data

Everything the app shows about the season comes from files in the `data/` folder. This page covers the everyday changes, step by step, from a web browser. Nothing needs installing.

| File | What it is | Who changes it |
| --- | --- | --- |
| `data/programme-YEAR.csv` | The season's printed programme, one file per year | A maintainer, once a year plus corrections |
| `data/extras-YEAR.csv` | Races, socials and training added after the programme was printed | A maintainer, or via the **Add an extra date** form |
| `data/courses-2026.csv` | The course cards | A maintainer, when the courses change |
| `app/assets/chart-2026.jpg` | The race marks chart | A maintainer, when the chart changes |
| `data/events.json`, `data/tides.json`, `data/tides-official.csv` | Club events and tides | Nobody: scheduled jobs rewrite them (see [automation.md](automation.md)) |

The format of the programme and extras files is in [data-format.md](data-format.md).

## How every change works

Changes are made on a branch and go live through a pull request (PR). That way each change is checked automatically before it's published, and there's a record of what changed and why.

1. Make the change on GitHub (the sections below say how). At the end, GitHub asks how to save it: choose **Create a new branch for this commit and start a pull request**, give it a short description, and click **Propose changes**, then **Create pull request**.
2. Wait a minute for the **Build and deploy** check on the PR. A green tick means the data is fine. A red cross means something would show wrongly: click **Details** to see which file and line, fix it on the same branch (edit the file again from the PR's branch), and the check runs again.
3. **Merge** the PR. If you're a maintainer you can merge your own straight away; otherwise a maintainer approves it first.
4. The change is live a minute or two later. Close and reopen the app to see it.

If a change turns out to be wrong after merging, open the merged PR and click **Revert**, then merge the PR that creates.

## Correct a date in the programme

For a small fix (a start time, a race name, a missing row):

1. Open `data/programme-YEAR.csv` on GitHub and click the **pencil** icon (Edit this file).
2. Find the row: each line starts with its date, so use the browser's Find for `2027-05-16`, say.
3. Edit the text between the commas. Every row for that day has the same date, tide and start time, so change all of them if you're changing one of those.
4. Save as a pull request, as above.

For bigger changes, download the file (**…** menu → **Download**), edit it in a spreadsheet, save it as CSV, and upload it over the old one (below).

## Add a new season

1. Prepare `programme-YEAR.csv` in the format in [data-format.md](data-format.md). Starting from the Google Sheets or Excel template (both linked from the format guide), or a copy of last year's file, is easiest. A CSV downloaded from Google Sheets is named after the sheet, so rename it `programme-YEAR.csv` before uploading. Check it first with the app's preview (`https://bsc-sailing.github.io/calendar/?preview`) and the race card (`…/racecard.html`); both open a file from your own device without uploading it.
2. On GitHub, open the `data` folder, then **Add file → Upload files**, and drop the file in. Leave the earlier seasons in place.
3. Choose **Create a new branch for this commit and start a pull request**, and create the PR.
4. Check the result of **Build and deploy** on the PR, as above. It reports any row that wouldn't show correctly, by line number.
5. Merge it. The new season appears as a button at the top of the app, and becomes the one it opens on once the current season has finished. The app looks for files for last year, this year and the next two years, so there's nothing else to change.

**Tides the programme doesn't print** (coaching days, Friday courses) can be left blank: the app fills them with an estimate marked `≈`, and that estimate improves automatically. To write the estimates into the file instead, see `scripts/tide/TIDES.md`, "Two ways to use this".

If someone without a GitHub account prepares the file (the sailing secretary, say), point them at the format guide on the live site (`https://bsc-sailing.github.io/calendar/guide.html`): it has the template, the format, and the preview and race-card tools, so they can check it themselves. They then email it to a maintainer, who uploads it as above.

## Add an extra date

Races, socials or training added after the programme was printed go in `data/extras-YEAR.csv`, not the programme file, so re-exporting the programme never wipes them. The app shows them with an **Extra** badge.

- **The easy way:** **Issues → New issue → Add an extra date**, and fill in the form. A maintainer's own requests turn into a pull request straight away; anyone else's wait for a maintainer to add the `approved` label. Merge the PR and it's live.
- **By hand:** edit `data/extras-YEAR.csv` like the programme (above). It has the same columns plus `Request` (the issue it came from, or blank). An informal race is one row with no fleet: `Event` = `Informal race`, `Race / series` = its name, `Detail` = where and who, for example "On the river – All classes welcome. Not part of any series."

## Replace the course cards or chart

- **Course cards:** upload the new file into `data/` with the same column headings (`Code, Family, Wind sector, Distance (miles), Order, Mark, Side, Rounding`). Keeping the name `courses-2026.csv` needs no other change; if you give it a new name (say `courses-2027.csv`), also change `coursesFile` in `CONFIG` near the top of `app/index.html`, and the same name in the `FILES` list in `app/sw.js`, in the same pull request.
- **Chart:** upload the new image into `app/assets/`. The same applies: keeping the name `chart-2026.jpg` needs nothing else; a new name needs `chartImage` (and `chartImageDate`) in `CONFIG`, and the `FILES` list in `app/sw.js`, changed in the same PR.

Unlike the programme, these two aren't picked up by year automatically. The build check fails if the app asks for a file that isn't there, so a missed rename can't reach the live site.

## Checking what's live

Open the app with `?check` on the end of the address (`https://bsc-sailing.github.io/calendar/?check`) to see the data check for the season on screen, including how many extra dates were loaded. **Support info**, at the bottom of the app, shows which seasons are loaded and when each file last changed.
