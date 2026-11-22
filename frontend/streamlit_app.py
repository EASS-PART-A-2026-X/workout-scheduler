import datetime as dt
import string

import streamlit as st

import api

st.set_page_config(page_title="Workout Scheduler")
st.title("Workout Scheduler")

INTENSITIES = ["low", "medium", "high"]

# Every ASCII punctuation mark, prefixed with a backslash.
MARKDOWN_ESCAPES = str.maketrans({c: "\\" + c for c in string.punctuation})


def plain(text: str) -> str:
    """Escape Markdown so user text is shown, not interpreted."""
    return text.translate(MARKDOWN_ESCAPES)


def notify(message: str) -> None:
    """Remember a success message, then rerun so lists show fresh data."""
    st.session_state["notice"] = message
    st.rerun()


def workout_fields(key: str, workout: api.Workout | None = None) -> dict:
    """Draw the workout inputs (inside a form) and return them as a request body."""
    w: dict = dict(workout) if workout else {}
    sport = st.text_input(
        "Sport",
        w.get("sport", ""),
        max_chars=50,
        placeholder="e.g. Pilates",
        required=True,  # checked in the browser; easy to bypass
        key=f"{key}-sport",
    )
    day = st.date_input(
        "Date",
        dt.date.fromisoformat(w["date"]) if "date" in w else dt.date.today(),
        key=f"{key}-date",
    )
    start = st.time_input(
        "Start time",
        dt.time.fromisoformat(w["start_time"]) if "start_time" in w else dt.time(18, 0),
        key=f"{key}-start",
    )
    duration = st.number_input(
        "Duration (minutes)",
        1,
        300,
        w.get("duration_minutes", 45),
        key=f"{key}-duration",
    )
    intensity = st.selectbox(
        "Intensity",
        INTENSITIES,
        INTENSITIES.index(w.get("intensity", "medium")),
        key=f"{key}-intensity",
    )
    notes = st.text_input(
        "Notes (optional)", w.get("notes") or "", max_chars=200, key=f"{key}-notes"
    )
    return {
        "sport": sport,
        "date": day.isoformat(),
        "start_time": start.strftime("%H:%M"),
        "duration_minutes": duration,
        "intensity": intensity,
        "notes": notes or None,
    }


if notice := st.session_state.pop("notice", None):
    st.success(notice)

try:
    with st.spinner("Loading workouts..."):
        workouts = api.list_workouts()
except api.BackendError as exc:
    st.error(str(exc))
    st.stop()  # nothing else on this page works without the backend

browse, add = st.tabs(["Workouts", "Add a workout"])

with browse:
    if not workouts:
        st.info("No workouts yet. Add one in the 'Add a workout' tab.")
    for workout in sorted(workouts, key=lambda w: (w["date"], w["start_time"])):
        wid = workout["id"]
        sport = plain(workout["sport"])  # user text: show it, never interpret it
        label = (
            f"{sport}: {workout['date']} at {workout['start_time'][:5]} "
            f"({workout['duration_minutes']} min, {workout['intensity']})"
        )
        with st.expander(label), st.form(f"edit-{wid}"):
            changes = workout_fields(f"edit-{wid}", workout)
            save_col, delete_col = st.columns(2)
            save = save_col.form_submit_button(
                "Save changes", key=f"save-{wid}", width="stretch"
            )
            delete = delete_col.form_submit_button(
                "Delete", key=f"delete-{wid}", width="stretch"
            )
            try:
                if save and not changes["sport"].strip():
                    st.warning("Give the workout a sport before saving.")
                elif save:
                    api.update_workout(wid, changes)
                    notify(f"Saved {plain(changes['sport'])} workout.")
                if delete:
                    api.delete_workout(wid)
                    notify(f"Deleted {sport} workout.")
            except api.BackendError as exc:
                st.error(str(exc))

with add, st.form("add"):
    new_workout = workout_fields("add")
    submitted = st.form_submit_button("Add workout", key="add-submit", width="stretch")
    # frontend check before any request
    if submitted and not new_workout["sport"].strip():
        st.warning("Give the workout a sport before saving.")
    elif submitted:
        try:
            created = api.create_workout(new_workout)
        except api.BackendError as exc:
            st.error(str(exc))
        else:
            notify(f"Added {plain(created['sport'])} workout.")
