export interface ClipData {
  id: string;
  index: number;
  clip_path: string;
  thumbnail_path: string;
  narration_text: string | null;
  code: string | null;
  prompt: string | null;
  duration: number | null;
  visuals: string | null;
}

export interface VideoData {
  id: string;
  title: string;
  description: string;
  url: string;
  clips: ClipData[];
}
