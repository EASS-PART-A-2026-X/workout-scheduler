import datetime as dt
from enum import Enum

from pydantic import BaseModel, Field


class Intensity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class WorkoutCreate(BaseModel):
    sport: str = Field(min_length=1, max_length=50)
    date: dt.date
    start_time: dt.time
    duration_minutes: int = Field(ge=1, le=300)
    intensity: Intensity = Intensity.medium
    notes: str | None = Field(default=None, max_length=200)


class Workout(WorkoutCreate):
    id: int