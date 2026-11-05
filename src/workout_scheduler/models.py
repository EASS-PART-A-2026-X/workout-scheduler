import datetime as dt
from enum import Enum

from sqlmodel import Field, SQLModel


class Intensity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class WorkoutBase(SQLModel):
    sport: str = Field(min_length=1, max_length=50)
    date: dt.date
    start_time: dt.time
    duration_minutes: int = Field(ge=1, le=300)
    intensity: Intensity = Intensity.medium
    notes: str | None = Field(default=None, max_length=200)


class Workout(WorkoutBase, table=True):
    id: int | None = Field(default=None, primary_key=True)


class WorkoutCreate(WorkoutBase):
    pass


class WorkoutPublic(WorkoutBase):
    id: int
