import os
import re
import subprocess

from langgraph.graph import END, START, StateGraph

from app.prompts.manim_agent import code_generator_prompt, code_rewrite_prompt, visual_review_prompt
from app.schemas.manim_agent_schema import CodingAgentState
from app.services.llm_service import llm
from app.services.logging_service import logger
from app.services.video_service import mix_audio


def code_generator(state: CodingAgentState):
    print(f"\n code generator got called with state as {state['feedback']}")
    if state["rewrite"] == "required":
        msg = llm.invoke(
            code_rewrite_prompt(state["direction"], state["code"], state["feedback"], state["slide_index"])
        )
    else:
        msg = llm.invoke(code_generator_prompt(state["direction"], state["slide_index"]))

    return {"code": msg.content}


def visual_review(direction: str, frame_path: str, code: str):
    review_prompt = visual_review_prompt(direction, code)
    with open(frame_path, "rb") as f:
        image_bytes = f.read()
    result = llm.invoke(review_prompt, images=[image_bytes])
    logger.info(f"Visual review result: {result.content}")
    if "accepted" in result.content.lower():
        return {"rewrite": "not required", "feedback": None}
    return {"rewrite": "required", "feedback": result.content}


## Sandbox this in Production
def run_manim_code(code: str, slide_index: int, clip_video_id: str):
    base_dir = "media"
    codes_dir = os.path.join(base_dir, "codes", clip_video_id)
    videos_dir = os.path.join(base_dir, clip_video_id)

    os.makedirs(codes_dir, exist_ok=True)
    os.makedirs(videos_dir, exist_ok=True)

    code_path = os.path.join(codes_dir, f"slide_{slide_index}.py")
    video_name = f"slide_{slide_index}.mp4"
    video_name = f"slide_{slide_index}.mp4"
    thumbnail_name = f"slide_{slide_index}_last.png"

    # Clean up LLM markdown fences if any
    code = re.sub(r"^```(?:python)?\s*", "", code.strip())
    code = re.sub(r"```$", "", code.strip())

    # Save or overwrite code
    with open(code_path, "w") as f:
        f.write(code)
        logger.info(f"Saved Manim code to {code_path}")
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
                thumbs_path = os.path.join(root,thumbnail_name)
                return {"success": True, "video_path": video_path, "thumbnail_path": thumbs_path}

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
    result = run_manim_code(state["code"], state["slide_index"], state["clip_video_id"])
    if not result["success"]:
        simplified_error = re.search(r"ValueError: (.*)", result["error"])
        concise_feedback = simplified_error.group(1) if simplified_error else result["error"]
        return {"rewrite": "required", "feedback": concise_feedback}
    frame = extract_last_frame(result["video_path"])
    review = visual_review(state["direction"], frame, state["code"])
    if review["rewrite"] == "required":
        return {"rewrite": "required", "feedback": review.get("feedback")}
    else:
        logger.info("Mixing audio with video")
        base_dir = "media"
        clip_dir = os.path.join(base_dir, "clips", state["clip_video_id"])
        aud_dir = os.path.join(base_dir, "audio", state["clip_video_id"])
        os.makedirs(clip_dir, exist_ok=True)
        os.makedirs(aud_dir, exist_ok=True)
        clip_path = os.path.join(clip_dir, f"slide_{state['slide_index']}.mp4")
        aud_path = os.path.join(aud_dir, f"slide_{state['slide_index']}.mp3")
        mixed_video_path = mix_audio(result["video_path"], aud_path, clip_path)
        return {
            "rewrite": "not required",
            "video_paths": [{"index": state["slide_index"], "video_path": mixed_video_path}],
            "clips": [
                {
                    "id": state["clip_id"],
                    "video_id": state["clip_video_id"],
                    "index": state["slide_index"],
                    "clip_path": mixed_video_path,
                    "thumbnail_path": result.get("thumbnail_path"),
                    "narration_text": state["narration_text"],
                    "code": state["code"],
                    "prompt": state["direction"],
                    "duration": state.get("duration", 0),
                    "visuals": state.get("visuals", ""),
                    "audio_path": aud_path,
                }
            ],
        }


def route_code_review(state: CodingAgentState):
    if state["rewrite"] == "required":
        logger.info(f"Code review rejected for slide {state['slide_index']}")
        return "Rejected"
    else:
        logger.info(f"Code review accepted for slide {state['slide_index']}")
        return "Accepted"


def finalize_code(state: CodingAgentState):
    logger.info(f"Finalizing code for slide {state['slide_index']}")
    return {"codes": [{"index": state["slide_index"], "code": state["code"]}]}


# Coding Agent
coding_agent = StateGraph(CodingAgentState)
coding_agent.add_node("code_generator", code_generator)
coding_agent.add_node("manim_checker", manim_checker)
coding_agent.add_node("finalize_code", finalize_code)

coding_agent.add_edge(START, "code_generator")
coding_agent.add_edge("code_generator", "manim_checker")
coding_agent.add_conditional_edges(
    "manim_checker", route_code_review, {"Rejected": "code_generator", "Accepted": "finalize_code"}
)
coding_agent.add_edge("finalize_code", END)
coding_agent_compiled = coding_agent.compile()
