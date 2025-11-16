"use client";
import VideoPlayer from "./VideoPlayer";
import ClipStrip from "./ClipStrip";
import { useEffect, useState } from "react";
import ClipModal from "./ClipModal";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "../ui/button";
import { ClipData, VideoData } from "@/types/video";
import { Skeleton } from "@/components/ui/skeleton";
import { formatVideoData } from "@/lib/videoUtils";

const POLLING_INTERVAL_MS = 3000;

export default function VideoSection({
  initialVideo,
}: {
  initialVideo: VideoData;
}) {
  const [video, setVideo] = useState<VideoData>(initialVideo);
  const [selectedClip, setSelectedClip] = useState<ClipData | null>(null);

  const [isProcessing, setIsProcessing] = useState<boolean>(
    !initialVideo.url || initialVideo.status === "PENDING"
  );

  useEffect(() => {
    if (!isProcessing) return;

    console.log("Starting polling for video data...");

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`http://127.0.0.1:8000/videos/${video.id}`, {
          cache: "no-store",
        });

        if (!res.ok) {
          console.error("Polling fetch failed");
          return;
        }

        const rawVideo = await res.json();

        // Check if the backend has populated the final video path
        if (rawVideo.status === "READY") {
          console.log("Video is ready!");
          clearInterval(interval);
          setVideo(formatVideoData(rawVideo));
          setIsProcessing(false);
        } else if (rawVideo.status === "PENDING") {
          setIsProcessing(true);
          console.log("Video still processing...");
        }
      } catch (error) {
        console.error("Error during polling:", error);
      }
    }, POLLING_INTERVAL_MS);

    return () => clearInterval(interval);
  }, [isProcessing, video.id]);

  const handleRender = async () => {
    setIsProcessing(true);
    try {
      const res = await fetch(
        `http://127.0.0.1:8000/videos/${video.id}/render`,
        {
          method: "POST",
        }
      );

      if (!res.ok) {
        throw new Error("Render request failed");
      }

      console.log("Render request sent, starting polling...");
    } catch (error) {
      console.error("Render failed:", error);
      setIsProcessing(false);
    }
  };

  const handleDownload = async () => {
    if (isProcessing || !video.url) return;

    try {
      const res = await fetch(`http://127.0.0.1:8000/${video.url}`);
      const blob = await res.blob();

      const objectUrl = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = objectUrl;
      a.download = `${video.title.replace(/ /g, "_") || "video"}.mp4`;

      document.body.appendChild(a);
      a.click();

      document.body.removeChild(a);
      URL.revokeObjectURL(objectUrl);
    } catch (error) {
      console.error("Download failed:", error);
    }
  };

  return (
    <div className="w-full flex justify-center px-8 py-10 pt-30">
      <div className="w-full max-w-7xl">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          {isProcessing ? (
            <Skeleton className="w-full aspect-video rounded-lg" />
          ) : (
            <VideoPlayer src={`http://127.0.0.1:8000/${video.url}`} />
          )}

          <div className="flex flex-col ">
            <h1 className="text-2xl font-semibold text-gray-100">
              {video.title}
            </h1>

            <p className="text-gray-400 mt-2">{video.description}</p>

            <div className="flex gap-4 mt-6">
              <Button
                className="px-5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white"
                onClick={handleDownload}
                disabled={isProcessing || !video.url}
              >
                Download Full Video
              </Button>
              <Button
                className="px-5 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-gray-200"
                onClick={handleRender}
                disabled={isProcessing}
              >
                {isProcessing ? "Rendering..." : "Render Again"}
              </Button>
            </div>
            <div className="flex gap-4 mt-6">
              <Select>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="Music" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectLabel>Sort By</SelectLabel>
                    <SelectItem value="Music 1">Music 1 </SelectItem>
                    <SelectItem value="Music 2">Music 2</SelectItem>
                    <SelectItem value="Music 3">Music 3</SelectItem>
                    <SelectItem value="Music 4">Music 4</SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
              <Select>
                <SelectTrigger className="w-[200px]">
                  <SelectValue placeholder="Fade" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectLabel>Sort By</SelectLabel>
                    <SelectItem value="No fade">No fade</SelectItem>
                    <SelectItem value="Fade 1">Fade 1</SelectItem>
                    <SelectItem value="Fade 2">Fade 2</SelectItem>
                    <SelectItem value="Fade 3">Fade 3</SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        {isProcessing ? (
          <>
            <Skeleton className="h-6 w-32 mt-5 mb-4" />
            <Skeleton className="h-32 w-full rounded-lg" />
          </>
        ) : (
          <>
            <h3 className="text-gray-100 text-lg font-medium mt-5 mb-4">
              Edit Clips
            </h3>
            <ClipStrip clips={video.clips} onOpen={setSelectedClip} />
          </>
        )}

        {selectedClip && (
          <ClipModal
            clip={selectedClip}
            onClose={() => setSelectedClip(null)}
          />
        )}
      </div>
    </div>
  );
}
