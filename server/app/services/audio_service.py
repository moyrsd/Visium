import json
import os
import subprocess

from deepgram import DeepgramClient
from dotenv import load_dotenv

from app.services.logging_service import logger

load_dotenv()


def generate_voiceovers(script, video_id: str):
    deepgram = DeepgramClient(api_key=os.getenv("DEEPGRAM_API_KEY"))
    audio_dir = f"media/audio/{video_id}"
    os.makedirs(audio_dir, exist_ok=True)
    audio_paths = []

    for i, s in enumerate(script, start=1):
        try:
            response_generator = deepgram.speak.v1.audio.generate(text=s.dialouge, model="aura-2-draco-en")
            path = os.path.join(audio_dir, f"slide_{i}.mp3")
            with open(path, "wb") as audio_file:
                for chunk in response_generator:
                    audio_file.write(chunk)
            duration = get_audio_duration(path)
            audio_paths.append(path)
            s.duration = duration
            logger.info(f"Audio saved to {path} (Duration: {duration:.2f} seconds)")

        except Exception as e:
            logger.error(f"Failed to generate audio for slide {i}: {e}")

    return script, audio_paths


def get_audio_duration(path):
    try:
        out = subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path], text=True
        )
        return float(json.loads(out)["format"]["duration"])
    except Exception:
        return 0.0
