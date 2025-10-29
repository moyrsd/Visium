from pydantic import Field
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict, Annotated, Literal
from langchain_google_genai import ChatGoogleGenerativeAI
import operator
from dotenv import load_dotenv
import os
import shutil
import subprocess
import uuid  # noqa: F401
import re


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


def code_generator(state: CodingAgentState):
    # print(f"\n code generator got called with state as {state['feedback']}")
    if state["rewrite"] == "required":
        msg = llm.invoke(f"""
            You are a professional Manim CE developer. Your task is to fix and finalize the Manim code below so it exactly matches the given slide specification.

            # Slide Specification
            {state["direction"]}

            # Previous Code
            {state["code"]}

            # Reviewer Feedback
            {state["feedback"]}

            # Instructions
            - Never include ```python fences in your output.
            - Apply **only the minimal changes** required to correct the code.
            - Preserve the same class name (`Slide{state["slide_index"]}`) and structure.
            - Fix all syntax or logical issues (invalid methods, wrong vertex format, etc.).
            - Ensure all shapes, coordinates, colors, and LaTeX text match the description exactly.
            - Verify Manim CE 0.18+ API compatibility.

            # Rules
            - All coordinate points must be 3D vectors of the form [x, y, 0]. Using [x, y] will cause broadcasting errors.
            - Use `Polygon(p1, p2, p3)` format, never nested lists.
            - Use `.set_fill(color, opacity=...)` and `.set_stroke(WHITE, width=1)` for shapes.
            - Use `.scale()` for sizing, not `font_size =`.
            - Use `.next_to`, `.move_to`, `.to_edge` for positioning.
            - Ensure all text is `MathTex`.
            - You must output only Python source code — not markdown fences, not explanations, not comments.
            """)

    else:
        msg = llm.invoke(f"""
            You are an expert Manim CE (version 0.18+) developer. Your task is to generate slide based on the description below.

            # Visual Specification
            {state["direction"]}

            # Code Requirements
            - All coordinate points must be 3D vectors of the form [x, y, 0]. Using [x, y] will cause broadcasting errors.
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


## Sandbox this in Production
def run_manim_code(code: str, slide_index: int, session_key: str):
    base_dir = "media"
    codes_dir = os.path.join(base_dir, "codes", session_key)
    videos_dir = os.path.join(base_dir, "videos", session_key)

    os.makedirs(codes_dir, exist_ok=True)
    os.makedirs(videos_dir, exist_ok=True)

    code_path = os.path.join(codes_dir, f"slide_{slide_index}.py")
    video_name = f"slide_{slide_index}.mp4"

    # Clean up LLM markdown fences if any
    code = re.sub(r"^```(?:python)?\s*", "", code.strip())
    code = re.sub(r"```$", "", code.strip())

    # print(f"\n\n {code}")

    # Save or overwrite code
    with open(code_path, "w") as f:
        f.write(code)

    # Remove previous renders
    old_outputs = [
        os.path.join(videos_dir, f)
        for f in os.listdir(videos_dir)
        if f.startswith(f"slide_{slide_index}")
    ]
    for f in old_outputs:
        os.remove(f)

    # Render with correct CLI flags
    cmd = [
        "manim",
        code_path,
        f"Slide{slide_index}",
        "-ql",
        "-o",
        video_name,
        "--media_dir",
        videos_dir,
        "--disable_caching",
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.returncode != 0:
        return {"success": False, "error": proc.stderr}

    # Find generated video path (Manim stores inside subfolders)
    for root, _, files in os.walk(videos_dir):
        for file in files:
            if file == video_name:
                video_path = os.path.join(root, file)
                return {"success": True, "video_path": video_path}

    return {
        "success": False,
        "error": (
            "No video was generated because the scene contains no animations. "
            "Manim renders only a static image when no animations are played. "
            "To fix this, you must include at least one animation, such as "
            "self.play(Create(circle1)) or self.play(FadeIn(circle2)). "
            "Ensure that the slide includes a simple animation for visibility."
        ),
    }


def visual_review(direction: str, frame_path: str, code: str):
    review_prompt = f"""
            You are a visual reviewer for Manim slides with tolerance awareness.

            You are given:
            1. A rendered Manim slide image (attached below).
            2. The textual specification describing how the slide should look:

            {direction}

            # The code that has generated the image
            {code}

            Your job:
            - Evaluate if the image visually matches the specification **to the human eye**.
            - Ignore tiny geometric or typographic deviations (within ~10% size or 0.2 units shift).
            - Focus only on meaningful differences: missing elements, wrong colors, or major misplacement.

            Decision criteria:
            1. If all major elements exist, colors are approximately correct, and text is readable and near its intended location -> reply **accepted**.
            2. Otherwise, reply **rejected:** followed by concise issue list and specific code-level fixes.

            Output format (strictly follow):
            accepted
            -- OR --
            rejected:
            - Issue: <short, clear mismatch>
            Fix: <specific code-level instruction>

            Rules:
            - Give specific feedback as given in the directions , not some vague something thing is off type feedback
            - If You cant see the image say to increase the video length by 1 sec
            - You can see the image — never say otherwise.
            - Ignore very small differences in font size, stroke width, or exact coordinates.
            - Accept if the slide looks visually correct, even if the code differs slightly.
            - Only reject for substantial visual errors (wrong color, missing text, wrong shape, unreadable label, misplaced geometry).
            - Estimate small fix magnitudes (e.g., "shift DOWN*0.3", "set_fill(RED_C, opacity=0.8)").
            """

    with open(frame_path, "rb") as f:
        image_bytes = f.read()
    result = llm.invoke(review_prompt, images=[image_bytes])
    print(f"\n Visual Feedback {result.content}")
    if "accepted" in result.content.lower():
        return {"rewrite": "not required", "feedback": None}
    return {"rewrite": "required", "feedback": result.content}


def extract_last_frame(video_path: str):
    frame_path = video_path.replace(".mp4", "_last.png")
    cmd = [
        "ffmpeg",
        "-y",
        "-sseof",
        "-0.3",
        "-i",
        video_path,
        "-vframes",
        "1",
        frame_path,
    ]
    subprocess.run(cmd, capture_output=True)
    return frame_path


def manim_checker(state: CodingAgentState):
    result = run_manim_code(state["code"], state["slide_index"], state["session_key"])
    if not result["success"]:
        simplified_error = re.search(r"ValueError: (.*)", result["error"])
        concise_feedback = (
            simplified_error.group(1) if simplified_error else result["error"]
        )
        return {"rewrite": "required", "feedback": concise_feedback}
    frame = extract_last_frame(result["video_path"])
    review = visual_review(state["direction"], frame, state["code"])
    if review["rewrite"] == "required":
        return {"rewrite": "required", "feedback": review.get("feedback")}
    else:
        return {"rewrite": "not required"}


def route_code_review(state: CodingAgentState):
    if state["rewrite"] == "required":
        return "Rejected"
    else:
        return "Accepted"


def finalize_code(state: CodingAgentState):
    session_key = state["session_key"]
    base_dir = "media"
    codes_dir = os.path.join(base_dir, "codes", session_key)
    videos_dir = os.path.join(base_dir, "videos", session_key)

    # Remove temporary directories if they exist
    for path in [codes_dir, videos_dir]:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                print(f"🧹 Cleaned up temporary folder: {path}")
            except Exception as e:
                print(f"⚠️ Failed to delete {path}: {e}")

    return {"codes": [{"index": state["slide_index"], "code": state["code"]}]}


# Coding Agent
coding_agent = StateGraph(CodingAgentState)
coding_agent.add_node("code_generator", code_generator)
coding_agent.add_node("manim_checker", manim_checker)
coding_agent.add_node("finalize_code", finalize_code)

coding_agent.add_edge(START, "code_generator")
coding_agent.add_edge("code_generator", "manim_checker")
coding_agent.add_conditional_edges(
    "manim_checker",
    route_code_review,
    {"Rejected": "code_generator", "Accepted": "finalize_code"},
)
coding_agent.add_edge("finalize_code", END)
coding_agent_compiled = coding_agent.compile()


# initial_state = {
#     "direction": "Slide 1: Two circles, Background: BLACK, Shape: Circle, Center: [-2, 0], Radius: 1, Color: BLUE_C, Outline: White, thin, Shape: Circle, Center: [2, 0], Radius: 1, Color: BLUE_C, Outline: White, thin",
#     "rewrite": "not required",
#     "code": "",
#     "feedback": "",
#     "slide_index": 1,
#     "session_key": str(uuid.uuid4()),
# }
# output = coding_agent_compiled.invoke(initial_state)
# print(output["code"])
