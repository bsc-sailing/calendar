# BSC Sailing Calendar

A phone-friendly sailing calendar for Blackwater Sailing Club (BSC), built from the club's season programme: races by fleet, events, training, high water and a weather forecast for every day.

**Open it here:** https://bsc-sailing.github.io/calendar/

Source code and issues: https://github.com/bsc-sailing/calendar

It works as an ordinary website in any browser on a phone, tablet or computer, so there is nothing to install. Bookmark the link if you like. Saving it as an app is optional (see below).

This is an unofficial version made from the printed programme. Check the club website and newsletters for updates.

## Using it

- **My fleets:** pick one or more fleets to see only their races, which are shown in red. Tap a fleet again to remove it, or tap **Reset** (or **All fleets**) to go back to everything. Your choice is remembered on your device.
- **Tap a day** for the full details: racing by fleet, events, training, the weather forecast and the tide.
- **BJRC** races (Blackwater Joint Racing Club, not run by BSC) count as racing. A day with no BSC fleet racing says "No club racing", since BJRC may still be racing.
- **Next on** moves to the following day's event once a day's first start was more than 8 hours ago.
- **Search** for a race or event, or tap the search box for quick filters such as "This weekend". The **Cadets** filter shows every day with cadet training, coaching or racing.
- **Swipe the "Next on" card** left for the next upcoming event and right to go back.
- **Add to calendar:** tap a day, then **Add this day to calendar**, or use **Add N days to calendar** at the bottom of the list to add everything currently shown (so filter by fleet, month or search first). It saves an `.ics` file that opens in your phone's Calendar. A racing entry runs from 1.5 hours before the first start to 3 hours after high water, to allow rigging and de-rigging time. Events and training are one entry per day at their start; training with a start TBC is added as an all-day entry, and anything else with no finish time listed lasts 3 hours by default (change `CONFIG.defaultMinutes` to alter this). Adding the same file again updates the entries rather than duplicating them. There is no live subscription feed: each download is a snapshot, so download again after the data changes.
- **Start TBC** means the coach or instructor sets the start time.
- **≈** before a time or height means the tide isn't printed in the programme and is estimated.
- **Season buttons** (2026, 2027 and so on) appear at the top when there is more than one season. The app opens on the current season and moves to the next one automatically once the current one has finished.
- **Grand Prix weekend** dates carry a gold badge, on the day list and in the day details.
- **GO SAIL** — see its own section below.

## Use it as a website, or save it as an app

**As a website:** just open the link in your browser. Everything works the same way, including search, filters, the weather forecast and **Add to calendar**. Your fleet choice is remembered in that browser. Add a bookmark, or use your browser's **Add to Home Screen** shortcut, to get back to it quickly.

**As an app (optional):** saving it gives you its own icon, opens it full-screen without the browser bars, and lets it open without a signal using the last copy saved on your device. The name on your home screen is **BSC Calendar**, with the club icon.

- **iPhone or iPad:** open the link in **Safari**, tap **Share**, then **Add to Home Screen**, then **Add**.
- **Android:** open it in **Chrome**, tap the **⋮** menu, then **Install app** (or **Add to home screen**).
- **Laptop (Chrome or Edge):** click the install icon at the right-hand end of the address bar.

The forecast needs an internet connection either way. If you see an old icon or name, remove the shortcut and add it again.

## Contributing

Changes go through a pull request, reviewed against `.github/CODEOWNERS`. To set this up on a repo (or check it's still in place):

1. **Repo → Settings → Rulesets → New branch ruleset.** Target `main`.
2. Turn on **Require a pull request before merging**, set **Required approvals: 1**, and turn on **Require review from Code Owners**.
3. Leave **"Do not allow bypassing the above settings"** off. This is what lets the code owner keep pushing routine updates straight to `main` (or merge their own PRs) without needing anyone else's sign-off — Organization Owners and repo Admins can bypass the rule, everyone else can't.

Worth knowing: GitHub never lets anyone approve their own pull request, code owner or not. So if the code owner is also the one opening PRs (the usual case here), that's exactly why step 3 matters — without it, the code owner would be the only person allowed to approve, yet unable to approve their own work, and stuck. Anyone who isn't a bypass-eligible Admin has no such workaround: their PRs always need the code owner's approval.

## Chart, course cards and GO SAIL

Tap **Race Courses** or **Race Marks Map** near the top of the app — each opens its own screen.

- **Chart:** the club's large-print race marks chart (March 2026). Tap the chart to open it full size and pinch-zoom in on it. A plain list of mark names sits below the small version.
- **Course cards:** all the club's printed courses, one card per wind direction and length. Filter by wind direction, or search by course code (for example `A3`) or a mark name. Each card expands to show its marks in sailing order, with a **Port** (red) or **Starboard** (green) badge. Club Line Gate and Finish show no badge, since you sail through a gate rather than round it.

### GO SAIL

A button at the bottom of each expanded course card. It opens a big, high-contrast, always-dark full-screen view of that course, sized to be readable at a glance on deck:

- The course code, the wind direction it's for, and today's forecast wind speed for that direction (when a forecast is available).
- A compact **START** / **HW** line — today's first start and high water, or "n/a" if there's no club racing that day.
- Every mark in order, abbreviated (Ballast H, Northey P., CLG), with its Port/Starboard badge on the right. Text size adjusts automatically so the whole course fits the screen with no scrolling, however many marks it has.
- Tap the chart to open it full size for zooming, the same as from the Race Marks Map screen.
- Tries to keep the screen awake while open (works on Chrome/Android; Safari doesn't support this, so it will still time out there).

**GO SAIL from a specific day:** open a day's details and tap **GO SAIL** next to **Add to calendar**. You're taken to Race Courses with a banner showing which day you're choosing for — pick a course and GO SAIL shows that day's own Start and HW (with the date shown alongside them, since it may not be today). Opening GO SAIL from the header button, rather than from a day, always uses today's start and tide.

To update either for a new season:
- **Chart:** replace `chart-2026.jpg` with a new export of the printed chart when it changes.
- **Course cards:** replace `courses-2026.csv` with the new season's data, keeping the same column headings (`Code, Family, Wind sector, Distance (miles), Order, Mark, Side, Rounding`), and update `CONFIG.coursesFile` if you rename it.

Neither file is year-aware the way the programme data is — a new chart or course-card export needs its filename (and `CONFIG.chartImage` / `CONFIG.coursesFile`) updated by hand, rather than just being uploaded under a new year.

## Tides & Weather

Tap **Tides & Weather** for a tide and forecast for any date, not just days that happen to have racing or an event. Enter a date directly, swipe left or right through days from the card itself, or pick from the next 14 days shown below it. If the selected day has racing, training or an event on, a note says which and offers to open its full details.

This is built from `tides.json`, which is a separate, independent dataset from each season's `programme-YEAR.csv` — kept apart deliberately, since the programme files are prepared by hand and shouldn't have anything automated writing to them. Wherever a date's real tide is known (it's in a season's printed programme), this screen shows that exact value, with no `≈`; only dates with no real data get the model's estimate. A weather-source link (to Open-Meteo) appears only when a forecast was actually shown; the estimated-tide footnote sits next to it when there is one, or on its own line when there's no forecast to attribute it to.

Weather shows as a 3-hour strip centred on that day's high water (2 hours before, at, and 2 hours after) — the same style as a day's own details screen — for whichever of those hours fall within the forecast's ~16-day range. Further out, only the tide shows.

Days in the app with no printed tide also take their `≈` tide from `tides.json`, so they improve whenever it's refitted. The coming week shows the club's published pontoon high waters (National Oceanography Centre, the same source as the printed programme) without the `≈`, refreshed daily. See `scripts/tide/TIDES.md`, "Checking against published tide predictions".

**`tides.json` refreshes itself weekly**, via `.github/workflows/update-tides.yml` — see `scripts/tide/TIDES.md` for the model itself (method, accuracy, and how it's validated), and the notes below for the automation around it.

- **Why a rolling 730-day file, not just each season's own blanks filled in:** it means a date has a sensible tide *before* that season's file even exists, and it means the fit keeps improving as more seasons of real data accumulate — `generate-tide-reference.py` pools every `programme-*.csv` it finds in the repo, not just the latest one.
- **Real data always wins:** for any date that's also covered by a season's actual printed programme, the file uses that exact value rather than a fresh prediction of it — so this screen and a day's own details can never show two different numbers for the same date.
- **Same authentication as Club Events, and the same reason:** pushes straight to `main` using the `RELEASE_TOKEN` secret described under **Club Events** below — no separate setup needed if that's already in place, since both workflows share the one secret.
- **Run it early once:** **Actions** tab → **Update tide reference** → **Run workflow**, rather than waiting up to a week for the first scheduled run.
- **What it does and doesn't touch:** only `tides.json`. A run that parses zero real training points, or finds no actual change once the file's own timestamp is ignored, doesn't commit — so a quiet week in the Actions history is normal, not a sign anything's wrong.
- **Worth glancing at each run:** the log prints an accuracy check (time and height error against the season's own known points) every time it runs. A sudden jump in those numbers is usually a sign something about a newly-added season's data looks unusual, worth a look before trusting its estimates.

## Club Events

Tap **Club Events** for Open Days, RYA courses, talks, socials and other club events — things the racing programme doesn't cover. Each item shows its date, a short excerpt, and a link to the club's own page for the full details and registration.

**Why this needs a workflow, not a direct fetch:** the club's website doesn't allow other sites to read its event feed directly from a visitor's browser (no CORS headers), so the app can't just pull it live the way it does the weather forecast. Instead, `.github/workflows/update-events.yml` runs once a day, fetches the club's public RSS feed (`https://blackwatersailingclub.org.uk/events/RSS`) from GitHub's own servers — not a browser, so the same restriction doesn't apply — and converts it to `events.json` using `scripts/update-events.py`.

**It pushes straight to `main` with no PR to approve**, authenticating as a real account (`jfairhead`) via a repository secret called `RELEASE_TOKEN`, rather than the default `github-actions[bot]` identity. This repo's ruleset bypass list has no entry for GitHub Actions itself — only for roles, teams and installed Apps — so a plain Actions-identity push would be blocked by the same "require a pull request" rule as anyone else's. Authenticating as a `maintainers`-team member instead sidesteps that: the push is allowed for the same reason any of your own pushes are. This is safe to grant because the workflow can only ever touch one file (`events.json`), sourced from one fixed URL, and every field from it is rendered as plain text in the app — never as HTML — so nothing it fetches can affect how the app behaves. It does **not** extend to changes to the workflow file itself: `.github/workflows/*.yml` still needs a token with the `workflow` permission to push, and still goes through the normal PR review — so what the bot is *allowed to do* is always reviewed, even though its routine daily output isn't.

- **First-time setup — `RELEASE_TOKEN`:** create a fine-grained personal access token scoped to only this repo, **Contents: Read and write** (nothing else needed), under the `jfairhead` account (or whichever account is on the `maintainers` team). Add it at **Settings → Secrets and variables → Actions → New repository secret**, named `RELEASE_TOKEN`. This is a separate token from the one used to sync releases from a laptop — that one additionally needs the **Workflows** permission, since Contents alone can't create or update anything under `.github/workflows/`.
- **Run it early once:** after merging, trigger it by hand from the repo's **Actions** tab → **Update club events** → **Run workflow**, rather than waiting up to a day for the first scheduled run.
- **What it does and doesn't touch:** only `events.json` — never the programme, courses, or app code. A feed that returns zero events (an outage, or the club changing its page) is treated as a failure, not "no events" — the existing file is left alone rather than overwritten, and the run logs a warning. Only upcoming events are shown in the app; past ones drop off the list on their own as the date passes. A run that finds no real change doesn't commit at all — the content comparison ignores the file's own `generated` timestamp, so a daily no-op run doesn't create daily noise in the repo's history.
- **If it stops finding anything:** the club's feed URL or structure has probably changed. Check `https://blackwatersailingclub.org.uk/events/RSS` still returns XML in that shape, and adjust `scripts/update-events.py` if not.

## Extra dates

Races, socials or training added after the printed programme go in **`extras-YEAR.csv`** (for example `extras-2026.csv`), not in the programme file. The app merges it into that year's season and marks each one **Extra**, with "Added after the printed programme" in the day's details. Keeping them separate means re-exporting the printed programme never wipes them. Tides for these dates come from `tides.json` automatically.

Same columns as the programme, plus a `Request` column (the issue it came from). An informal race is one row with no fleet: `Event` = `Informal race`, `Race / series` = its name, `Detail` = where and who, for example "On the river – All classes welcome. Not part of any series."

**Requesting one.** Anyone with a GitHub account can open an issue with the **Add an extra date** form (**Issues → New issue**). Nothing reaches the app without a maintainer's approval:

1. When the person asking is a member of the bsc-sailing org, a workflow checks the form straight away. Otherwise it waits until a maintainer adds the `approved` label (only people with triage or write access can label). Requests from strangers therefore cost nothing but a glance.
2. If a field doesn't make sense (a date in the past, a start time that isn't `HH:MM`), it comments on the issue saying what to fix. Editing the issue re-checks it.
3. Otherwise it opens a pull request adding the row to `extras-YEAR.csv`. The PR is opened by `github-actions[bot]`, so either code owner can approve it, including whoever asked.
4. Merging the PR publishes it and closes the issue.

Every field is treated as untrusted text: checked against what it should look like, stripped of control characters, length-limited, read from the event file rather than pasted into a shell command, and shown in the app as plain text only.

**One-off setup:** create an `approved` label (**Issues → Labels → New label**); turn on **Settings → Actions → General → Allow GitHub Actions to create and approve pull requests** (it may also need allowing at org level, under the org's own Settings → Actions); and make sure `.github/CODEOWNERS` lists both maintainers, each with write access.

You can still edit `extras-YEAR.csv` directly on GitHub (pencil icon) for a quick fix. Check it afterwards with `?check`, which also reports how many extra rows were loaded.

## Adding a new season (2027 and beyond)

Each season is one file named **`programme-YEAR.csv`**, for example `programme-2027.csv`. The app looks for the files for last year, this year and the next two years, so there is nothing to register and no code to change.

1. Prepare the season's data in the format below. `programme-2026.csv` is a worked example, and `programme-template.csv` shows the column headings with a few sample rows. A spreadsheet (Google Sheets or Excel) is the easiest place to edit.
2. Export it as CSV and name it `programme-YEAR.csv`.
3. Upload it to this repo (GitHub: **Add file**, then **Upload files**). Leave the earlier seasons in place.
4. Wait a minute or two, then close and reopen the app. The new season appears as a button, and becomes the default once the previous season has finished.

To check a file before you rely on it, open the app with `?check` on the end of the address (for example `https://bsc-sailing.github.io/calendar/?check`). It lists problems such as dates in the wrong format, start times that aren't `HH:MM` or `TBC`, racing rows with no start time, and days with no tide.

If you still have the older single `programme.csv` in the repo it keeps working: it's treated as the season for the year of its dates, unless a `programme-YEAR.csv` covers that year. You can delete it once `programme-2026.csv` is there.

**Estimated tides (the `≈` ones):** for dates the club's programme doesn't print a tide for, `scripts/tide/tidefit.py` and `tide_predict.py` generate one and fill the blank rows automatically — see `scripts/tide/TIDES.md` for the full method, its accuracy, and the exact commands to run for a new season.

### The columns

Each row is one date plus one fleet (or one event or training item with no fleet). The tide and start time repeat on every row for the day. Tide columns can be left blank; the app then just hides the tide.

| Column | What it holds |
| --- | --- |
| Date | `YYYY-MM-DD` |
| High water, Tide height (m) | Time as `HH:MM` and height in metres |
| Tide source | `Programme`, or `Estimated` for tides not printed in the programme |
| Start time | `HH:MM`, `TBC` (set by the coach or instructor), or blank |
| Fleet | The fleet name, exactly as spelled elsewhere in the file (Fast / Fireball, Medium, Wayfarer, Sprite, Short course, Fridays, Mirror, Cruiser). Blank for events and training. The fleet buttons come from these names, so a new fleet just works |
| Race start order | 1 to 6, the order fleets start in. Only on racing rows |
| Event | A club-wide event (Regatta, Evening race, BJRC Blackwater Cup, Cadet week, Mirror sailing, No racing and so on) |
| Training | Cadet training, Cadet coaching, Adult RYA, or "[Fleet] training" |
| GP weekend | `TRUE` on Grand Prix weekend dates, otherwise `FALSE` |
| Race / series, Race no(s) | The trophy or series for a fleet-specific race, and its race numbers such as `1&2` |
| Detail | Extra information, such as a start location |

An event that covers several fleets has one row per fleet, all with the same Event. Extra columns (such as Issue) are ignored, and the rows can be in any order.

Weekly sessions (Mirror sailing and Beach Club) are named in `CONFIG.weekly` near the top of `index.html` and always show, the same as any other event. If a future season uses different names for these, change that list.

## Version and support

The version number is at the bottom of the app. Tap **Support info** there for the app version, the seasons loaded (with the date each data file was last updated), whether the offline copy is active, which saved copy is in use, and when Club Events and the tide reference were each last updated — a quick way to spot either of their scheduled jobs having quietly stopped, without needing to check GitHub. That is usually enough to work out whether someone is seeing an old version. Add `?check` to the address for a data check. `CHANGELOG.md` lists what changed in each version.

### Releasing a new version

A release is a zip called `bsc-sailing-app.zip` containing the changed files at their repo paths, plus a `release-manifest.json`:

```json
{ "version": "2.16.2", "base_version": "2.15.3",
  "base_files":  { "index.html": "<git blob hash it was built from>", "new-file.csv": null },
  "known_files": { "index.html": ["<an earlier release's hash>"] } }
```

`version` must match `CONFIG.version` in `index.html`, `VERSION` in `sw.js`, and the newest heading in `CHANGELOG.md` (bump all three, and `CONFIG.released`). `base_files` records each file as it was when the release was built (`git hash-object <file>`), or `null` for a new file; `known_files` lists other copies that are safe to replace, such as an earlier release's.

To apply one, download it and run `./scripts/sync-release.sh` from the repo root. It:

1. finds the newest `bsc-sailing-app*.zip` in `~/Downloads` (or takes a path);
2. checks the version numbers inside agree, and refuses a zip older than the repo unless you insist;
3. switches to the zip's copy of `sync-release.sh` first, if it has a newer one;
4. fast-forwards if GitHub is ahead (the scheduled data jobs push there daily);
5. warns before overwriting any file changed on GitHub since the release was built (data files the scheduled jobs own are exempt), asking even with `-y`;
6. tags a backup, copies the files in, commits, pushes, tags the version, and waits for the live site to show it;
7. moves the zip to `~/Downloads/bsc-sailing-app-applied/`, so the next download keeps the plain name.

Add `-y` to skip the routine questions.

## Files

| File | What it does |
| --- | --- |
| `index.html` | The app. Settings, including the forecast location, are in `CONFIG` at the top of the script. |
| `programme-2026.csv`, `programme-2027.csv`, ... | One programme file per season. |
| `extras-2026.csv`, `extras-2027.csv`, ... | Dates added after the printed programme. See **Extra dates**. |
| `programme-template.csv` | Column headings and sample rows for a new season. It is not loaded by the app. |
| `manifest.webmanifest` | Name, colours and icons, so phones can install it. |
| `sw.js` | Lets it open offline. It always tries the internet first, so updates appear straight away. |
| `CHANGELOG.md` | What changed in each version. |
| `icon-192.png`, `icon-512.png`, `apple-touch-icon.png` | The app icon (the club roundel on white). |
| `logo.png` | The club roundel shown next to the title. If it is missing the page just leaves it out. |
| `chart-2026.jpg` | The printed race-marks chart (large-print version). |
| `courses-2026.csv` | The course cards: one row per mark, grouped into courses. |
| `events.json` | Club events, generated by `.github/workflows/update-events.yml`. Don't hand-edit it — changes get overwritten on the next scheduled run. |
| `tides.json` | The rolling 24-month tide reference, generated by `.github/workflows/update-tides.yml`. Don't hand-edit it either, for the same reason. |
| `.github/workflows/update-events.yml`, `scripts/update-events.py` | The scheduled job that keeps `events.json` current. |
| `.github/workflows/update-tides.yml`, `scripts/tide/generate-tide-reference.py` | The scheduled job that keeps `tides.json` current. |
| `.github/ISSUE_TEMPLATE/extra-date.yml`, `.github/workflows/extra-date.yml`, `scripts/add-extra-date.py` | The **Add an extra date** form, and the workflow that turns an approved request into a pull request. |
| `.github/workflows/check-official-tides.yml`, `scripts/tide/fetch-official-tides.py`, `scripts/tide/official-tides.json` | The daily check against the club's published tide table (and optionally ADMIRALTY), and its settings. |
| `tides-official.csv` | Published high waters collected by that check, with what we'd estimated for each date beforehand. Generated: don't hand-edit. |
| `scripts/tide/tidefit.py`, `tide_predict.py`, `TIDES.md`, `tide-model-2026.json` | The tide model itself — fitting it, predicting from it, and documenting it. See `scripts/tide/TIDES.md`. |
| `.github/CODEOWNERS` | Who has to approve a pull request — see **Contributing** above. |
| `scripts/sync-release.sh` | Applies a downloaded release zip to this repo: backs up the current version as a tag, copies the files in, commits, pushes, tags, and confirms the live site picked it up. Run it from the repo root as `./scripts/sync-release.sh`. See **Releasing a new version**. |

Weather data is from [Open-Meteo.com](https://open-meteo.com/).
