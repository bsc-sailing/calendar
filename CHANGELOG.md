# Changelog

Version numbers are in `CONFIG.version` in `index.html` and `VERSION` in `sw.js`. Keep the two the same, and add a line here for every release. The version is shown at the bottom of the app, with more detail under **Support info**.

## 2.16.6 – 6 Oct 2026
- Extra-date requests are recognised by the form's questions, not the issue title, so retyping the title no longer stops a request being processed. Once a request is checked, its title is set automatically to "Extra date: YYYY-MM-DD Name".

## 2.16.5 – 6 Oct 2026
- Extra-date requests: whether to process one straight away now depends on the requester's write access to the repo, checked with GitHub, instead of the org membership shown on the issue (private org members showed as outsiders, so their requests were skipped). Duplicate runs when an issue is created are avoided, and requests from outside the club get a reply saying a maintainer will review them.

## 2.16.4 – 6 Oct 2026
- Sunrise and sunset for Heybridge Basin, worked out on the device for any date (no data feed, works offline): a **Daylight** section in each day's details, a line in Tides & Weather, and SUNSET on the GO SAIL screen. Notes when high water falls after sunset or before sunrise.

## 2.16.3 – 6 Oct 2026
- Which high water to show is now the one nearest solar noon (13:00 in summer, 12:00 in winter) rather than 12:00 all year, so the choice no longer flips between morning and evening from one day to the next (19 Oct showed 06:08 after 18 Oct's 18:02; it now shows 19:30).
- When a day's two high waters are about equally far from midday (roughly 6 am and 6 pm, a few days a month), both are shown: in the day's details, and as "19:30 & 06:08" in Tides & Weather.

## 2.16.2 – 6 Oct 2026
- `sync-release.sh` does the whole release from a downloaded `bsc-sailing-app.zip`: fast-forwards if GitHub is ahead, reads the version from the zip's `release-manifest.json` and checks `index.html`, `sw.js` and `CHANGELOG.md` all agree, refuses an older zip unless you insist, warns before overwriting anything changed on GitHub since the release was built, updates itself if the zip has a newer copy, and moves the applied zip to `~/Downloads/bsc-sailing-app-applied/`.

## 2.16.1 – 6 Oct 2026
- The daily tide check now reads the club website's 7-day pontoon table (National Oceanography Centre, the same source as the printed programme) instead of needing an ADMIRALTY key. The coming week shows those times without the `≈`, credited to NOC. ADMIRALTY is now an optional comparison.

## 2.16.0 – 6 Oct 2026
- Extra dates: `extras-YEAR.csv` for races and events added after the printed programme, shown with an **Extra** badge. Three added: Blindfold Racing (16 Oct), Postcard Race (23 Oct), Christmas Challenge (22 Dec).
- **Add an extra date** issue form, with a workflow that turns approved requests into a pull request.
- Tide model fixed to treat programme times as UK clock time (GMT/BST) rather than UTC, cutting the typical timing error from about 50 to about 28 minutes.
- Days without a printed tide now use `tides.json`, so their estimates improve whenever it's refitted.
- Daily check against official ADMIRALTY tide predictions (needs a free API key; see `scripts/tide/TIDES.md`), which records estimate accuracy and feeds official points into the model.
- GoatCounter visit counting.

## 2.15.3 – 1 Oct 2026
- Reordered the nav buttons: Race Courses, Race Marks Map, Tides & Weather, Club Events — groups the three sailing-data screens together, with Club Events on its own at the end.

## 2.15.2 – 1 Oct 2026
- Nav buttons (Race Courses, Race Marks Map, Club Events, Tides & Weather) are now equal width and share the exact same look as the filter pills, rather than a smaller custom size.
- GO SAIL's and the full-size chart's Close buttons now match that same pill style too, instead of a filled dark box.
- Fixed a likely cause of the stray highlight sometimes seen between adjacent fleet/filter buttons after tapping one on iOS: buttons are now explicitly blurred after a touch tap (never after a keyboard activation, so keyboard focus indication is untouched).
- Tides & Weather: the cross-reference note no longer says "see details" twice (once in the text, once on the button next to it). The forecast source link no longer shows on a date too far ahead to have a forecast — it was being shown regardless, which made no sense with nothing to attribute.
- Add to calendar: a racing entry now runs from 1.5 hours before the first start to 3 hours after high water, to allow rigging and de-rigging time, rather than a flat 3 hours from the start. Noted on the main page footer.
- Support info's "updated" lines for Club Events and the tide reference now say what they actually measure — when the *content* last changed, not when the job last ran. A manually-triggered run that finds nothing new won't move this number, which is correct, if easy to misread as the job not having run at all.

## 2.15.1 – 1 Oct 2026
- Support info now shows when Club Events and the tide reference were each last updated — the easiest way to notice either scheduled job has quietly stopped working, without checking GitHub.
- Nav buttons now wrap their own text onto two lines (e.g. "Race / Courses") instead of the whole row wrapping — all four fit on one line as a result.
- Tides & Weather: swipe the detail card left/right to step through days, the same way the home screen's "Next on" card does. Weather now shows the same 3-hour strip (2 hours either side of high water) used on a day's own details screen, rather than a single midday snapshot, with a source link and — when the tide is estimated — a footnote saying so next to it. The cross-reference note now says what's actually on (racing, training, or an event) instead of "something."
- Fixed a possible horizontal scrollbar on the Tides & Weather screen, most likely from the native date picker on iOS.
- Made the Race Courses / Race Marks Map / Club Events / Tides & Weather title row match how GO SAIL and the day sheet already positioned their Close button (anchored to the top, not vertically centred) — the one real inconsistency found while investigating an ongoing report that Close still isn't fully clear of content on some screens. Not confirmed as the actual fix; still needs a fresh screenshot to diagnose properly if it persists.

## 2.15.0 – 30 Sep 2026
- New **Tides & Weather** screen, alongside Race Courses, Race Marks Map and Club Events — a tide and (within ~16 days) forecast for any date, via a date picker or the next 14 days listed below it. Built from the new `tides.json` reference: any date with a real printed tide shows it exactly, with no `≈`; only genuinely unknown dates get the estimate. If the selected date has racing or an event on, a note offers to open its full day details.
- The four buttons under the title now wrap onto two lines rather than fitting one — a deliberate trade-off to make room for the new screen.
- Found and fixed a real bug in the new screen's own code while testing it: the "select today by default" logic was checking the wrong condition and would always try to select today, even on a date tides.json doesn't cover, rather than falling back sensibly.

## Unreleased (docs/tooling only — no app code changed)
- Added `tides.json`: a rolling 24-month estimated-tide reference, refreshed weekly by `.github/workflows/update-tides.yml`, the same pattern as the club events workflow. It pools every `programme-*.csv` in the repo for training data, not just the latest season, so accuracy should improve as more years accumulate. This is a standalone dataset for now — **the app doesn't read it yet**; that's a deliberate next step, not done in this pass.
- Ran the tide model against the full `programme-2026.csv` (all 162 dates, both real and already-estimated) as a dedicated accuracy check — nothing in that file was changed. Found and documented a real, worthwhile insight in the process: the model disagrees with real recorded tide *times* more on the days it was trained on (RMS 50 min) than on the already-published estimates (RMS 36 min), because the training fit only ever matched height at a known time, never validated predicted timing — now explained properly in TIDES.md.
- Found and fixed two real bugs in the scheduled-commit logic while building the tides workflow, and fixed the same two in the existing events workflow: (1) `git diff --quiet` doesn't detect a file that isn't tracked by git yet, so a brand-new `tides.json` would have silently failed to commit on its first-ever run; (2) both `events.json` and `tides.json` carry their own `generated` timestamp, which made every run look "changed" even when the real data was identical, defeating the point of skipping no-op commits. Both fixed by comparing content with that field stripped out, verified against real before/after scenarios, not just read through.
- Added `scripts/tide/` — the harmonic tide model behind every `≈ Estimated` value, previously undocumented and only ever run once by hand. `tidefit.py` fits it from a season's printed high-water points; `tide_predict.py` fills in a whole season's blank tide rows in one command. `TIDES.md` documents the method, its accuracy (cross-validated, not just self-reported), and — importantly — a real overfitting mistake found and fixed while rebuilding it: the first attempt included two more constituents (K2, P1) that are too close in frequency to resolve from isolated daily high-water points rather than a continuous record, and it produced physically impossible heights (10+ m) between the days it was trained on despite fitting those days closely. Dropping to 5 well-separated constituents fixed it; see TIDES.md for the numbers and reasoning, so this doesn't get re-introduced by mistake later.
- Fixed a stray duplicate "Adding a new season" heading in README.md.

## 2.14.3 – 30 Sep 2026
- More top clearance on every screen with a Close button (Race Courses, Race Marks Map, Club Events, GO SAIL, the day-details sheet, the full-size chart) — the previous increase still wasn't enough on some devices.
- Fixed: event links on the Club Events screen were showing the browser's default blue/purple link colours instead of the app's own colours, especially jarring in dark mode. They now match the rest of the app, with no underline.

## 2.14.2 – 30 Sep 2026
- Fixed the real cause of the Close button sitting under the status bar/notch on iPhone: the page was missing `viewport-fit=cover`, so iOS never reported real safe-area values to any dialog — every fallback padding was silently being applied as if there were no notch at all, even on installed standalone app. Also extended the same fix to the day-details sheet, which never had this handling.
- The three buttons under the title (Race Courses, Race Marks Map, Club Events) now fit on one line on every current phone, rather than wrapping to two.

## 2.14.1 – 29 Sep 2026
- Club Events now updates itself with no PR to approve: the workflow pushes straight to `main` once GitHub Actions is added to the ruleset's bypass list (see README). Added a safeguard so a broken or empty feed leaves `events.json` alone instead of wiping the list.

## 2.14.0 – 29 Sep 2026
- New **Club Events** screen, alongside Race Courses and Race Marks Map — Open Days, RYA courses, talks, socials and other club events that aren't part of the racing programme. Built from the club's public events feed, refreshed once a day by a scheduled GitHub Action (see README, "Club Events") since the club's site doesn't allow the app to fetch it directly.

## 2.13.1 – 29 Sep 2026
- Fixed: on iPhone, the top of the "Race Courses" and "Race Marks Map" screen sat too close to the status bar / notch, slightly covering the Close button. It now keeps clear of it, the same way GO SAIL already did.

## 2.13.0 – 29 Sep 2026
- The on-screen header now just says "BSC Sailing Calendar" — no year — so nothing in the app needs changing when 2027's data arrives. The browser tab title still shows the year, so it's still easy to tell seasons apart if you have more than one open.
- Added `.github/CODEOWNERS`, so pull requests need a review from the listed owner before they can be merged (see README).

## 2.12.1 – 28 Sep 2026
- The app now lives in the club's GitHub organisation: https://bsc-sailing.github.io/calendar/ (source: https://github.com/bsc-sailing/calendar). README links updated; no change to how the app works. Anyone who saved the old address to their home screen needs to add the new one.

## 2.12.0 – 23 Sep 2026
- GO SAIL: Start and High water are now a single compact "START: 11:30   HW: 13:19" line under the wind, instead of two large boxes — this frees more height for the marks, which now scale slightly larger on long courses.
- Race Courses list: Port is now red and Starboard green (matching GO SAIL and real buoyage), replacing the earlier blue/orange.
- The race marks chart can be tapped to open full size in its own screen for pinch-zooming.
- The day-detail sheet now has a **GO SAIL** button alongside Add to calendar. It asks you to pick a course from Race Courses, then opens GO SAIL showing that day's Start and High water (with the date shown if it isn't today).
- Fixed: an empty gold banner briefly showed at the top of Race Courses even outside the course-picking flow.

## 2.11.0 – 23 Sep 2026
- Replaced the race marks chart with the club's large-print version (clearer buoy icons and labels); the chart is now this printed image only — the live Google My Map and the toggle between them are removed.

## 2.10.0 – 20 Sep 2026
- GO SAIL: the P/S circle now sits on the right of the mark name; Club Line Gate and Finish never show a rounding side, since you sail through them rather than round them (the ordinary Race Courses list carries the same fix).
- The whole course now fits the screen with no scrolling — text size adjusts automatically to the number of marks and the screen's height, checked down to a 16-mark course on a small phone.
- Smaller course-code heading; the wind line is now "Wind: N–NNE · 11 kn", pulling today's live forecast wind speed for the course's start time (or the current hour if racing hasn't started); distance is dropped from this screen to save space.

## 2.9.1 – 20 Sep 2026
- GO SAIL: a day with no club racing now says "No club racing today" instead of a bare dash (BJRC racing, training-only, or weekly-session days still show the tide if there is one); a day with no data at all says "No tide data today" too, rather than leaving either box looking blank.

## 2.9.0 – 20 Sep 2026
- **GO SAIL**: a button on each course card opens a big, high-contrast, always-dark full-screen view for reading at the helm — course code, wind sector, distance, today's start time and high water, and the marks in order with a large P (red) or S (green) circle and abbreviated names (Ballast H, Northey P., CLG). Keeps the screen awake where the browser supports it.

## 2.8.0 – 20 Sep 2026
- Course cards now sort in logical order (A1-A6, AZ1-AZ6, B1-B6, ...) instead of alphabetically by wind sector; the wind-direction dropdown follows the same order.
- **Race Courses** and **Race Marks Map** are now two separate screens with no shared tab bar, each opening straight to its own content with the matching title.
- Removed the "Show days with no club racing" tick box (use the Racing filter instead) and the "Weekly sessions" tick box (Mirror sailing and Beach Club now always show, like everything else).
- The "Next on" card can be swiped left for the next upcoming event and right to go back, with a small "n of N upcoming" hint when there's more than one.

## 2.7.0 – 20 Sep 2026
- New **Cadets** filter chip (between Training and Events) — shows every day with cadet training, coaching or racing.
- "Weekly sessions" off now hides those Wednesdays completely, even with "Show days with no club racing" ticked; days with a real event (including on bank holidays) are unaffected.
- "Chart & course cards" is now two buttons on the home screen — **Race Courses** and **Race Marks Map** — each opening straight to that tab.
- The club roundel at the top now links to https://blackwatersailingclub.org.uk/.

## 2.6.0 – 20 Sep 2026
- Added **Chart & course cards**, from the header button.
  - **Chart:** the club's live "BSC Race Marks" Google My Map when online (an embedded iframe), or the printed chart (`chart-2026.jpg`, March 2026) when offline or on request, with a toggle between the two. A plain list of mark names underneath.
  - **Course cards:** all 96 printed courses (`courses-2026.csv`), filterable by wind direction sector and searchable by course code or mark name. Each shows its distance and its marks in order, with port/starboard rounding (and "round fully" where the card says so).

## 2.5.1 – 20 Sep 2026
- Days with no BSC fleet racing now say "No club racing" (day summary, Next on card, day detail and the tick box), because BJRC may still be racing that day.

## 2.5.0 – 20 Sep 2026
- BJRC events count as racing (not BSC club racing): they show as "BJRC: race" on the day, the Racing filter includes them, and a BJRC-only day says "No club racing".
- Day summaries and day details list racing as "fleet: series" with no start-order numbers. The day detail heading is "Racing by Fleet".
- Day detail: removed "In x days", moved the title next to Close, listed open meetings before cruiser weekends and non-club events (such as BJRC), and put the high water time and height as large numbers at the top of the Tide section.
- "Weather Forecast" now shows just the forecast and a link to the source, and says "No forecast available" for dates too far ahead.
- "Add N days to calendar" moved to the bottom of the results.
- "Next on" moves to the next event once a day's first start was more than 8 hours ago.

## 2.4.0 – 20 Sep 2026
- Renamed to **BSC Sailing Calendar** (home-screen name **BSC Calendar**).
- **Add to calendar**: save one day, or every day currently shown (respecting My fleets, month, chips and search), as an `.ics` file. Entries carry a stable ID so importing again updates them.

## 2.3.0 – 20 Sep 2026
- New app icon and header logo: the Blackwater Sailing Club roundel (`icon-*.png`, `apple-touch-icon.png` and `logo.png`).

## 2.2.0 – 20 Sep 2026
- Pick more than one fleet under **My fleets**, with a **Reset** button. Old single-fleet choices carry over.
- Version and **Support info** at the bottom of the app.
- The service worker's saved copy is named after the version, so each release replaces the old one.

## 2.1.0 – 20 Sep 2026
- One data file per season (`programme-2026.csv`, `programme-2027.csv`, ...), with season buttons and an automatic switch to the next season once one has finished.
- `?check` on the address lists problems in the data.
- Tide columns can be left blank.

## 2.0.0 – 20 Sep 2026
- Rebuilt around the normalised data in `programme.csv`: races in start order by fleet, events, training, Start TBC, Grand Prix weekends and estimated tides marked with ≈.
- My fleet filter, weekly sessions tick box and search suggestions built from the data.

## 1.x – Sep 2026
- 1.0: first version, list of days with start times, races and high water, installable on a phone.
- 1.1: tap a day for details, search suggestions and quick filters.
- 1.2: weather forecast (temperature, wind, gusts and direction).
- 1.3: first app icons (club burgee, then a drawn shield).
