from langgraph.graph import StateGraph, START, END
import os
import shutil  # noqa: F401
import subprocess
import uuid  # noqa: F401
import re
from app.services.llm_call import llm
from app.schemas.manim_agent import CodingAgentState
from app.prompts.manim_agent import (
    code_rewrite_prompt,
    code_generator_prompt,
    visual_review_prompt,
)


def code_generator(state: CodingAgentState):
    print(f"\n code generator got called with state as {state['feedback']}")
    if state["rewrite"] == "required":
        msg = llm.invoke(
            code_rewrite_prompt(
                state["direction"],
                state["code"],
                state["feedback"],
                state["slide_index"],
            )
        )
    else:
        msg = llm.invoke(
            code_generator_prompt(state["direction"], state["slide_index"])
        )

    return {"code": msg.content}


def visual_review(direction: str, frame_path: str, code: str):
    review_prompt = visual_review_prompt(direction, code)
    with open(frame_path, "rb") as f:
        image_bytes = f.read()
    result = llm.invoke(review_prompt, images=[image_bytes])
    # print(f"\n Visual Feedback {result.content}")
    if "accepted" in result.content.lower():
        return {"rewrite": "not required", "feedback": None}
    return {"rewrite": "required", "feedback": result.content}


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
    # fmt: off
    # Render with correct CLI flags
    cmd = ["manim",code_path,f"Slide{slide_index}","-ql","-o",video_name,"--media_dir",videos_dir,"--disable_caching"] 
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return {"success": False, "error": proc.stderr}
    # fmt: on

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


def extract_last_frame(video_path: str):
    frame_path = video_path.replace(".mp4", "_last.png")
    # fmt: off
    cmd = ["ffmpeg","-y","-sseof","-0.3","-i",video_path,"-vframes","1",frame_path]
    # fmt: on
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
    # session_key = state["session_key"]
    # base_dir = "media"
    # codes_dir = os.path.join(base_dir, "codes", session_key)
    # videos_dir = os.path.join(base_dir, "videos", session_key)

    # # Remove temporary directories if they exist
    # for path in [codes_dir, videos_dir]:
    #     if os.path.exists(path):
    #         try:
    #             shutil.rmtree(path)
    #             print(f"🧹 Cleaned up temporary folder: {path}")
    #         except Exception as e:
    #             print(f"⚠️ Failed to delete {path}: {e}")

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
