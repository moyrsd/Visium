export const revalidate = 5;

import VideosPage from "@/components/custom/VideosPage";
import { EmptyDemo } from "@/components/custom/Empty";
import SearchBar from "@/components/custom/SearchBar";
import { VideoData } from "@/types/video";

export default async function Videos() {
  const res = await fetch("http://127.0.0.1:8000/videos", {
    cache: "no-store",
    next: { revalidate: 5 },
  });

  if (!res.ok) {
    return (
      <>
        <SearchBar />
        <div className="mt-10 text-red-500 p-10">Failed to load videos</div>
      </>
    );
  }

  const data = await res.json();

  const videos = data.map((v: VideoData) => ({
    id: v.id,
    title: v.title,
    description: v.description,
    thumbnail:
      v.status === "READY"
        ? `http://127.0.0.1:8000/${v.thumbnail_path}`
        : "/Progress Bar.gif",
  }));

  return (
    <>
      <SearchBar />
      <div className="mt-10">
        {videos.length > 0 ? (
          <VideosPage videos={videos} />
        ) : (
          <EmptyDemo className="min-h-[70vh]" />
        )}
      </div>
    </>
  );
}
