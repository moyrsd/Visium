"use client";
import { ScrollArea } from "@/components/ui/scroll-area";
import SearchBar from "@/components/custom/SearchBar";
import VideoCard from "@/components/custom/VideoCard";
import { Separator } from "@/components/ui/separator";

interface VideoItem {
  title: string;
  description: string;
  duration: string;
  thumbnail?: string;
}

interface VideosPageProps {
  videos: VideoItem[];
}

export default function VideosPage({ videos }: VideosPageProps) {
  return (
    <div className="w-full flex justify-center px-6 py-6 h-[80vh]">
      <ScrollArea className="w-full max-w-7xl rounded-md border p-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {videos.map((v, idx) => (
            <VideoCard
              key={idx}
              title={v.title}
              description={v.description}
              duration={v.duration}
              thumbnail={v.thumbnail ?? "/file.svg"}
            />
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}