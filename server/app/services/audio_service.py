import json
import os
import subprocess

from deepgram import DeepgramClient
from dotenv import load_dotenv

from app.services.logging_service import logger

load_dotenv()


def generate_voiceovers(script, video_id: str):
    audio_dir = f"media/audio/{video_id}"
    os.makedirs(audio_dir, exist_ok=True)
    audio_paths = []

    for i, s in enumerate(script, start=1):
        try:
            path = os.path.join(audio_dir, f"slide_{i}.mp3")
            path,duration = generate_single_voiceover(s.text, path)
            audio_paths.append(path)
            s.duration = duration
            logger.info(f"Audio saved to {path} (Duration: {duration:.2f} seconds)")
            
        except Exception as e:
            logger.error(f"Failed to generate audio for slide {i}: {e}")

    return script, audio_paths




def generate_single_voiceover(text, output_path):
    deepgram = DeepgramClient(api_key=os.getenv("DEEPGRAM_API_KEY"))
    try:
        response_generator = deepgram.speak.v1.audio.generate(text=text, model="aura-2-draco-en")
        with open(output_path, "wb") as audio_file:
            for chunk in response_generator:
                audio_file.write(chunk)
        duration = get_audio_duration(output_path)
        logger.info(f"Single audio saved to {output_path} (Duration: {duration:.2f} seconds)")
        return output_path, duration

    except Exception as e:
        logger.error(f"Failed to generate single audio: {e}")
        return None, 0.0
    

def get_audio_duration(path):
    try:
        out = subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path], text=True
        )
        return float(json.loads(out)["format"]["duration"])
    except Exception:
        return 0.0
