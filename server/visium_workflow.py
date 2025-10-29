from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated, Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.types import Send
from typing import List
import operator
from dotenv import load_dotenv
import os
import uuid
from manim_agent import coding_agent_compiled

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("⚠️ GEMINI_API_KEY not found in environment!")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_retries=3,
    google_api_key=api_key,
)


class Script(BaseModel):
    dialouge: str = Field(
        None,
        json_schema_extra="What will the narrator say at this part of the video, only say the dialouge no other comments",
    )
    slide_visuals: str = Field(
        None,
        json_schema_extra="What will the slide look like, only tell if something would be written or some diagram has to be formed no other comments",
    )


class ScriptState(BaseModel):
    script: List[Script] = Field(
        [], json_schema_extra="Step by step explainination of the given topic"
    )


class Director(BaseModel):
    directions: List[str] = Field(
        [], json_schema_extra="Visual directions for the video in natural language"
    )


class State(TypedDict):
    topic: Annotated[str, None]
    script: List[Script]
    directions: List[str]
    codes: Annotated[list, operator.add]


def script_writer(state: State):
    script_llm = llm.with_structured_output(ScriptState)
    msg = script_llm.invoke(
        f"Write a script on the {state['topic']}, you are preparing slides to explain the topic properly, the slides will be static in nature but will be made with manim library "
    )
    print(msg.script)
    return {"script": msg.script}


def director(state: State):
    director_llm = llm.with_structured_output(Director)
    msg = director_llm.invoke(
        f""" You are preparing slides for the topic {state["topic"]}, here is the already prepared script{state["script"]}, you have elaborate the visuals numerally and textually with utmost precision

        # 3Blue1Brown Visual Grammar
        - Background: always dark (BLACK or #0B0C10)
        - Palette: YELLOW, BLUE_C, GREEN_C, RED_C only.
        - Shapes: use simple Manim primitives (Line, Polygon, Circle, Square, Tex, MathTex, Arrow, Brace).
        - Center important math objects; avoid clutter.
        - Text must be LaTeX (`MathTex`), not plain strings.
        - Font size small but readable; consistent across slides.
        - Use thin white outlines and soft opacity for clarity.
        - Never use external images or complex textures.

        # Rules 
        - Each instruction should contain all about a single slide
        - Explain which shape, text, position to be drawn in the slide exactly 
        - Dont give vague instruction be deterministic
        - Give proper instructions about the orientation and position of the shapes
        - The slides should contain as minimum text as possible
        - The slide instructions is for a coding agent to code dont give unnecessary comments
        - Just write specfic object and where it should be 
        - Follow a similar font size throught the instructions 
        - Be specific on the sizes and symbols and colors used througout the instructions
        - Make sure the instructions make sense indepentdently 
        - External images cant be used only simple shapes can be made, which is possible using library manim 

        # Example
        ["Slide 1: Title Slide, Background: BLACK, Text: MathTex(r'\\text{{Pythagoras Theorem}}, Color: YELLOW', Position: Centered, Font size: Large", "Slide 2: Right-angled triangle, Background: BLACK, Shape: Polygon, vertices=[[-2, -1], [2, -1], [2, 1]], Color: BLUE_C, Outline: White, thin, Labels: a, b, c, Position: a near side [-2, -1] to [2, -1], b near side [2, -1] to [2, 1], c near side [-2, -1] to [2, 1], Color: YELLOW, Text: MathTex('a'), Position: below side a, Text: MathTex('b'), Position: right of side b, Text: MathTex('c'), Position: near hypotenuse c, Font size: Medium"]
         """
    )
    return {"directions": msg.directions}


def spawn_slide_workers(state: State):
    session_key = str(uuid.uuid4())
    sends = []
    print(state["directions"])
    for idx, direction in enumerate(state["directions"]):
        print(f"\n Running the coding agent on direction {direction}")
        sends.append(
            Send(
                "coding_agent",
                {
                    "direction": direction,
                    "rewrite": "not required",
                    "code": "",
                    "feedback": "",
                    "slide_index": idx,
                    "session_key": session_key,
                },
            )
        )
    return sends


# Main Graph
visium_workflow = StateGraph(State)
# Nodes
visium_workflow.add_node("script_writer", script_writer)
visium_workflow.add_node("director", director)
visium_workflow.add_node("coding_agent", coding_agent_compiled, output_keys="codes")
# Edges
visium_workflow.add_edge(START, "script_writer")
visium_workflow.add_edge("script_writer", "director")
visium_workflow.add_conditional_edges("director", spawn_slide_workers, ["coding_agent"])
visium_workflow.add_edge("coding_agent", END)


workflow = visium_workflow.compile()
initial_state = {
    "topic": "pythagoras theorem",
    "script": [],
    "directions": [],
    "code": "",
    "rewrite": "not required",
    "feedback": "",
    "codes": [],
}
output = workflow.invoke(initial_state)
# print(output["script"])
# ordered = sorted(output["codes"], key=lambda x: x["index"])
# final_codes = [c["code"] for c in ordered]
# print(final_codes)
