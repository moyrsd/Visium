import os

from sqlmodel import Session, select

from app.agents.visium_workflow import workflow
from app.db.database import Clip, Video, VideoStatus
from app.db.operations import get_job, mark_job, update_video_status
from app.services.logging_service import logger
from app.services.video_service import render_video


def run_complete_workflow(topic: str, job_id: str, video_id: str, session: Session):
    job = get_job(session, job_id)
    try:
        mark_job(session, job, "running")
        out_path = run_workflow(topic, video_id, job_id, session)
        update_video_status(session, video_id, VideoStatus.READY)
        mark_job(session, job, "completed", result=out_path)

    except Exception as e:
        logger.exception("Workflow failed for job %s: %s", job_id, e)
        if job:
            mark_job(session, job, "failed", result=str(e))
        raise


def run_workflow(topic: str, video_id: str, job_id: str, session: Session) -> str:
    initial_state = {
        "topic": topic,
        "script": [],
        "directions": [],
        "code": "",
        "rewrite": "not required",
        "feedback": "",
        "codes": [],
        "video_paths": [],
        "video_id": video_id,
        "job_id": job_id,
        "clips": [],
    }

    output = workflow.invoke(initial_state)
    ordered = sorted(output["video_paths"], key=lambda x: x["index"])
    clips = sorted(output["clips"], key=lambda x: x["index"])
    clip_objs = [Clip(**c) for c in clips]
    for obj in clip_objs:
        session.add(obj)
    session.commit()
    for obj in clip_objs:
        session.refresh(obj)
    video_paths = [v["video_path"] for v in ordered]
    music_paths = [f"3b1b_music_library/{i}.mp3" for i in range(1, 11)]
    out_path = os.path.join("media/final_video/", f"{video_id}.mp4")
    job = get_job(session, job_id)
    mark_job(session, job, "video_rendering_in_progress")
    render_video(video_paths, music_paths, out_path)

    video = session.exec(select(Video).where(Video.id == video_id)).first()
    if video is None:
        raise RuntimeError("Video not found in DB")
    video.final_video_path = out_path
    video.thumbnail_path = clips[0]["thumbnail_path"] if clips else None
    session.add(video)
    session.commit()
    session.refresh(video)
    return out_path
