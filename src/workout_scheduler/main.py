from fastapi import FastAPI, HTTPException

from .models import Workout, WorkoutCreate
from .repository import WorkoutRepository

app = FastAPI(title="Workout Scheduler")
repo = WorkoutRepository()


@app.get("/workouts")
def list_workouts() -> list[Workout]:
    return repo.list_all()


@app.get("/workouts/{workout_id}")
def get_workout(workout_id: int) -> Workout:
    workout = repo.get(workout_id)
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout


@app.post("/workouts", status_code=201)
def create_workout(data: WorkoutCreate) -> Workout:
    return repo.create(data)


@app.put("/workouts/{workout_id}")
def update_workout(workout_id: int, data: WorkoutCreate) -> Workout:
    workout = repo.update(workout_id, data)
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout


@app.delete("/workouts/{workout_id}", status_code=204)
def delete_workout(workout_id: int) -> None:
    if not repo.delete(workout_id):
        raise HTTPException(status_code=404, detail="Workout not found")