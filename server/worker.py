import json
import os
import subprocess
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed


def get_duration(path: str) -> float:
    """Get video duration in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "json", path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    duration = float(json.loads(result.stdout)["format"]["duration"])
    return duration


def render_segment(seg):
    """Render a single segment using Manim."""
    name = seg["name"]
    code_lines = seg["code"]
    code = "\n".join(code_lines)

    # 1. Save code to temp .py file
    tmp_py = os.path.join(tempfile.gettempdir(), f"{name}.py")
    with open(tmp_py, "w") as f:
        f.write(code)

    # 2. Run manim CLI
    scene_class = name.capitalize()  # expects Scene1, Scene2...
    cmd = ["manim", "-ql", tmp_py, scene_class]

    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f"Error rendering {name}: {e.stderr.decode()}")
        return None

    # 3. Get path
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

    # preserve JSON order
    outputs.sort(key=lambda r: [s["name"] for s in segments].index(r["name"]))
    return outputs


def has_audio(path: str) -> bool:
    """Check if file has an audio stream using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a",
        "-show_entries", "stream=codec_type",
        "-of", "csv=p=0", path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return bool(result.stdout.strip())


def stitch_videos(results, output_path="final_video.mp4"):
    """Stitch clips, fade-in first, fade-out last, even if no audio."""
    video_paths = [os.path.abspath(seg["video"]) for seg in results]
    last_dur = get_duration(video_paths[-1])

    cmd = ["ffmpeg"]
    for v in video_paths:
        cmd.extend(["-i", v])

    filter_parts = []

    # fade-in on first
    if has_audio(video_paths[0]):
        filter_parts.append("[0:v]fade=t=in:st=0:d=1[v0]; [0:a]afade=t=in:st=0:d=1[a0]")
    else:
        filter_parts.append("[0:v]fade=t=in:st=0:d=1[v0]")

    # middle untouched
    for i in range(1, len(video_paths) - 1):
        if has_audio(video_paths[i]):
            filter_parts.append(f"[{i}:v]copy[v{i}]; [{i}:a]copy[a{i}]")
        else:
            filter_parts.append(f"[{i}:v]copy[v{i}]")

    # fade-out on last
    last = len(video_paths) - 1
    if has_audio(video_paths[last]):
        filter_parts.append(
            f"[{last}:v]fade=t=out:st={last_dur-1:.2f}:d=1[v{last}]; "
            f"[{last}:a]afade=t=out:st={last_dur-1:.2f}:d=1[a{last}]"
        )
    else:
        filter_parts.append(
            f"[{last}:v]fade=t=out:st={last_dur-1:.2f}:d=1[v{last}]"
        )

    # concat
    streams = "".join([f"[v{i}]" + (f"[a{i}]" if has_audio(video_paths[i]) else "") for i in range(len(video_paths))])
    vcount = len(video_paths)
    acount = sum(1 for v in video_paths if has_audio(v))

    if acount == vcount:  # all clips have audio
        filter_parts.append(f"{streams}concat=n={vcount}:v=1:a=1[outv][outa]")
        maps = ["-map", "[outv]", "-map", "[outa]"]
    else:  # no audio or mixed
        filter_parts.append(f"{streams}concat=n={vcount}:v=1:a=0[outv]")
        maps = ["-map", "[outv]"]

    filter_complex = "; ".join(filter_parts)

    cmd.extend([
        "-filter_complex", filter_complex,
        *maps,
        "-y", output_path
    ])

    subprocess.run(cmd, check=True)
    print(f"Final stitched video saved at: {output_path}")

if __name__ == "__main__":
    results = render_from_json("jobs.json", max_workers=3)
    print("\nAll segments rendered.")
    stitch_videos(results, output_path="final_video.mp4")
    for r in results:
        print(r)
