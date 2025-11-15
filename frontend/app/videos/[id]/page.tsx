import VideoSection from "@/components/video/VideoSection";
import { ClipData } from "@/types/video";

export default async function VideoPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  const res = await fetch(`http://127.0.0.1:8000/videos/${id}`, {
    cache: "no-store",
  });

  if (!res.ok) {
    return <div className="p-10 text-red-500">Failed to load video</div>;
  }

  const video = await res.json();

  const formatted = {
    id: video.id,
    title: video.title,
    description: video.description,
    url: video.final_video_path,
    clips: video.clips.map((c: ClipData) => ({
      id: c.id,
      index: c.index,
      clip_path: c.clip_path,
      thumbnail_path: c.thumbnail_path,
      duration: c.duration,
      narration_text: c.narration_text,
      code: c.code,
      prompt: c.prompt,
      visuals: c.visuals,
    })),
  };

  return <VideoSection video={formatted} />;
}
