# Workout Scheduler

A REST API for scheduling workouts (for example, Pilates classes).
Built with **FastAPI**, **Pydantic** and **SQLModel**. Workouts are stored in a **SQLite** database, so they survive a restart.

## Features
- Create, list, view, update and delete workouts (CRUD)
- Data validation:
  - `sport` must be 1–50 characters
  - `duration_minutes` must be between 1 and 300
  - `intensity` must be `low`, `medium` or `high`
  - `notes` is optional (max 200 characters)
- Persistent storage in SQLite (`data/app.db`)

## Endpoints

| Method | Path | Description | Success code |
|---|---|---|---|
| GET | `/workouts` | List all workouts | 200 |
| GET | `/workouts/{id}` | Get one workout | 200 (404 if not found) |
| POST | `/workouts` | Create a workout | 201 (422 if invalid) |
| PUT | `/workouts/{id}` | Update a workout | 200 (404 if not found, 422 if invalid) |
| DELETE | `/workouts/{id}` | Delete a workout | 204 (404 if not found) |
| GET | `/health` | Health check | 200 |

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
- Docker (optional, for running in a container)

## Setup
```bash
git clone https://github.com/EASS-PART-A-2026-X/workout-scheduler.git
cd workout-scheduler
uv sync
```

## Configuration
| Setting | Default | Meaning |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./data/app.db` | Where the database is stored |

See `.env.example`. The `data/` folder is created automatically on startup and is not committed to Git.

## Run locally
```bash
uv run fastapi dev src/workout_scheduler/main.py
```
Open http://127.0.0.1:8000/docs to try the API.

**Restart check:** create a workout, stop the server (Ctrl+C), start it again, and `GET /workouts` still returns it.

## Test
```bash
uv run pytest -v
```
The tests use a separate in-memory database, so they never touch `data/app.db`. `test_workout_survives_restart` checks that data is still there after a restart.

## Run with Docker
```bash
docker build -t workout-scheduler .
docker run -d --name backend -p 8000:8000 -v workout-data:/app/data workout-scheduler
```
Open http://127.0.0.1:8000/health — it should return `{"status": "ok"}`.

The named volume `workout-data` keeps the database when the container is replaced:
```bash
docker rm -f backend
docker run -d --name backend -p 8000:8000 -v workout-data:/app/data workout-scheduler
```
The container runs as a non-root user (`appuser`, uid 10001).

## Try the API with examples.http
`examples.http` contains ready-made requests for every endpoint, including invalid input (422) and a missing workout (404).
Install the **REST Client** extension in VS Code, start the API, open `examples.http`, and click **Send Request** above each request.

## Project structure
```
src/workout_scheduler/
├── models.py       # SQLModel/Pydantic models and validation
├── db.py           # Database connection (DATABASE_URL) and table creation
├── repository.py   # CRUD operations on the database
└── main.py         # FastAPI app and endpoints
tests/
└── test_workouts.py  # API tests with pytest (including a restart test)
Dockerfile          # Container image for the API
.env.example        # Example configuration
examples.http       # Ready-made requests (REST Client)
```

## AI use
- **Tool:** Claude (Anthropic), used as a tutor.
- **Help received:** environment setup (WSL, uv, Python 3.12, Git, Docker), explanations of FastAPI, Pydantic, SQLModel and pytest, suggested code for the models, database, repository, endpoints, tests and Dockerfile, and help debugging a `main` naming conflict and Docker permissions in WSL.
- **Checks I ran:** `uv run pytest -v` (11 passed); every endpoint by hand in `/docs` (201, 200, 204, 404, 422); a workout still exists after restarting the server locally, and after replacing the Docker container with the same volume; `docker exec backend id` shows `appuser`.
