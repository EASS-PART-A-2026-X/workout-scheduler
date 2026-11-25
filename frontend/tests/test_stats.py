"""The summary numbers, tested without Streamlit or a backend."""

import datetime as dt

from stats import minutes_this_week, next_workout


def workout(day: str, time: str, minutes: int = 45) -> dict:
    return {"date": day, "start_time": time, "duration_minutes": minutes}


# Wednesday 25 November 2026: that week runs from Monday 23 to Sunday 29.
WEDNESDAY = dt.date(2026, 11, 25)


def test_minutes_this_week_counts_monday_to_sunday_only():
    workouts = [
        workout("2026-11-22", "10:00", 30),  # Sunday before: not counted
        workout("2026-11-23", "10:00", 45),  # Monday: counted
        workout("2026-11-29", "10:00", 60),  # Sunday: counted
        workout("2026-11-30", "10:00", 90),  # next Monday: not counted
    ]
    assert minutes_this_week(workouts, WEDNESDAY) == 105


def test_minutes_this_week_is_zero_without_workouts():
    assert minutes_this_week([], WEDNESDAY) == 0


def test_next_workout_skips_ones_that_already_started():
    now = dt.datetime(2026, 11, 25, 12, 0)
    earlier_today = workout("2026-11-25", "09:00")
    later_today = workout("2026-11-25", "18:30")
    tomorrow = workout("2026-11-26", "08:00")
    found = next_workout([tomorrow, earlier_today, later_today], now)
    assert found is later_today


def test_next_workout_is_none_when_all_are_past():
    now = dt.datetime(2026, 11, 25, 12, 0)
    assert next_workout([workout("2026-11-01", "09:00")], now) is None
