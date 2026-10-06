"""
Real-world weekly schedule for the Timekeeper's weekly events.

Kept free of discord imports so it can be unit tested.
"""
from datetime import datetime, time, timedelta, timezone
from typing import List

try:
    from zoneinfo import ZoneInfo
except ImportError:  # Python 3.8
    from backports.zoneinfo import ZoneInfo


def parse_notification_time(value: str) -> time:
    """Parse an 'HH:MM' string into a time."""
    hours, minutes = str(value).strip().split(':')
    return time(int(hours), int(minutes))


def to_aware(dt: datetime, tz: ZoneInfo) -> datetime:
    """Convert a datetime to tz. Naive datetimes are treated as server local time."""
    if dt.tzinfo is None:
        dt = dt.astimezone()  # attach the server's local timezone
    return dt.astimezone(tz)


def weekly_events_between(
    start: datetime,
    end: datetime,
    day: int,
    at: time,
    tz_name: str = 'Europe/London',
) -> List[datetime]:
    """Return every scheduled weekly event time in the interval (start, end].

    Args:
        start: Previous check time (naive = server local time, or aware)
        end: Current check time (naive = server local time, or aware)
        day: Day of week, 0 = Sunday ... 6 = Saturday
        at: Wall-clock time of day in tz_name
        tz_name: IANA timezone, e.g. 'Europe/London' (handles GMT/BST)
    """
    tz = ZoneInfo(tz_name)
    start_local = to_aware(start, tz)
    end_local = to_aware(end, tz)
    if end_local <= start_local:
        return []

    # Python weekday(): Monday = 0 ... Sunday = 6; config uses Sunday = 0
    target_weekday = (day - 1) % 7
    days_ahead = (target_weekday - start_local.weekday()) % 7
    candidate_date = start_local.date() + timedelta(days=days_ahead)

    events = []
    while True:
        candidate = datetime.combine(candidate_date, at, tzinfo=tz)
        if candidate > end_local:
            break
        if candidate > start_local:
            events.append(candidate)
        candidate_date += timedelta(days=7)
    return events


def game_time_at(event: datetime, now: datetime, game_now: datetime, time_ratio: float) -> datetime:
    """In-game time at a past real-world event, given the in-game time at `now`.

    Used so caught-up weekly events each report their own week's date.
    """
    now_aware = now.astimezone() if now.tzinfo is None else now
    lag_seconds = (now_aware.astimezone(timezone.utc) - event.astimezone(timezone.utc)).total_seconds()
    return game_now - timedelta(seconds=max(0.0, lag_seconds) * time_ratio)
