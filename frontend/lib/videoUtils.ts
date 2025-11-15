import { ClipData, VideoData } from "@/types/video";

interface ApiVideo {
  id: string;
  title: string;
  description: string;
  status: "PENDING" | "READY" | "ERROR";
  final_video_path: string | null;
  thumbnail_path: string;
  clips: ClipData[];
}

export const formatVideoData = (video: ApiVideo): VideoData => {
  return {
    id: video.id,
    title: video.title,
    status: video.status,
    description: video.description,
    url: video.final_video_path,
    thumbnail_path: video.thumbnail_path,
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
};
