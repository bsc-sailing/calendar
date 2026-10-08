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
- **Daylight:** each day's details show sunrise, sunset and hours of daylight for Heybridge Basin, and say when high water falls after sunset or before sunrise. Tides & Weather shows the same, and GO SAIL shows the day's sunset. These are calculated on your device, so they work for any date and offline.
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

## Tides & Weather

Tap **Tides & Weather** for a tide and forecast for any date, not just days that happen to have racing or an event. Enter a date directly, swipe left or right through days from the card itself, or pick from the next 14 days shown below it. If the selected day has racing, training or an event on, a note says which and offers to open its full details.

Wherever a date's real tide is known (it's printed in a season's programme), this screen shows that exact value, with no `≈`. The coming week shows the club's published pontoon high waters (National Oceanography Centre, the same source as the printed programme), also without the `≈`. Every other date gets an estimate from the club's own tide model, which is refitted automatically as more real data arrives — see `scripts/tide/TIDES.md` for the method and its accuracy, and [docs/automation.md](docs/automation.md) for the scheduled jobs.

Weather shows as a 3-hour strip centred on that day's high water (2 hours before, at, and 2 hours after), for whichever of those hours fall within the forecast's ~16-day range. Further out, only the tide shows.

## Club Events

Tap **Club Events** for Open Days, RYA courses, talks, socials and other club events — things the racing programme doesn't cover. Each item shows its date, a short excerpt, and a link to the club's own page for the full details and registration. The list is refreshed daily from the club website's events feed (see [docs/automation.md](docs/automation.md)).

## Extra dates

Races, socials or training added after the printed programme are shown with an **Extra** badge and "Added after the printed programme" in the day's details. Anyone with a GitHub account can ask for one with the **Add an extra date** form (**Issues → New issue**); a maintainer approves it, and it appears once the resulting pull request is merged. How to add or change one is in [docs/updating-data.md](docs/updating-data.md).

## Keeping the data up to date

The season programme, extra dates and course cards are files in the `data/` folder (the chart is in `app/assets/`). [docs/updating-data.md](docs/updating-data.md) covers adding a new season, fixing a date, adding an extra date and replacing the course cards or chart, step by step, from a web browser without installing anything.

For whoever prepares the programme, with or without a GitHub account, the **[format guide](https://bsc-sailing.github.io/calendar/guide.html)** on the live site has everything in one place:

- the column-by-column format, with a worked example comparing a race-card day with the app's rows (the same text as [docs/data-format.md](docs/data-format.md));
- a **Google Sheets template** (a "make a copy" link to a sheet in the maintainer's Google Drive, which must stay shared as "Anyone with the link: Viewer") and an **Excel template** (`templates/programme-template.xlsx`, regenerated with `scripts/make-template-xlsx.py`), both with the headings, formats and drop-down lists set up;
- **[Preview a file](https://bsc-sailing.github.io/calendar/?preview):** open a programme CSV from your own device in the app, with a data check that gives line numbers. Nothing is uploaded;
- **[Race card](https://bsc-sailing.github.io/calendar/racecard.html):** any published season, or a file from your device, laid out like the printed race card, for printing or saving as a PDF.

Every change is checked automatically before it goes live, and goes through a pull request so there's a record of what changed and why.

## For maintainers

### Repo layout

| Folder | What's in it |
| --- | --- |
| `app/` | The app itself: `index.html` (settings in `CONFIG` at the top of the script), `sw.js` (the offline copy) and `manifest.webmanifest` (name, colours and icons for saving it as an app). Also `guide.html` (the format guide) and `racecard.html` (the printable race card). |
| `app/assets/` | Images: the app icons, the club logo and the race marks chart. |
| `data/` | Everything the app reads: `programme-YEAR.csv`, `extras-YEAR.csv`, `courses-2026.csv`, and the generated `events.json`, `tides.json` and `tides-official.csv` (don't hand-edit those three; the scheduled jobs rewrite them). |
| `templates/` | `programme-template.csv` and `programme-template.xlsx`: column headings and sample rows for a new season. Published for download, but not loaded by the app. |
| `docs/` | How-to guides: updating the data, the data format, releasing, and the automation. Published too, so `guide.html` can show `data-format.md`. |
| `scripts/` | The site build and data check, the release script, the events and extra-date scripts, and the tide model (`scripts/tide/`). |
| `.github/` | Workflows, the extra-date issue form, and `CODEOWNERS`. |

The live site doesn't have these folders: `scripts/build-site.py` publishes every file from `app/`, `app/assets/`, `data/`, `templates/` and `docs/` side by side, at the same addresses as before the repo was split up (`…/calendar/programme-2026.csv` and so on). So moving files between those folders never breaks bookmarks, saved apps or the offline copy. Two files with the same name in different folders stop the build.

### How changes reach the live site

`.github/workflows/deploy.yml` builds and publishes the site whenever something lands on `main`: a merged pull request, a direct push, or one of the scheduled data jobs. It checks the season data (`scripts/check-data.py`), assembles the site (`scripts/build-site.py`) and publishes it, usually within a minute or two. Every pull request runs the same checks without publishing, so a broken data file shows as a red cross on the PR rather than on the live site. After publishing a new app version, it tags it (`v2.17.0` and so on).

**One-off setup:** **Settings → Pages → Build and deployment → Source: GitHub Actions** (instead of "Deploy from a branch").

### Releasing, pull requests and reviews

Changes go through pull requests, so each one has a record of what changed and why. Releases from a downloaded zip use `./scripts/sync-release.sh`, which opens the pull request for you. The full process, the branch ruleset and code owners, and how to roll back are in [docs/releasing.md](docs/releasing.md).

### Scheduled jobs

Club events (daily), the tide reference (weekly), the published-tide check (daily) and extra-date requests each run as a GitHub Actions workflow. What they touch, the `RELEASE_TOKEN` they share, and what to check if one stops are in [docs/automation.md](docs/automation.md).

### Security

Who can change what, why a data file can't run code in the app, and the settings worth keeping on are in [docs/security.md](docs/security.md).

## Version and support

The version number is at the bottom of the app. Tap **Support info** there for the app version, the seasons loaded (with the date each data file was last updated), whether the offline copy is active, which saved copy is in use, and when Club Events and the tide reference were each last updated — a quick way to spot either of their scheduled jobs having quietly stopped, without needing to check GitHub. That is usually enough to work out whether someone is seeing an old version. Add `?check` to the address for a data check. `CHANGELOG.md` lists what changed in each version.

Weather data is from [Open-Meteo.com](https://open-meteo.com/).
