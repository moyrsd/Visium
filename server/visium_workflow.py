from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated, Literal
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.types import Send
from typing import List
import operator
from dotenv import load_dotenv
import os

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


class CodingReviewState(BaseModel):
    rewrite: Literal["required", "not required"] = Field(
        "not required",
        json_schema_extra="Check if rewrite of the code is required or not",
    )
    feedback: str = Field(
        None,
        json_schema_extra="If code rewrite is required what changes to make suggest so that the geometry is exactly like described",
    )


class CodingAgentState(TypedDict):
    direction: str
    code: str
    slide_index: int
    rewrite: Literal["required", "not required"] = Field(
        "not required",
        json_schema_extra="Check if rewrite of the code is required or not",
    )
    feedback: str = Field(
        None,
        json_schema_extra="If code rewrite is required what changes to make suggest so that the geometry is exactly like described",
    )
    codes: Annotated[list, operator.add]


def script_writer(state: State):
    script_llm = llm.with_structured_output(ScriptState)
    msg = script_llm.invoke(
        f"Write a script on the {state['topic']}, you are preparing slides to explain the topic properly, the slides will be static in nature but will be made with manim library "
    )
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
                },
            )
        )
    return sends


def code_generator(state: CodingAgentState):
    if state["rewrite"] == "required":
        msg = msg = llm.invoke(f"""
            You are a professional Manim CE developer. Your task is to fix and finalize the Manim code below so it exactly matches the given slide specification.

            # Slide Specification
            {state["direction"]}

            # Previous Code
            {state["code"]}

            # Reviewer Feedback
            {state["feedback"]}

            # Instructions
            - Apply **only the minimal changes** required to correct the code.
            - Preserve the same class name (`Slide{state["slide_index"]}`) and structure.
            - Fix all syntax or logical issues (invalid methods, wrong vertex format, etc.).
            - Ensure all shapes, coordinates, colors, and LaTeX text match the description exactly.
            - Verify Manim CE 0.18+ API compatibility.

            # Rules
            - Use `Polygon(p1, p2, p3)` format, never nested lists.
            - Use `.set_fill(color, opacity=...)` and `.set_stroke(WHITE, width=1)` for shapes.
            - Use `.scale()` for sizing, not `font_size =`.
            - Use `.next_to`, `.move_to`, `.to_edge` for positioning.
            - Ensure all text is `MathTex`.
            - Output **only valid Python code**, no markdown or explanations.
            """)

    else:
        msg = llm.invoke(f"""
            You are an expert Manim CE (version 0.18+) developer. Your task is to generate **syntactically correct Python code** for a static slide based on the description below.

            # Visual Specification
            {state["direction"]}

            # Code Requirements
            - Define a class named `Slide{state["slide_index"]}(Scene)` with a `construct(self)` method.
            - Set `self.camera.background_color = BLACK`.
            - Use `MathTex` for all text and mathematical expressions (never Tex).
            - Use **only** Manim primitives: `Polygon`, `Square`, `Circle`, `Line`, `Arrow`, `Brace`.
            - For polygons, always use vertex unpacking like: `Polygon([-2, -1], [2, -1], [2, 1])`.
            - Do **not** use any nonexistent methods (for example, `set_vertices()` or `config.text_size`).
            - For size and position:
            - Use `.scale(1.0)` to `.scale(1.3)` for emphasis.
            - Use `.to_edge(UP)`, `.move_to(ORIGIN)`, `.next_to(...)`, or `.shift(...)` for positioning.
            - For style:
            - Shapes: `.set_stroke(WHITE, width=1)` and optional `.set_fill(<color>, opacity=<value>)`.
            - Text: consistent scaling and color as per spec.
            - Follow 3Blue1Brown visual grammar:
            - Background: BLACK
            - Colors: YELLOW, BLUE_C, GREEN_C, RED_C
            - Thin white outlines, soft color opacity.
            - **Output only the Python code.**
            - **Do not include markdown fences, comments, or explanations.**
            """)

    return {"code": msg.content}


def code_reviewer(state: CodingAgentState):
    evaluator = llm.with_structured_output(CodingReviewState)
    output = llm.with_structured_output(CodingReviewState)
    output = evaluator.invoke(f"""
    You are a Manim code reviewer ensuring fidelity between the intended visual description and the generated Python code.

    # Slide Specification
    {state["direction"]}

    # Code to Review
    {state["code"]}

    # Review Instructions
    - Check if every object mentioned in the description exists in the code.
    - Verify that color, size, and position constraints match.
    - Detect syntax or Manim API errors.
    - If any error or mismatch is found, set `rewrite='required'` and describe **exact changes needed**.
    - If code is correct, set `rewrite='not required'`.
    """)
    return {"rewrite": output.rewrite, "feedback": output.feedback}


def route_code_review(state: CodingAgentState):
    if state["rewrite"] == "required":
        return "Rejected"
    else:
        return "Accepted"


def finalize_code(state: CodingAgentState):
    return {"codes": [{"index": state["slide_index"], "code": state["code"]}]}


# Coding Agent
coding_agent = StateGraph(CodingAgentState)
coding_agent.add_node("code_generator", code_generator)
coding_agent.add_node("code_reviewer", code_reviewer)
coding_agent.add_node("finalize_code", finalize_code)

coding_agent.add_edge(START, "code_generator")
coding_agent.add_edge("code_generator", "code_reviewer")
coding_agent.add_conditional_edges(
    "code_reviewer",
    route_code_review,
    {"Rejected": "code_generator", "Accepted": "finalize_code"},
)
coding_agent.add_edge("finalize_code", END)
coding_agent_compiled = coding_agent.compile()

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
ordered = sorted(output["codes"], key=lambda x: x["index"])
final_codes = [c["code"] for c in ordered]
print(final_codes)
