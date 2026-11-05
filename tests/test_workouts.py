import pytest
from fastapi.testclient import TestClient

from workout_scheduler import main
from workout_scheduler.repository import WorkoutRepository

VALID_WORKOUT = {
    "sport": "Pilates",
    "date": "2026-11-05",
    "start_time": "18:30",
    "duration_minutes": 45,
    "intensity": "medium",
    "notes": "Reformer class",
}


@pytest.fixture
def client():
    main.repo = WorkoutRepository()
    return TestClient(main.app)
def test_create_workout(client):
    response = client.post("/workouts", json=VALID_WORKOUT)
    assert response.status_code == 201
    assert response.json()["id"] == 1
    assert response.json()["sport"] == "Pilates"


def test_list_workouts(client):
    client.post("/workouts", json=VALID_WORKOUT)
    response = client.get("/workouts")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_workout(client):
    client.post("/workouts", json=VALID_WORKOUT)
    response = client.get("/workouts/1")
    assert response.status_code == 200
    assert response.json()["notes"] == "Reformer class"


def test_get_missing_workout_returns_404(client):
    response = client.get("/workouts/99")
    assert response.status_code == 404


def test_duration_too_long_returns_422(client):
    bad = {**VALID_WORKOUT, "duration_minutes": 500}
    response = client.post("/workouts", json=bad)
    assert response.status_code == 422


def test_invalid_intensity_returns_422(client):
    bad = {**VALID_WORKOUT, "intensity": "super-hard"}
    response = client.post("/workouts", json=bad)
    assert response.status_code == 422


def test_update_workout(client):
    client.post("/workouts", json=VALID_WORKOUT)
    changed = {**VALID_WORKOUT, "date": "2026-11-06"}
    response = client.put("/workouts/1", json=changed)
    assert response.status_code == 200
    assert response.json()["date"] == "2026-11-06"


def test_delete_workout(client):
    client.post("/workouts", json=VALID_WORKOUT)
    response = client.delete("/workouts/1")
    assert response.status_code == 204
    assert client.get("/workouts/1").status_code == 404