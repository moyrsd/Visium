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

    if (!playerRef.current) {
      playerRef.current = videojs(videoRef.current, {
        controls: true,
        autoplay: false,
        preload: "auto",
        fluid: true,
        responsiveness: true,
        sources: [
          {
            src,
            type: "video/mp4",
          },
        ],
      });
    } else {
      // Update source without reinitializing
      playerRef.current.src({ src, type: "video/mp4" });
    }

    return () => {
      if (playerRef.current) {
        playerRef.current.dispose();
        playerRef.current = null;
      }
    };
  }, [src]);

  return (
    <div className="rounded-xl overflow-hidden border border-gray-700">
      <video ref={videoRef} className="video-js vjs-big-play-centered"></video>
    </div>
  );
}
