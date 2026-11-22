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

## Frontend (EX2)

A browser page built with **Streamlit** in `frontend/`. It lists, adds, edits and deletes workouts through the backend API.

```
Browser -> Streamlit frontend (port 8501) -> FastAPI backend (port 8000) -> SQLite
```

All HTTP calls live in `frontend/api.py`; the page (`frontend/streamlit_app.py`) never talks to the database directly.

### Run the frontend
Use two terminals.

Terminal 1, the backend (from the repository root):
```bash
uv run fastapi dev src/workout_scheduler/main.py
```

Terminal 2, the frontend:
```bash
cd frontend
uv sync
uv run streamlit run streamlit_app.py
```
Open http://127.0.0.1:8501.

| Setting | Default | Meaning |
|---|---|---|
| `BACKEND_URL` | `http://localhost:8000` | Where the frontend sends its requests |

**WSL tip:** if the Windows browser cannot open the page, start the backend with `--host 0.0.0.0` and the frontend with `--server.address 0.0.0.0`, then open `http://<output of hostname -I>:8501`. Stop both servers when you are done.

### Test the frontend
From `frontend/`:
```bash
uv run pytest -v
```
These tests use Streamlit's `AppTest` with a fake backend (`respx`), so no server is needed. They cover the empty list, a stopped backend, a 422 shown in words, a lost reply after a save, a missing workout, the exact JSON sent on create, and that the page only reaches the backend through `api.py`.

One real-browser flow (add, reload, delete) needs both servers running:
```bash
uv run playwright install --with-deps chromium   # once
uv run pytest e2e --base-url http://127.0.0.1:8501
```

Style checks:
```bash
uv run ruff check . && uv run ruff format --check .
```

### Manual checks
| Situation | What the page shows |
|---|---|
| No workouts yet | "No workouts yet. Add one in the 'Add a workout' tab." |
| Empty sport | "Give the workout a sport before saving." (no request is sent) |
| Duration over 300 (from the API) | "Please fix: duration_minutes: Input should be less than or equal to 300" |
| Backend stopped | "Cannot reach the backend at http://localhost:8000. Start it (uv run fastapi dev src/workout_scheduler/main.py) and reload the page." |
| After restarting the backend | Reloading the page shows the list again |

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
frontend/
├── api.py            # Every HTTP call to the backend
├── streamlit_app.py  # The Streamlit page
├── tests/            # AppTest tests and the import-boundary test
└── e2e/              # One real-browser test (Playwright)
```

## AI use
- **Tool:** Claude (Anthropic), used as a tutor.
- **Help received:** environment setup (WSL, uv, Python 3.12, Git, Docker), explanations of FastAPI, Pydantic, SQLModel and pytest, suggested code for the models, database, repository, endpoints, tests and Dockerfile, and help debugging a `main` naming conflict and Docker permissions in WSL.
- **Checks I ran:** `uv run pytest -v` (11 passed); every endpoint by hand in `/docs` (201, 200, 204, 404, 422); a workout still exists after restarting the server locally, and after replacing the Docker container with the same volume; `docker exec backend id` shows `appuser`.
- **EX2 frontend:** Claude suggested the Streamlit page, `api.py`, the tests and the README sections, following the course's Lecture 4 and 5 patterns. I ran the page in my browser and checked add, edit (persists after reload), delete, and the message shown when the backend is stopped; I ran `uv run pytest` in `frontend/`.

## Open-source evidence

| Student | Repository | License | Stars (checked) | PR | Summary | Merge evidence |
|---|---|---|---|---|---|---|
| adi tavakoli (@adit265) | [tldr-pages/tldr](https://github.com/tldr-pages/tldr) | [LICENSE.md](https://github.com/tldr-pages/tldr/blob/main/LICENSE.md) | 64.2K (16 Nov 2026) | [#25280](https://github.com/tldr-pages/tldr/pull/25280) | Added a Hebrew translation of the `mkdir` page | Pending (open) |
| adi tavakoli (@adit265) | [tldr-pages/tldr](https://github.com/tldr-pages/tldr) | [LICENSE.md](https://github.com/tldr-pages/tldr/blob/main/LICENSE.md) | 64.2K (16 Nov 2026) | [#25281](https://github.com/tldr-pages/tldr/pull/25281) | Added a Hebrew translation of the `rmdir` page | Pending (open) |
| adi tavakoli (@adit265) | [tldr-pages/tldr](https://github.com/tldr-pages/tldr) | [LICENSE.md](https://github.com/tldr-pages/tldr/blob/main/LICENSE.md) | 64.2K (16 Nov 2026) | [#25282](https://github.com/tldr-pages/tldr/pull/25282) | Added a Hebrew translation of the `clear` page | Pending (open) |
