from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
import os
from app.agents.visium_workflow import workflow
from app.services.video import final_video

app = FastAPI(title="Visium Server")


JOBS = {}


class PromptInput(BaseModel):
    topic: str


@app.post("/generate_video")
async def generate_video(req: PromptInput, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": "started", "result": None}
    background_tasks.add_task(run_workflow, req.topic, job_id)
    return {"job_id": job_id, "message": "Video generation started"}


@app.get("/status/{job_id}")
async def check_status(job_id: str):
    if job_id not in JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    return JOBS[job_id]


def run_workflow(topic: str, job_id: str):
    """
    Executes the full Visium workflow in the background.
    Updates JOBS dict when done.
    """
    try:
        JOBS[job_id]["status"] = "running"

        # Create session ID for intermediate outputs
        session_key = str(uuid.uuid4())
        initial_state = {
            "topic": topic,
            "script": [],
            "directions": [],
            "code": "",
            "rewrite": "not required",
            "feedback": "",
            "codes": [],
            "id": session_key,
        }

        # Run main graph
        output = workflow.invoke(initial_state)
        video_paths_ordered = sorted(output["video_paths"], key=lambda x: x["index"])
        video_paths = [v["video_path"] for v in video_paths_ordered]
        audio_paths = output["audio_paths"]
        music_paths = [f"3b1b_music_library/{i}.mp3" for i in range(1, 11)]

        # Generate final video
        final_video(video_paths, audio_paths, music_paths)

        result_path = os.path.abspath("output.mp4")
        JOBS[job_id] = {
            "status": "completed",
            "result": {"video_path": result_path, "job_id": job_id},
        }

    except Exception as e:
        JOBS[job_id] = {"status": "failed", "result": str(e)}
        raise


@app.get("/")
def root():
    return {"message": "Visium Video Generator API is running"}
