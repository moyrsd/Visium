import json
import os
import subprocess
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed


def render_segment(seg):
    """Render a single segment using Manim."""
    name = seg["name"]
    code_lines = seg["code"]
    code = "\n".join(code_lines)  # join array of lines into code

    # 1. Save code to temp .py file
    tmp_py = os.path.join(tempfile.gettempdir(), f"{name}.py")
    with open(tmp_py, "w") as f:
        f.write(code)

    # 2. Run manim CLI on it
    scene_class = name.capitalize()  # expects Scene class named "Scene1", "Scene2", etc.
    cmd = ["manim", "-ql", tmp_py, scene_class]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Error rendering {name}: {e.stderr.decode()}")
        return None

    # 3. Expected output path (Manim default folder)
    video_path = f"media/videos/{os.path.splitext(os.path.basename(tmp_py))[0]}/480p15/{scene_class}.mp4"

    print(f"Rendered {name} → {video_path}")

    return {
        "name": name,
        "video": video_path,
        "dialogue": seg["dialogue"],
        "bg_music": seg["bg_music"],
        "transition": seg["transition"]
    }


def render_from_json(json_file, max_workers=2):
    """Render all segments in parallel."""
    with open(json_file, "r") as f:
        job = json.load(f)

    segments = job["segments"]
    outputs = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(render_segment, seg): seg for seg in segments}
        for future in as_completed(futures):
            result = future.result()
            if result:
                outputs.append(result)

    return outputs


if __name__ == "__main__":
    results = render_from_json("jobs.json", max_workers=3)  # parallel workers
    print("\nAll segments rendered:")
    for r in results:
        print(r)
