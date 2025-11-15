"use client";

import { useEffect, useRef } from "react";
import videojs from "video.js";
import "video.js/dist/video-js.css";
import type Player from "video.js/dist/types/player";

interface Props {
  src: string;
}

export default function VideoPlayer({ src }: Props) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const playerRef = useRef<Player | null>(null);

  useEffect(() => {
    if (!videoRef.current) return;

    const t = setTimeout(() => {
      if (!playerRef.current) {
        playerRef.current = videojs(videoRef.current as HTMLVideoElement, {
          controls: true,
          autoplay: false,
          preload: "auto",
          fluid: true,
          sources: [{ src, type: "video/mp4" }],
        });
      } else {
        playerRef.current.src({ src, type: "video/mp4" });
      }
    }, 80);

    return () => {
      clearTimeout(t);
      if (playerRef.current) {
        playerRef.current.dispose();
        playerRef.current = null;
      }
    };
  }, [src]);

  return (
    <div className="rounded-xl overflow-hidden border border-gray-700">
      <video
        ref={videoRef}
        className="video-js vjs-big-play-centered w-full h-full"
      ></video>
    </div>
  );
}
