"use client";

import { useRouter } from "next/navigation";
import { ScrollArea } from "@/components/ui/scroll-area";
import VideoCard from "@/components/custom/VideoCard";

interface VideoItem {
  id: string;
  title: string;
  description: string;
  duration: string;
  thumbnail?: string;
}

interface VideosPageProps {
  videos: VideoItem[];
}

export default function VideosPage({ videos }: VideosPageProps) {
  const router = useRouter();

  return (
    <div className="w-full flex justify-center px-6 py-6 h-[80vh]">
      <ScrollArea className="w-full max-w-7xl rounded-md border p-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {videos.map((v) => (
            <div
              key={v.id}
              onClick={() => router.push(`/videos/${v.id}`)}
              className="cursor-pointer"
            >
              <VideoCard
                title={v.title}
                description={v.description}
                thumbnail={v.thumbnail ?? "/file.svg"}
              />
            </div>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
