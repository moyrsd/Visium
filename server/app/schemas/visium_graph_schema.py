import operator
from typing import Annotated

from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class Script(BaseModel):
    dialouge: str = Field(
        None,
        json_schema_extra="What will the narrator say at this part of the video, only say the dialouge no other comments",
    )
    slide_visuals: str = Field(
        None,
        json_schema_extra="What will the slide look like, only tell if something would be written or some diagram has to be formed no other comments",
    )
    duration: float = Field(None, json_schema_extra="The duration for which this dialogue will be narrated.")


class ScriptState(BaseModel):
    script: list[Script] = Field([], json_schema_extra="Step by step explainination of the given topic")


class Director(BaseModel):
    directions: list[str] = Field([], json_schema_extra="Visual directions for the video in natural language")


class State(TypedDict):
    topic: Annotated[str, None]
    script: list[Script]
    directions: list[str]
    audio_paths: list[str]
    video_paths: Annotated[list, operator.add]
    codes: Annotated[list, operator.add]
    job_id: str
    video_id: str
    clips: Annotated[list, operator.add]
