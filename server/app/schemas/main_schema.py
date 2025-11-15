from pydantic import BaseModel


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
    code: list[str]
    dialogue: str
    bg_music: str
    transition: Transition


class VideoScript(BaseModel):
    """
    Represents the full video script, which is composed
    of a list of segments.
    """

    segments: list[Segment]


class PromptInput(BaseModel):
    topic: str


class UpdateClipInput(BaseModel):
    prompt: str | None = None
    narration_text: str | None = None
    code: str | None = None


class GenerateTitleDesciption(BaseModel):
    title: str
    description: str
