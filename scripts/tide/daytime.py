"""
daytime.py: which of a day's (usually two) high waters to show.

Most days have one high water near the middle of the day and one in the night,
so the choice is obvious. But every couple of weeks the two fall roughly 6 am
and 6 pm, and the "nearest midday" choice can flip from one day to the next
(18:02 one day, 06:08 the next). The rule here:

  * pick the high water nearest the middle of the day, meaning solar noon
    (12:00 GMT: 13:00 on the clock in summer, 12:00 in winter);
  * if the other one is almost as near (within AMBIGUOUS_MINUTES of the same
    distance), return it too, as the alternative, so the app can show both
    rather than quietly picking one.

Stdlib only, so the fetch script can use it without numpy.
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

LOCAL_TZ = ZoneInfo("Europe/London")
AMBIGUOUS_MINUTES = 60


def to_min(hhmm):
    return int(hhmm[:2]) * 60 + int(hhmm[3:5])


def solar_noon_minutes(date_str):
    """12:00 GMT on that date, as minutes past midnight UK clock time."""
    d = datetime.strptime(date_str + " 12:00", "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc).astimezone(LOCAL_TZ)
    return d.hour * 60 + d.minute


def choose(date_str, highs):
    """highs: list of (HH:MM, height). Returns (chosen, alternative or None)."""
    highs = [h for h in highs if h and h[0]]
    if not highs:
        return None, None
    noon = solar_noon_minutes(date_str)
    ranked = sorted(highs, key=lambda h: abs(to_min(h[0]) - noon))
    best = ranked[0]
    alt = None
    if len(ranked) > 1 and abs(to_min(ranked[1][0]) - noon) - abs(to_min(best[0]) - noon) <= AMBIGUOUS_MINUTES:
        alt = ranked[1]
    return best, alt
