import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlmodel import Session, select

from app.db.database import Job, Video, VideoStatus, get_session
from app.db.operations import update_video_status
from app.schemas.main_schema import GenerateTitleDesciption, PromptInput
from app.services.llm_service import llm
from app.services.video_service import render_video
from app.services.workflow_service import run_complete_workflow

router = APIRouter()


@router.post("/generate_video")
async def generate_video(req: PromptInput, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    job_id = str(uuid.uuid4())
    video_id = str(uuid.uuid4())
    msg = generate_title_description(req.topic)
    title = msg.title
    description = msg.description
    video = Video(id=video_id, title=title, description=description,status=VideoStatus.PENDING)
    job = Job(id=job_id, status="started", result=None, video_id=video_id)
    session.add(job)
    session.add(video)
    session.commit()
    background_tasks.add_task(run_complete_workflow, req.topic, job_id, video_id, session)
    return {
        "job_id": job_id,
        "video_id": video_id,
        "message": "Video generation started",
        "title": title,
        "description": description,
    }


@router.get("/videos")
def list_videos(session: Session = Depends(get_session)):
    videos = session.exec(select(Video)).all()
    return [
        {
            "id": v.id,
            "title": v.title,
            "status": v.status.value,
            "description": v.description,
            "created_at": v.created_at,
            "final_video_path": v.final_video_path,
            "thumbnail_path": v.thumbnail_path,
            "clip_count": len(v.clips),
        }
        for v in videos
    ]


@router.get("/videos/{video_id}")
def get_video(video_id: str, session: Session = Depends(get_session)):
    video = session.get(Video, video_id)
    if not video:
        raise HTTPException(404, "Video not found")

    return {
        "id": video.id,
        "title": video.title,
        "status": video.status.value,
        "description": video.description,
        "created_at": video.created_at,
        "final_video_path": video.final_video_path,
        "clips": [
            {
                "id": c.id,
                "index": c.index,
                "clip_path": c.clip_path,
                "thumbnail_path": c.thumbnail_path,
                "narration_text": c.narration_text,
                "code": c.code,
                "prompt": c.prompt,
                "duration": c.duration,
                "visuals": c.visuals,
            }
            for c in video.clips
        ],
    }


@router.post("/videos/{video_id}/render")
def render_video_again(video_id: str, session: Session = Depends(get_session)):
    video = session.get(Video, video_id)
    out_path = video.final_video_path
    update_video_status(session, video_id, VideoStatus.PENDING)
    music_paths = [f"3b1b_music_library/{i}.mp3" for i in range(1, 11)]
    clips = [v.clip_path for v in video.clips]
    render_video(clips, music_paths, out_path)
    update_video_status(session, video_id, VideoStatus.READY)
    return {"message": "Video re-rendered successfully", "final_video_path": out_path}



def generate_title_description(topic: str) -> GenerateTitleDesciption:
    title_desc_llm = llm.with_structured_output(GenerateTitleDesciption)
    msg = title_desc_llm.invoke(
        f"Generate a title and a brief description for a video on the topic: {topic}.The title should be concise and engaging, while the description should provide a clear overview of the video's content. all in english"
    )
    return msg
