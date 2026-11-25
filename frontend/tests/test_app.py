"""AppTest runs streamlit_app.py in-process; respx fakes every backend call."""

import datetime as dt
import json

import httpx
import pytest
import respx
from streamlit.testing.v1 import AppTest

from api import BACKEND_URL as BASE  # the URL api.py really calls

APP = "../streamlit_app.py"  # resolved relative to THIS test file

PILATES = {
    "id": 1,
    "sport": "Pilates",
    "date": "2026-11-25",
    "start_time": "18:30:00",
    "duration_minutes": 45,
    "intensity": "medium",
    "notes": "Reformer class",
}


@pytest.fixture
def backend():
    with respx.mock(base_url=BASE, assert_all_called=False) as mock:
        yield mock


def start_app(backend, workouts: list[dict]) -> AppTest:
    backend.get("/workouts").mock(return_value=httpx.Response(200, json=workouts))
    # 30 s instead of the 3 s default: a cold first run can be slow.
    return AppTest.from_file(APP, default_timeout=30).run()


def test_empty_state(backend):
    at = start_app(backend, [])
    assert "No workouts yet" in at.info[0].value


def test_list_shows_each_workout(backend):
    at = start_app(backend, [PILATES])
    assert "Pilates: 2026-11-25 at 18:30" in at.expander[0].label


def test_backend_down_shows_next_step_not_traceback(backend):
    backend.get("/workouts").mock(side_effect=httpx.ConnectError("refused"))
    at = AppTest.from_file(APP, default_timeout=30).run()
    assert not at.exception
    assert "Cannot reach the backend" in at.error[0].value
    assert "reload the page" in at.error[0].value
    assert len(at.tabs) == 0  # st.stop(): the rest of the page is not drawn


def test_empty_sport_is_stopped_before_any_request(backend):
    post = backend.post("/workouts").mock(return_value=httpx.Response(201))
    at = start_app(backend, [])
    at.text_input(key="add-sport").input("   ")
    at.button(key="add-submit").click().run()
    assert "Give the workout a sport" in at.warning[0].value
    assert not post.called


def test_validation_errors_are_shown_in_words(backend):
    msg = "Input should be less than or equal to 300"
    detail = [{"loc": ["body", "duration_minutes"], "msg": msg}]
    backend.post("/workouts").mock(
        return_value=httpx.Response(422, json={"detail": detail})
    )
    at = start_app(backend, [])
    at.text_input(key="add-sport").input("Pilates")
    at.button(key="add-submit").click().run()
    assert not at.exception
    assert at.error[0].value == f"Please fix: duration_minutes: {msg}"


def test_lost_reply_after_a_write_says_outcome_unknown(backend):
    backend.post("/workouts").mock(side_effect=httpx.ReadTimeout("no reply"))
    at = start_app(backend, [])
    at.text_input(key="add-sport").input("Pilates")
    at.button(key="add-submit").click().run()
    assert not at.exception
    assert "may have been saved" in at.error[0].value


def test_add_sends_exact_json(backend):
    post = backend.post("/workouts").mock(
        return_value=httpx.Response(201, json=PILATES)
    )
    at = start_app(backend, [])
    at.text_input(key="add-sport").input("Pilates")
    at.date_input(key="add-date").set_value(dt.date(2026, 11, 25))
    at.time_input(key="add-start").set_value(dt.time(18, 30))
    at.button(key="add-submit").click().run()
    assert json.loads(post.calls.last.request.content) == {
        "sport": "Pilates",
        "date": "2026-11-25",
        "start_time": "18:30",
        "duration_minutes": 45,
        "intensity": "medium",
        "notes": None,
    }
    assert at.success[0].value == "Added Pilates workout."


def test_missing_workout_on_save_says_reload(backend):
    backend.put("/workouts/1").mock(
        return_value=httpx.Response(404, json={"detail": "Workout not found"})
    )
    at = start_app(backend, [PILATES])
    at.button(key="save-1").click().run()
    assert "no longer exists" in at.error[0].value


def test_list_shows_intensity_icon(backend):
    at = start_app(backend, [PILATES])
    assert at.expander[0].label.startswith("🟡")  # medium intensity


def test_summary_cards(backend):
    at = start_app(backend, [PILATES])
    cards = {metric.label: metric.value for metric in at.metric}
    assert cards["Total workouts"] == "1"
    assert "Minutes this week" in cards
    assert "Next workout" in cards


def test_summary_cards_without_workouts(backend):
    at = start_app(backend, [])
    cards = {metric.label: metric.value for metric in at.metric}
    assert cards == {
        "Total workouts": "0",
        "Minutes this week": "0",
        "Next workout": "None yet",
    }
