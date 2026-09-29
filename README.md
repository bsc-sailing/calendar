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
- **Add to calendar:** tap a day, then **Add this day to calendar**, or use **Add N days to calendar** at the bottom of the list to add everything currently shown (so filter by fleet, month or search first). It saves an `.ics` file that opens in your phone's Calendar. Races are one entry per day at the first start; training with a start TBC is added as an all-day entry. The programme has no finish times, so timed entries last 3 hours unless a time range is given (change `CONFIG.defaultMinutes` to alter this). Adding the same file again updates the entries rather than duplicating them. There is no live subscription feed: each download is a snapshot, so download again after the data changes.
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

## Club Events

Tap **Club Events** for Open Days, RYA courses, talks, socials and other club events — things the racing programme doesn't cover. Each item shows its date, a short excerpt, and a link to the club's own page for the full details and registration.

**Why this needs a workflow, not a direct fetch:** the club's website doesn't allow other sites to read its event feed directly from a visitor's browser (no CORS headers), so the app can't just pull it live the way it does the weather forecast. Instead, `.github/workflows/update-events.yml` runs once a day, fetches the club's public RSS feed (`https://blackwatersailingclub.org.uk/events/RSS`) from GitHub's own servers — not a browser, so the same restriction doesn't apply — and converts it to `events.json` using `scripts/update-events.py`. If the content changed, it opens a pull request for review, the same as any other change, rather than pushing straight to `main`.

- **First-time setup:** the token used to sync releases needs the **Workflows** permission (Contents alone isn't enough for a token to create or update anything under `.github/workflows/`) — add it under **Repository permissions** on the token, the same place as Contents.
- **Run it early once:** after merging, trigger it by hand from the repo's **Actions** tab → **Update club events** → **Run workflow**, rather than waiting up to a day for the first scheduled run.
- **What it does and doesn't touch:** only `events.json` — never the programme, courses, or app code. Only upcoming events are shown; past ones drop off the list on their own as the date passes.
- **If it stops finding anything:** the club's feed URL or structure has probably changed. Check `https://blackwatersailingclub.org.uk/events/RSS` still returns XML in that shape, and adjust `scripts/update-events.py` if not.

## Adding a new season

## Adding a new season (2027 and beyond)

Each season is one file named **`programme-YEAR.csv`**, for example `programme-2027.csv`. The app looks for the files for last year, this year and the next two years, so there is nothing to register and no code to change.

1. Prepare the season's data in the format below. `programme-2026.csv` is a worked example, and `programme-template.csv` shows the column headings with a few sample rows. A spreadsheet (Google Sheets or Excel) is the easiest place to edit.
2. Export it as CSV and name it `programme-YEAR.csv`.
3. Upload it to this repo (GitHub: **Add file**, then **Upload files**). Leave the earlier seasons in place.
4. Wait a minute or two, then close and reopen the app. The new season appears as a button, and becomes the default once the previous season has finished.

To check a file before you rely on it, open the app with `?check` on the end of the address (for example `https://bsc-sailing.github.io/calendar/?check`). It lists problems such as dates in the wrong format, start times that aren't `HH:MM` or `TBC`, racing rows with no start time, and days with no tide.

If you still have the older single `programme.csv` in the repo it keeps working: it's treated as the season for the year of its dates, unless a `programme-YEAR.csv` covers that year. You can delete it once `programme-2026.csv` is there.

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

The version number is at the bottom of the app. Tap **Support info** there for the app version, the seasons loaded (with the date each data file was last updated), whether the offline copy is active and which saved copy is in use. That is usually enough to work out whether someone is seeing an old version. Add `?check` to the address for a data check. `CHANGELOG.md` lists what changed in each version.

To release a new version: change `CONFIG.version` and `CONFIG.released` in `index.html`, change `VERSION` in `sw.js` to match, and add a line to `CHANGELOG.md`.

## Files

| File | What it does |
| --- | --- |
| `index.html` | The app. Settings, including the forecast location, are in `CONFIG` at the top of the script. |
| `programme-2026.csv`, `programme-2027.csv`, ... | One programme file per season. |
| `programme-template.csv` | Column headings and sample rows for a new season. It is not loaded by the app. |
| `manifest.webmanifest` | Name, colours and icons, so phones can install it. |
| `sw.js` | Lets it open offline. It always tries the internet first, so updates appear straight away. |
| `CHANGELOG.md` | What changed in each version. |
| `icon-192.png`, `icon-512.png`, `apple-touch-icon.png` | The app icon (the club roundel on white). |
| `logo.png` | The club roundel shown next to the title. If it is missing the page just leaves it out. |
| `chart-2026.jpg` | The printed race-marks chart (large-print version). |
| `courses-2026.csv` | The course cards: one row per mark, grouped into courses. |
| `events.json` | Club events, generated by `.github/workflows/update-events.yml`. Don't hand-edit it — changes get overwritten on the next scheduled run. |
| `.github/workflows/update-events.yml`, `scripts/update-events.py` | The scheduled job that keeps `events.json` current. |

Weather data is from [Open-Meteo.com](https://open-meteo.com/).
