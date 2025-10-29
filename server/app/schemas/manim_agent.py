from pydantic import Field
from typing_extensions import TypedDict, Annotated, Literal
import operator


class CodingAgentState(TypedDict):
    direction: str
    code: str
    slide_index: int
    session_key: str
    rewrite: Literal["required", "not required"] = Field(
        "not required",
        json_schema_extra="Check if rewrite of the code is required or not",
    )
    feedback: str = Field(
        None,
        json_schema_extra="If code rewrite is required what changes to make suggest so that the geometry is exactly like described",
    )
    codes: Annotated[list, operator.add]
