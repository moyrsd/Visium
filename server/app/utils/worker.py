import json
import os
import subprocess
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from app.schemas.schema import VideoScript


class VisiumJob:
    def __init__(self,json_path,output_path,quality="480p15")->None:
        self.json_path = json_path 
        self.output_path = output_path
        self.max_workers = 3
        self.quality = quality
    
    def _load_from_json(self)->VideoScript:
        with open(self.json_path,"r") as f:
            job = json.load(f)
        return job 
    
    def _render_segment(self,seg):
        """Render a single segment using Manim."""
        name = seg["name"]
        code = seg["code"]
        # code = "\n".join(codelines)

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
        video_path = f"media/videos/{os.path.splitext(os.path.basename(tmp_py))[0]}/{self.quality}/{scene_class}.mp4"

        print(f"Rendered {name} → {video_path}")

        return {
            "name": name,
            "video": video_path,
            "dialogue": seg["dialogue"],
            "bg_music": seg["bg_music"],
        }
    
    def render_all(self):
        job = self._load_from_json()
        segments = job["segments"]
        outputs = []

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self._render_segment, seg): seg for seg in segments}
            for future in as_completed(futures):
                result = future.result()
                if result and os.path.exists(result["video"]):
                    outputs.append(result)
                else:
                    print(f"⚠️ Skipping missing or failed scene: {futures[future]['name']}")

        outputs.sort(key=lambda r: [s["name"] for s in segments].index(r["name"]))
        return outputs
    
  
    
    def stitch_videos(self, results):
        """Join all videos directly with ffmpeg, no effects."""
        # Collect paths
        video_paths = [os.path.abspath(seg["video"]) for seg in results]

        # Create temporary list file for ffmpeg concat
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt") as f:
            for v in video_paths:
                f.write(f"file '{v}'\n")
            list_path = f.name

        # Run ffmpeg concat
        cmd = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_path,
            "-c", "copy",
            self.output_path
        ]

        subprocess.run(cmd, check=True)
        os.remove(list_path)
        print(f"✅ Final stitched video saved at: {self.output_path}")




if __name__ == "__main__":
    jobs = VisiumJob("jobs.json","final_video.mp4")
    results = jobs.render_all()
    jobs.stitch_videos(results)
