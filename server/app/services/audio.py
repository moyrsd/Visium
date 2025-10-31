from deepgram import DeepgramClient
import os
from dotenv import load_dotenv
from app.schemas.visium_graph import Script  # noqa: F401
import uuid  # noqa: F401
import subprocess
import json


load_dotenv()


def generate_voiceovers(script, session_key):
    deepgram = DeepgramClient(api_key=os.getenv("DEEPGRAM_API_KEY"))
    audio_dir = f"media/audio/{session_key}"
    os.makedirs(audio_dir, exist_ok=True)
    audio_paths = []

    for i, s in enumerate(script, start=1):
        try:
            response_generator = deepgram.speak.v1.audio.generate(
                text=s.dialouge,
                model="aura-2-draco-en",
            )
            path = os.path.join(audio_dir, f"slide_{i}.mp3")
            with open(path, "wb") as audio_file:
                for chunk in response_generator:
                    audio_file.write(chunk)
            duration = get_audio_duration(path)
            audio_paths.append(path)
            s.duration = duration
            print(f"Audio saved to {path} (Duration: {duration:.2f} seconds)")

        except Exception as e:
            print(f"Exception: {e}")

    return script, audio_paths


def get_audio_duration(path):
    # fmt: off
    try:
        out = subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path],
            text=True
        )
        return float(json.loads(out)["format"]["duration"])
    # fmt : on
    except Exception:
        return 0.0


# if __name__ == "__main__":
#     script = [
#         Script(
#             dialouge="Welcome to the presentation on the Pythagoras Theorem!",
#             slide_visuals="Title Slide: Pythagoras Theorem",
#         ),
#         Script(
#             dialouge="The Pythagoras Theorem applies only to right-angled triangles. A right-angled triangle has one angle that measures 90 degrees. The side opposite the right angle is called the hypotenuse, labeled as 'c'. The other two sides are 'a' and 'b'.",
#             slide_visuals="Slide 2: Right-angled triangle with sides labeled a, b, and c (hypotenuse)",
#         ),
#     ]
#     session_key = str(uuid.uuid4())
#     generate_voiceovers(script, session_key)
#     print(script)
#     print("All audios generated successfully")
