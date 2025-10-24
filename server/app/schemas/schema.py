from pydantic import BaseModel
from typing import List


class Transition(BaseModel):
    """
    Defines the transition effects for a scene.
    """
    on: str
    off: str

class Segment(BaseModel):
    """
    Represents a single scene in the video, including
    its name, code, dialogue, and transitions.
    """
    name: str
    code: List[str]
    dialogue: str
    bg_music: str
    transition: Transition

class VideoScript(BaseModel):
    """
    Represents the full video script, which is composed
    of a list of segments.
    """
    segments: List[Segment]
