import os
import re
import subprocess

from langgraph.graph import END, START, StateGraph

from app.db.database import VideoStatus
from app.prompts.manim_agent import code_generator_prompt, code_rewrite_prompt, visual_review_prompt
from app.schemas.manim_agent_schema import CodingAgentState
from app.services.llm_service import llm
from app.services.logging_service import logger
from app.services.video_service import mix_audio


def code_generator(state: CodingAgentState):
    logger.info(f"[code_generator] called for slide_index={state.get('slide_index')} clip_video_id={state.get('clip_video_id')}")
    logger.debug(f"[code_generator] incoming state rewrite={state.get('rewrite')} feedback={state.get('feedback')}")
    if state["rewrite"] == "required":
        logger.info("[code_generator] Using rewrite prompt")
        msg = llm.invoke(
            code_rewrite_prompt(state["direction"], state["code"], state["feedback"], state["slide_index"])
        )
    else:
        logger.info("[code_generator] Using fresh code generation prompt")
        msg = llm.invoke(code_generator_prompt(state["direction"], state["slide_index"]))

    logger.debug(f"[code_generator] LLM response length={len(getattr(msg, 'content', '') or '')}")
    logger.info("[code_generator] Generated code returned")
    return {"code": msg.content}


def visual_review(direction: str, frame_path: str, code: str):
    logger.info(f"[visual_review] Called for direction={direction} frame_path={frame_path}")
    try:
        review_prompt = visual_review_prompt(direction, code)
        with open(frame_path, "rb") as f:
            image_bytes = f.read()
        logger.debug(f"[visual_review] Read image bytes: {len(image_bytes)} bytes")
        result = llm.invoke(review_prompt, images=[image_bytes])
        logger.info(f"[visual_review] Visual review received")
        logger.debug(f"[visual_review] Result content (truncated): {result.content[:500]}")
        if "accepted" in result.content.lower():
            logger.info("[visual_review] Marked as accepted by LLM")
            return {"rewrite": "not required", "feedback": None}
        logger.info("[visual_review] Marked as requires rewrite by LLM")
        return {"rewrite": "required", "feedback": result.content}
    except FileNotFoundError:
        logger.error(f"[visual_review] Frame not found: {frame_path}")
        return {"rewrite": "required", "feedback": "Frame not found for visual review"}
    except Exception as e:
        logger.exception(f"[visual_review] Unexpected error: {e}")
        return {"rewrite": "required", "feedback": str(e)}


## Sandbox this in Production
def run_manim_code(code: str, slide_index: int, clip_video_id: str):
    logger.info(f"[run_manim_code] Start rendering slide_index={slide_index} clip_video_id={clip_video_id}")
    base_dir = "media"
    codes_dir = os.path.join(base_dir, "codes", clip_video_id)
    videos_dir = os.path.join(base_dir, clip_video_id)

    os.makedirs(codes_dir, exist_ok=True)
    os.makedirs(videos_dir, exist_ok=True)
    logger.debug(f"[run_manim_code] Ensured directories codes_dir={codes_dir} videos_dir={videos_dir}")

    code_path = os.path.join(codes_dir, f"slide_{slide_index}.py")
    video_name = f"slide_{slide_index}.mp4"
    thumbnail_name = f"slide_{slide_index}_last.png"

    # Clean up LLM markdown fences if any
    code = re.sub(r"^```(?:python)?\s*", "", code.strip())
    code = re.sub(r"```$", "", code.strip())

    # Save or overwrite code
    try:
        with open(code_path, "w") as f:
            f.write(code)
        logger.info(f"[run_manim_code] Saved Manim code to {code_path}")
        logger.debug(f"[run_manim_code] Code snippet (truncated): {code[:500]}")
    except Exception as e:
        logger.exception(f"[run_manim_code] Failed to write code file: {e}")
        return {"success": False, "error": str(e)}

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
    logger.info(f"[run_manim_code] Running manim with command: {' '.join(cmd)}")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    logger.debug(f"[run_manim_code] manim returncode={proc.returncode}")
    logger.debug(f"[run_manim_code] manim stdout (truncated): {proc.stdout[:1000]}")
    logger.debug(f"[run_manim_code] manim stderr (truncated): {proc.stderr[:1000]}")
    if proc.returncode != 0:
        logger.error(f"[run_manim_code] manim failed for slide {slide_index}: {proc.stderr[:1000]}")
        return {"success": False, "error": proc.stderr}

    # Find generated video path (Manim stores inside subfolders)
    logger.info(f"[run_manim_code] Searching for generated video under {videos_dir}")
    for root, _, files in os.walk(videos_dir):
        for file in files:
            if file == video_name:
                video_path = os.path.join(root, file)
                thumbs_path = os.path.join(root, thumbnail_name)
                logger.info(f"[run_manim_code] Found video at {video_path}")
                logger.debug(f"[run_manim_code] Thumbnail expected at {thumbs_path}")
                return {"success": True, "video_path": video_path, "thumbnail_path": thumbs_path}

    logger.warning("[run_manim_code] No video file found after manim run")
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
    cmd = ["ffmpeg", "-y", "-sseof", "-0.3", "-i", video_path, "-vframes", "1", frame_path]
    logger.info(f"[extract_last_frame] Extracting last frame from {video_path} to {frame_path}")
    logger.debug(f"[extract_last_frame] Running ffmpeg command: {' '.join(cmd)}")
    proc = subprocess.run(cmd, capture_output=True, text=True)
    logger.debug(f"[extract_last_frame] ffmpeg returncode={proc.returncode}")
    if proc.stdout:
        logger.debug(f"[extract_last_frame] ffmpeg stdout (truncated): {proc.stdout[:500]}")
    if proc.stderr:
        logger.debug(f"[extract_last_frame] ffmpeg stderr (truncated): {proc.stderr[:500]}")
    if proc.returncode != 0:
        logger.error(f"[extract_last_frame] ffmpeg failed for {video_path}: {proc.stderr[:500]}")
    else:
        logger.info(f"[extract_last_frame] Frame saved to {frame_path}")
    return frame_path


def manim_checker(state: CodingAgentState):
    logger.info(f"[manim_checker] Checking slide_index={state.get('slide_index')} clip_video_id={state.get('clip_video_id')}")
    result = run_manim_code(state["code"], state["slide_index"], state["clip_video_id"])
    logger.debug(f"[manim_checker] run_manim_code result: {result}")
    if not result["success"]:
        logger.warning(f"[manim_checker] Render failed: {result.get('error')}")
        simplified_error = re.search(r"ValueError: (.*)", result["error"] or "")
        concise_feedback = simplified_error.group(1) if simplified_error else result["error"]
        logger.debug(f"[manim_checker] concise_feedback: {concise_feedback}")
        return {"rewrite": "required", "feedback": concise_feedback}
    frame = extract_last_frame(result["video_path"])
    logger.info(f"[manim_checker] Extracted frame at {frame}")
    if not os.path.exists(frame):
        logger.warning(f"[manim_checker] Extracted frame does not exist: {frame}")
    review = visual_review(state["direction"], frame, state["code"])
    logger.debug(f"[manim_checker] visual_review returned: {review}")
    if review["rewrite"] == "required":
        logger.info("[manim_checker] Visual review requested rewrite")
        return {"rewrite": "required", "feedback": review.get("feedback")}
    else:
        logger.info("[manim_checker] Visual review accepted, proceeding to mix audio")
        base_dir = "media"
        clip_dir = os.path.join(base_dir, "clips", state["clip_video_id"])
        aud_dir = os.path.join(base_dir, "audio", state["clip_video_id"])
        os.makedirs(clip_dir, exist_ok=True)
        os.makedirs(aud_dir, exist_ok=True)
        logger.debug(f"[manim_checker] Ensured clip and audio dirs: {clip_dir}, {aud_dir}")
        clip_path = os.path.join(clip_dir, f"slide_{state['slide_index']}.mp4")
        aud_path = os.path.join(aud_dir, f"slide_{state['slide_index']}.mp3")
        logger.info(f"[manim_checker] Mixing audio {aud_path} into video {result['video_path']} -> {clip_path}")
        try:
            mixed_video_path = mix_audio(result["video_path"], aud_path, clip_path)
            logger.info(f"[manim_checker] Mixed video saved to {mixed_video_path}")
        except Exception as e:
            logger.exception(f"[manim_checker] Failed to mix audio: {e}")
            return {"rewrite": "required", "feedback": f"Audio mixing failed: {e}"}
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
                    "status": VideoStatus.READY,
                    "duration": state.get("duration", 0),
                    "visuals": state.get("visuals", ""),
                    "audio_path": aud_path,
                }
            ],
        }


def route_code_review(state: CodingAgentState):
    logger.info(f"[route_code_review] slide_index={state.get('slide_index')} rewrite={state.get('rewrite')}")
    if state["rewrite"] == "required":
        logger.info(f"[route_code_review] Code review rejected for slide {state['slide_index']}")
        return "Rejected"
    else:
        logger.info(f"[route_code_review] Code review accepted for slide {state['slide_index']}")
        return "Accepted"


def finalize_code(state: CodingAgentState):
    logger.info(f"[finalize_code] Finalizing code for slide {state['slide_index']}")
    logger.debug(f"[finalize_code] Final code length={len(state.get('code',''))}")
    return {"codes": [{"index": state["slide_index"], "code": state["code"]}]}


# Coding Agent
logger.info("[module] Building coding_agent StateGraph")
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
logger.info("[module] coding_agent compiled successfully")
