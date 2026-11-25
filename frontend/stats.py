"""Summary numbers for the page. Pure functions: no I/O, easy to test."""

import datetime as dt
from collections.abc import Iterable, Mapping


def starts_at(workout: Mapping) -> dt.datetime:
    """The workout's date and start time as one datetime."""
    return dt.datetime.combine(
        dt.date.fromisoformat(workout["date"]),
        dt.time.fromisoformat(workout["start_time"]),
    )


def minutes_this_week(workouts: Iterable[Mapping], today: dt.date) -> int:
    """Total planned minutes from Monday to Sunday of today's week."""
    monday = today - dt.timedelta(days=today.weekday())
    sunday = monday + dt.timedelta(days=6)
    return sum(
        w["duration_minutes"]
        for w in workouts
        if monday <= dt.date.fromisoformat(w["date"]) <= sunday
    )


def next_workout(workouts: Iterable[Mapping], now: dt.datetime) -> Mapping | None:
    """The earliest workout that has not started yet, or None."""
    upcoming = [w for w in workouts if starts_at(w) >= now]
    return min(upcoming, key=starts_at, default=None)
