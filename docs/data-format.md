# The season programme file

This is the format the BSC Sailing Calendar app reads a season's programme from. It's written for whoever prepares the programme each year, so it doesn't assume any knowledge of GitHub or the app's code.

Each season is one spreadsheet saved as CSV, named `programme-YEAR.csv` (for example `programme-2027.csv`). Excel, Google Sheets or Numbers are all fine for editing it; save or export it as **CSV (UTF-8)** at the end.

Downloads: [blank template with sample rows](programme-template.csv) · [the full 2026 programme as a worked example](programme-2026.csv)

## The big difference from the race card

The printed race card has **one row per day**, with a column for each fleet. The app's file has **one row per day per fleet** (or per event, or per training session). So a race-card day with five fleets racing, a cruiser weekend, cadet training and an open meeting becomes eight rows, all with the same date and tide.

Here's Sunday 19 April 2026 from the race card:

| Date | HW | Ht | Start | Fast / Fireball | Medium | Wayfarer | Sprite | Short course, Fridays, Mirror | Cruiser | Events etc. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Su 19 Apr | 14:52 | 3.34 | 12:45 | Swann Spoon 1&2 | Fendick Tankard 1&2 | Pippin 1&2 | | April Cup / Mirror Blackwater Cup 1 | Cruiser weekend | Cadet Training / ITCA (Topper) Open |

and the same day in the app's file:

| Date | High water | Tide height (m) | Tide source | Start time | Fleet | Race start order | Event | Training | GP weekend | Race / series | Race no(s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-04-19 | 14:52 | 3.3 | Programme | 12:45 | Fast / Fireball | 1 | | | FALSE | Swann Spoon | 1&2 |
| 2026-04-19 | 14:52 | 3.3 | Programme | 12:45 | Medium | 2 | | | FALSE | Fendick Tankard | 1&2 |
| 2026-04-19 | 14:52 | 3.3 | Programme | 12:45 | Wayfarer | 3 | | | FALSE | Pippin | 1&2 |
| 2026-04-19 | 14:52 | 3.3 | Programme | 12:45 | Short course | 5 | | | FALSE | April Cup | |
| 2026-04-19 | 14:52 | 3.3 | Programme | 12:45 | Mirror | 5 | | | FALSE | Mirror Blackwater Cup | 1 |
| 2026-04-19 | 14:52 | 3.3 | Programme | | Cruiser | | Cruiser weekend | | FALSE | | |
| 2026-04-19 | 14:52 | 3.3 | Programme | TBC | | | | Cadet training | FALSE | | |
| 2026-04-19 | 14:52 | 3.3 | Programme | 12:45 | | | Open meeting | | FALSE | ITCA (Topper) Open | |

Things to notice:

- The race name and the race numbers go in separate columns: "Swann Spoon 1&2" is `Swann Spoon` and `1&2`.
- The combined "Short course, Fridays, Mirror" column becomes separate fleets (`Short course`, `Fridays`, `Mirror`), all with start order 5.
- Days with no club activity at all are simply left out. Days the card marks "NR" get one `No racing` row (see below).
- A few columns aren't shown above: `Detail` (and any extra columns, which are ignored).

## The columns

Keep these headings exactly as written, in the first row. Their order doesn't matter, and any extra columns (such as notes) are ignored.

| Column | What goes in it | Example |
| --- | --- | --- |
| **Date** | The date, as year-month-day. In a spreadsheet, format the column as `yyyy-mm-dd` before saving. | `2027-04-18` |
| **High water** | The daytime high water used for racing, 24-hour clock, UK local time (BST in summer). | `14:52` |
| **Tide height (m)** | Height in metres. | `3.3` |
| **Tide source** | `Programme` for a tide from the printed tables. `Estimated` only for ones worked out by the club's tide model. | `Programme` |
| **Start time** | The first start, 24-hour clock. `TBC` when the coach or instructor sets it. Blank for things with no start time (a cruiser weekend, No racing). | `12:45` |
| **Fleet** | One of the fleet names, spelled exactly the same every time: `Fast / Fireball`, `Medium`, `Wayfarer`, `Sprite`, `Short course`, `Fridays`, `Mirror`, `Cruiser`. Blank for club-wide events and training. A new fleet name just works: it gets its own button in the app. | `Medium` |
| **Race start order** | 1 to 6, the order that fleet starts in (as on the race card's "Order of Race Starts" row). Only on racing rows. | `2` |
| **Event** | A club-wide or special event: `Regatta`, `Evening race`, `Club week`, `Cadet week`, `Open meeting`, `Cruiser weekend`, `No racing`, a BJRC race by name, and so on. | `Cruiser weekend` |
| **Training** | `Cadet training`, `Cadet coaching`, `Adult RYA`, or "*Fleet* training". | `Cadet training` |
| **GP weekend** | `TRUE` on every row of a Grand Prix weekend date, otherwise `FALSE`. | `FALSE` |
| **Race / series** | The trophy or series name, without the race numbers. For an open meeting or BJRC race, its name. | `Fendick Tankard` |
| **Race no(s)** | The race numbers in that series. | `1&2` |
| **Detail** | Anything extra, shown in the day's details: a start location, a coordinator, session times. | `Osea Pier` |

## Rules of thumb

- **Every row for a day repeats the same date, tide and start time.** The only exceptions are training with `TBC`, and events with their own start (a BJRC race at 09:00 on a club-racing day).
- **One row per fleet** for anything fleet-specific, even when it's the same event for every fleet: Club week is one row per fleet, all with `Event` = `Club week`.
- **No racing:** one row with only Date, tide and `Event` = `No racing`.
- **Evening races:** one row per fleet with `Event` = `Evening race`, the evening start time (for example `19:00`), and the race number in `Race no(s)`.
- **Things the race card lists in its footer** (Grand Prix weekends, cadet coaching dates, Adult RYA course dates, cruising dates, Mirror Wednesday sessions) need rows of their own on each of those dates, so they appear on the right days in the app.
- **Leave a tide blank** rather than guess one: the app shows its own estimate, marked `≈`.
- **No formulas or merged cells** in the saved file, and no blank rows in the middle; a CSV keeps only what's displayed in each cell.

## Checking a file

You can check a draft yourself before sending it, on any computer or phone, without anything being uploaded or published:

- **[Preview it in the app](./?preview):** choose your saved CSV, and the app shows that season exactly as it would appear once published, with a data check at the top listing anything that doesn't follow the rules above.
- **[See it as a race card](racecard.html):** open the same file to see it laid out like the printed race card, to compare against your own version. It prints on A4 landscape, or saves as a PDF from the print dialog.

When the file is added to the calendar, it's checked again automatically, and any row that doesn't follow the rules is reported by line number before anything reaches the live app. Adding `?check` to the app's address (`https://bsc-sailing.github.io/calendar/?check`) shows the same check for a published season.

## Starting from a template

There's a ready-made template for Google Sheets and for Excel. Both have the headings, the date and time formats, and drop-down lists for Fleet, Race start order, Tide source and GP weekend already set up, so the CSV comes out in the right shape. Times are stored as text, so they save exactly as typed (`14:52`, `TBC`).

**Google Sheets:** [make your own copy of the template](https://docs.google.com/spreadsheets/d/1_f96_ONFH_KBwGspTjlORB28uWOV743X_6ce3sHiDSQ/copy) (you'll need to be signed in to a Google account). Fill in the **Programme** tab (delete the sample rows), then, with that tab open, **File → Download → Comma-separated values (.csv)**. Only the tab you're on is downloaded. Google names the file after the sheet and tab ("BSC programme template - Programme.csv"); the name doesn't matter for checking it, and whoever publishes it renames it `programme-2027.csv`. You can also share the sheet itself with a maintainer instead of emailing a CSV.

**Excel:** download [the Excel template](programme-template.xlsx). Fill in the **Programme** sheet (delete the sample rows), then **File → Save As → CSV UTF-8**, naming it `programme-2027.csv`. Excel warns that only the current sheet is saved; that's expected. (The Excel file also opens in Google Sheets: upload it to Google Drive and open it, and it works the same as the Google Sheets template.)
