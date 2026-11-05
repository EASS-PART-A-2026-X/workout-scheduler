# Workout Scheduler

A small REST API for scheduling workouts (for example, Pilates classes).
Built with **FastAPI** and **Pydantic** for EX1. Data is stored in memory, so it resets when the server restarts.

## Features
- Create, list, view, update and delete workouts (CRUD)
- Data validation:
  - `sport` must be 1–50 characters
  - `duration_minutes` must be between 1 and 300
  - `intensity` must be `low`, `medium` or `high`
  - `notes` is optional (max 200 characters)

## Endpoints

| Method | Path | Description | Success code |
|---|---|---|---|
| GET | `/workouts` | List all workouts | 200 |
| GET | `/workouts/{id}` | Get one workout | 200 (404 if not found) |
| POST | `/workouts` | Create a workout | 201 (422 if invalid) |
| PUT | `/workouts/{id}` | Update a workout | 200 (404 if not found) |
| DELETE | `/workouts/{id}` | Delete a workout | 204 (404 if not found) |

### Example workout
```json
{
  "sport": "Pilates",
  "date": "2026-11-05",
  "start_time": "18:30",
  "duration_minutes": 45,
  "intensity": "medium",
  "notes": "Reformer class"
}
```

## Requirements
- Python 3.12
- [uv](https://docs.astral.sh/uv/)

## Install
```bash
git clone https://github.com/adit265/workout-scheduler.git
cd workout-scheduler
uv sync
```

## Run
```bash
uv run fastapi dev src/workout_scheduler/main.py
```
Then open http://127.0.0.1:8000/docs to try the API in your browser.

## Test
```bash
uv run pytest -v
```

## Project structure
```
src/workout_scheduler/
├── models.py       # Pydantic models (what a workout looks like + validation)
├── repository.py   # In-memory storage (CRUD on a dictionary)
└── main.py         # FastAPI app and endpoints
tests/
└── test_workouts.py  # API tests with pytest
```

## AI Assistance
I used Claude (Anthropic) as a tutor during this exercise:
- It helped me set up my environment (WSL, uv, Python 3.12, Git).
- It explained FastAPI, Pydantic and pytest concepts step by step.
- It suggested code for the models, repository, endpoints and tests. I typed the code myself, ran it, and checked every result in the browser and with pytest.
- It helped me debug a naming conflict between `main.py` and the example `main()` function created by `uv init`.