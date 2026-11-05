from .models import Workout, WorkoutCreate


class WorkoutRepository:
    def __init__(self) -> None:
        self._workouts: dict[int, Workout] = {}
        self._next_id = 1

    def list_all(self) -> list[Workout]:
        return list(self._workouts.values())

    def get(self, workout_id: int) -> Workout | None:
        return self._workouts.get(workout_id)

    def create(self, data: WorkoutCreate) -> Workout:
        workout = Workout(id=self._next_id, **data.model_dump())
        self._workouts[workout.id] = workout
        self._next_id += 1
        return workout

    def update(self, workout_id: int, data: WorkoutCreate) -> Workout | None:
        if workout_id not in self._workouts:
            return None
        workout = Workout(id=workout_id, **data.model_dump())
        self._workouts[workout_id] = workout
        return workout

    def delete(self, workout_id: int) -> bool:
        return self._workouts.pop(workout_id, None) is not None