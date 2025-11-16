from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db.database import init_db
from app.routes import get_status, modify, video


# Database initialization on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    print("Shutting down...")


app = FastAPI(title="Visium Server", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)


# Static files to serve media content
os.makedirs("media/final_video", exist_ok=True)
os.makedirs("media/clips", exist_ok=True)
os.makedirs("media/clip_thumbs", exist_ok=True)
os.makedirs("media/final_thumbs", exist_ok=True)
os.makedirs("media/audio", exist_ok=True)
app.mount("/media", StaticFiles(directory="media"), name="media")

# All router registrations
app.include_router(video.router)
app.include_router(get_status.router)
app.include_router(modify.router)


@app.get("/")
def root():
    return {"message": "Visium Video Generator API is running"}
