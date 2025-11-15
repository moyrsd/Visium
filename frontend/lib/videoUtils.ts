import { ClipData, VideoData } from "@/types/video";

export const formatVideoData = (video: VideoData): VideoData => {
  return {
    id: video.id,
    title: video.title,
    description: video.description,
    url: video.url,
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
