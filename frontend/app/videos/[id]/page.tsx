import VideoSection from "@/components/video/VideoSection";
import { formatVideoData } from "@/lib/videoUtils"; // Import the helper

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
    return <div className="p-10 text-red-500">Failed to load video data</div>;
  }

  const rawVideo = await res.json();
  const formattedVideo = formatVideoData(rawVideo);

  return <VideoSection initialVideo={formattedVideo} />;
}
