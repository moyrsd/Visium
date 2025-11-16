"use client";

import Image from "next/image";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";
import { ClipData } from "@/types/video";

export default function ClipStrip({
  clips,
  onOpen,
}: {
  clips: ClipData[];
  onOpen: (clip: ClipData) => void;
}) {
  return (
    <ScrollArea className="w-full rounded-md whitespace-nowrap">
      <div className="flex w-max space-x-4 p-2">
        {clips.map((clip) => {
          const thumbnailSrc =
            clip.status === "PENDING"
              ? "/inprogress.gif"
              : `http://127.0.0.1:8000/${clip.thumbnail_path}`;

          return (
            <figure
              key={clip.id}
              className="shrink-0 cursor-pointer"
              onClick={() => onOpen(clip)}
            >
              <div className="overflow-hidden rounded-md border border-gray-700 hover:border-gray-500 transition">
                <Image
                  src={thumbnailSrc}
                  alt={clip.prompt || "clip"}
                  width={180}
                  height={120}
                  className="aspect-video h-24 w-40 object-cover"
                />
              </div>

              <figcaption className="text-gray-400 pt-1 text-xs">
                {clip.duration}s
              </figcaption>
            </figure>
          );
        })}
      </div>
      <ScrollBar orientation="horizontal" />
    </ScrollArea>
  );
}
