from sqlmodel import Session, select

from app.db.database import Job, Video, VideoStatus


def get_job(session: Session, job_id: str) -> Job:
    stmt = select(Job).where(Job.id == job_id)
    job = session.exec(stmt).first()
    if job is None:
        raise RuntimeError("Job not found in DB")
    return job


def mark_job(session: Session, job: Job, status: str, result: str | None = None):
    job.status = status
    job.result = result
    session.add(job)
    session.commit()
    session.refresh(job)


def get_video(session: Session, video_id: str):
    stmt = select(Video).where(Video.id == video_id)
    video = session.exec(stmt).first()
    if video is None:
        raise RuntimeError("Video not found in DB")
    return video


def add_video(session: Session, video: Video):
    session.add(video)
    session.commit()
    session.refresh(video)


def update_video_status(session: Session, video_id: str, status: VideoStatus):
    video=get_video(session, video_id)  
    video.status = status
    session.add(video)
    session.commit()
    session.refresh(video)

