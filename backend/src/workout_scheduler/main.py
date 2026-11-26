from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session

from .db import engine, init_db
from .models import WorkoutCreate, WorkoutPublic
from .repository import WorkoutRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Workout Scheduler", lifespan=lifespan)


def get_repo():
    with Session(engine) as session:
        yield WorkoutRepository(session)


RepoDep = Annotated[WorkoutRepository, Depends(get_repo)]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/workouts")
def list_workouts(repo: RepoDep) -> list[WorkoutPublic]:
    return repo.list_all()


@app.get("/workouts/{workout_id}")
def get_workout(workout_id: int, repo: RepoDep) -> WorkoutPublic:
    workout = repo.get(workout_id)
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout


@app.post("/workouts", status_code=201)
def create_workout(data: WorkoutCreate, repo: RepoDep) -> WorkoutPublic:
    return repo.create(data)


@app.put("/workouts/{workout_id}")
def update_workout(
    workout_id: int, data: WorkoutCreate, repo: RepoDep
) -> WorkoutPublic:
    workout = repo.update(workout_id, data)
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout


@app.delete("/workouts/{workout_id}", status_code=204)
def delete_workout(workout_id: int, repo: RepoDep) -> None:
    if not repo.delete(workout_id):
        raise HTTPException(status_code=404, detail="Workout not found")
