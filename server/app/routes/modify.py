from fastapi import APIRouter, Depends, Form, HTTPException
from sqlmodel import Session

from app.agents.manim_agent import coding_agent_compiled
from app.db.database import Clip, VideoStatus, get_session
from app.services.audio_service import generate_single_voiceover
from app.services.logging_service import logger

router = APIRouter()
@router.post("/modify_clip/{clip_id}")
async def modify_clip(clip_id: str, prompt: str = Form(None), code : str = Form(None), narration_text: str = Form(None), visuals: str = Form(None), session: Session = Depends(get_session)):
    try:
            clip = session.get(Clip, clip_id)
            if not clip:
                raise HTTPException(status_code=404, detail="Clip not found")
            
            duration = None
            audio_path = None
            if narration_text:
                audio_path, duration = generate_single_voiceover(narration_text, clip.audio_path)
            clip.status = VideoStatus.PENDING
            session.add(clip)
            session.commit()
            session.refresh(clip)

            intial_state = {
                "direction": prompt or clip.direction,
                "rewrite": "not required",
                "code": code or clip.code,
                "feedback": "",
                "slide_index": clip.index,
                "clip_id": clip.id,
                "clip_video_id": clip.video_id,
                "narration_text": narration_text or clip.narration_text,
                "duration": duration or clip.duration,
                "visuals": visuals or clip.visuals,
            }
            logger.info(f"Modifying clip {clip.id} with state: {intial_state}")
            result = coding_agent_compiled.invoke(intial_state)
            clip.direction = result["clips"][0]["prompt"]
            clip.code = result["clips"][0]["code"]
            clip.narration_text = result["clips"][0]["narration_text"]
            clip.visuals = result["clips"][0]["visuals"]
            clip.duration = duration or clip.duration
            clip.thumbnail_path = result["clips"][0]["thumbnail_path"] or clip.thumbnail_path
            clip.audio_path = audio_path or clip.audio_path
            clip.prompt = result["clips"][0]["prompt"]
            clip.status = VideoStatus.READY
            session.add(clip)
            session.commit()
            session.refresh(clip)
            return clip
    except Exception as e:
        print(f"ERROR in modify_clip: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


