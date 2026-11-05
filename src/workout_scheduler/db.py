import os
from pathlib import Path

from sqlmodel import SQLModel, create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def init_db() -> None:
    Path("data").mkdir(exist_ok=True)
    SQLModel.metadata.create_all(engine)
