import operator
from typing import Annotated, Literal

from pydantic import Field
from typing_extensions import TypedDict


class CodingAgentState(TypedDict):
    direction: str
    code: str
    slide_index: int
    clip_id: str
    rewrite: Literal["required", "not required"] = Field(
        "not required", json_schema_extra="Check if rewrite of the code is required or not"
    )
    feedback: str = Field(
        None,
        json_schema_extra="If code rewrite is required what changes to make suggest so that the geometry is exactly like described",
    )
    video_paths: Annotated[list, operator.add]
    codes: Annotated[list, operator.add]
    clips: Annotated[list, operator.add]
    duration: float
    visuals: str
    clip_video_id: str
    narration_text: str
