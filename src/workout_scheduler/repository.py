from sqlmodel import Session, select

from .models import Workout, WorkoutCreate


class WorkoutRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[Workout]:
        return list(self.session.exec(select(Workout)).all())

    def get(self, workout_id: int) -> Workout | None:
        return self.session.get(Workout, workout_id)

    def create(self, data: WorkoutCreate) -> Workout:
        workout = Workout.model_validate(data)
        self.session.add(workout)
        self.session.commit()
        self.session.refresh(workout)
        return workout

    def update(self, workout_id: int, data: WorkoutCreate) -> Workout | None:
        workout = self.get(workout_id)
        if workout is None:
            return None
        workout.sqlmodel_update(data.model_dump())
        self.session.add(workout)
        self.session.commit()
        self.session.refresh(workout)
        return workout

    def delete(self, workout_id: int) -> bool:
        workout = self.get(workout_id)
        if workout is None:
            return False
        self.session.delete(workout)
        self.session.commit()
        return True
