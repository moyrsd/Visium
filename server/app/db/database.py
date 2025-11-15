import datetime
import os

from dotenv import load_dotenv
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./visium.db")

engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


class Video(SQLModel, table=True):
    id: str = Field(primary_key=True)
    title: str | None = None
    description: str | None = None
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    final_video_path: str | None = None
    thumbnail_path: str | None = None
    clips: list["Clip"] = Relationship(back_populates="video")


class Clip(SQLModel, table=True):
    id: str = Field(primary_key=True)
    video_id: str = Field(foreign_key="video.id")
    index: int
    clip_path: str
    thumbnail_path: str | None = None
    narration_text: str | None = None
    code: str | None = None
    prompt: str | None = None
    duration: float | None = None
    visuals: str | None = None
    video: Video | None = Relationship(back_populates="clips")


class Job(SQLModel, table=True):
    id: str = Field(primary_key=True)
    status: str
    result: str | None = None
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at: datetime.date = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    video_id: str | None = Field(foreign_key="video.id")
