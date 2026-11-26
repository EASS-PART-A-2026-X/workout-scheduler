"""Every HTTP call to the backend lives here. The UI never sees httpx."""

import os
from typing import Any, TypedDict

import httpx

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
TIMEOUT = httpx.Timeout(10.0, connect=2.0)
NOT_SENT = (httpx.ConnectError, httpx.ConnectTimeout, httpx.UnsupportedProtocol)


class Workout(TypedDict):
    """One workout as the backend returns it (WorkoutPublic)."""

    id: int
    sport: str
    date: str
    start_time: str
    duration_minutes: int
    intensity: str
    notes: str | None


class BackendError(Exception):
    """Something went wrong; str(error) is a message you can show to a user."""


class BackendUnavailable(BackendError):
    """Nothing reached the backend (refused, DNS, connect timeout): safe to retry."""


class BackendNoAnswer(BackendError):
    """The request was sent but no full reply came back in time: outcome unknown."""


def _friendly(response: httpx.Response) -> str:
    match response.status_code:
        case 422:
            problems = [
                f"{err['loc'][-1]}: {err['msg']}" for err in response.json()["detail"]
            ]
            return "Please fix: " + "; ".join(problems)
        case 404:
            return "That workout no longer exists. Reload the page."
        case code:
            return f"The backend failed ({code}). Check its logs."


def _request(method: str, path: str, **kwargs) -> httpx.Response:
    kwargs.setdefault("timeout", TIMEOUT)
    try:
        response = httpx.request(method, f"{BACKEND_URL}{path}", **kwargs)
    except NOT_SENT as exc:
        raise BackendUnavailable(
            f"Cannot reach the backend at {BACKEND_URL}. "
            "Start it (uv run fastapi dev src/workout_scheduler/main.py "
            "in backend/) and reload the page."
        ) from exc
    except httpx.TransportError as exc:
        if method == "GET":
            raise BackendNoAnswer(
                "The backend took too long to answer. Reload the page to try again."
            ) from exc
        raise BackendNoAnswer(
            "The backend did not answer in time. Your change may have been saved. "
            "Reload the page and check before trying again."
        ) from exc
    if response.is_error:
        raise BackendError(_friendly(response))
    return response


def _json(response: httpx.Response) -> Any:
    try:
        return response.json()
    except ValueError as exc:
        raise BackendError(
            f"The service at {BACKEND_URL} did not answer like the Workout "
            "Scheduler API. Check BACKEND_URL."
        ) from exc


def list_workouts() -> list[Workout]:
    return _json(_request("GET", "/workouts"))


def create_workout(workout: dict) -> Workout:
    return _json(_request("POST", "/workouts", json=workout))


def update_workout(workout_id: int, workout: dict) -> Workout:
    return _json(_request("PUT", f"/workouts/{workout_id}", json=workout))


def delete_workout(workout_id: int) -> None:
    _request("DELETE", f"/workouts/{workout_id}")
