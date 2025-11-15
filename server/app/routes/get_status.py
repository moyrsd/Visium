from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.database import Job, get_session

router = APIRouter()
@router.get("/status/{job_id}")
def get_status(job_id: str, session: Session = Depends(get_session)):
    job = session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job.id, "status": job.status, "result": job.result}