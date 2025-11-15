"use client";
import VideoPlayer from "./VideoPlayer";
import ClipStrip from "./ClipStrip";
import { useState } from "react";
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

export default function VideoSection({ video }: { video: VideoData }) {
  const [selectedClip, setSelectedClip] = useState<ClipData | null>(null);

  return (
    <div className="w-full flex justify-center px-8 py-10 pt-20">
      <div className="w-full max-w-7xl">
        {/* Top Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          <VideoPlayer src={`http://127.0.0.1:8000/${video.url}`} />

          <div className="flex flex-col ">
            <h1 className="text-2xl font-semibold text-gray-100">
              {video.title}
            </h1>
            <p className="text-gray-400 mt-2">{video.description}</p>

            <div className="flex gap-4 mt-6">
              <Button className="px-5 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white">
                {" "}
                Download Full Video
              </Button>
              <Button className="px-5 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-gray-200">
                {" "}
                Render
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

        {/* Clip Strip */}
        <h3 className="text-gray-100 text-lg font-medium mt-5 mb-4">
          Edit Clips
        </h3>
        <ClipStrip clips={video.clips} onOpen={setSelectedClip} />

        {/* Modal */}
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
