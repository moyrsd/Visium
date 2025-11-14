"use client";

import { Play } from "lucide-react";
import Image from "next/image";

export default function VideoCard({
  title,
  description,
  duration,
  thumbnail,
}: {
  title: string;
  description: string;
  duration: string;
  thumbnail?: string;
}) {
  return (
    <div className="rounded-xl bg-black/20 border border-gray-800 p-3 hover:bg-black/30 transition cursor-pointer">
      <div className="relative w-full h-40 rounded-lg overflow-hidden mb-3">
        <Image
          src={thumbnail || "/file.svg"}
          height={160}
          width={640}
          className="w-full h-full object-cover opacity-80 width-[640px] max-width: 100vw 33vw"
          alt={title}
        ></Image>

        <Play className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-white h-10 w-10 opacity-70" />
        <div className="absolute bottom-2 right-2 bg-black/60 px-2 py-1 text-xs rounded text-gray-200">
          {duration}
        </div>
      </div>

      <h3 className="font-semibold text-gray-200 text-sm">{title}</h3>
      <p className="text-gray-500 text-xs">{description}</p>
    </div>
  );
}
