"use client";

import VideosPage from "@/components/custom/VideosPage";
import { EmptyDemo } from "@/components/custom/Empty";
import React from "react";
import SearchBar from "@/components/custom/SearchBar";

export default function Videos() {
  const videos = [
    {
      title: "Futuristic Cityscape",
      description: "A cinematic flythrough of a neon-lit megacity.",
      duration: "0:45",
      thumbnail: "/file.svg",
    },
    {
      title: "Quantum Particles Explained",
      description: "A simple visualization of probability waves.",
      duration: "1:12",
      thumbnail: "/globe.svg",
    },
    {
      title: "Desert Ruins",
      description: "Camera tracking through ancient abandoned temples.",
      duration: "0:58",
      thumbnail: "/window.svg",
    },
    {
      title: "Blue Style Vector Fields",
      description: "Divergence and curl explained visually.",
      duration: "0:39",
      thumbnail: "/next.svg",
    },
    {
      title: "Brown Style Fractal Zoom",
      description: "Exploring recursive geometry with animation.",
      duration: "1:03",
      thumbnail: "/vercel.svg",
    },
    {
      title: "Linear Algebra Transformations",
      description: "Matrix effects visualized with moving grids.",
      duration: "0:54",
      thumbnail: "/logo1.png",
    },
    {
      title: "Neural Network Basics",
      description: "From perceptrons to activations in 60 seconds.",
      duration: "0:47",
      thumbnail: "/logo3.png",
    },
    {
      title: "Fourier Series Animation",
      description: "Drawing complex curves using rotating vectors.",
      duration: "2:01",
      thumbnail: "/file.svg",
    },
    {
      title: "Futuristic Cityscape",
      description: "A cinematic flythrough of a neon-lit megacity.",
      duration: "0:45",
      thumbnail: "/file.svg",
    },
    {
      title: "Quantum Particles Explained",
      description: "A simple visualization of probability waves.",
      duration: "1:12",
      thumbnail: "/globe.svg",
    },
    {
      title: "Desert Ruins",
      description: "Camera tracking through ancient abandoned temples.",
      duration: "0:58",
      thumbnail: "/window.svg",
    },
    {
      title: "Blue Style Vector Fields",
      description: "Divergence and curl explained visually.",
      duration: "0:39",
      thumbnail: "/next.svg",
    },
    {
      title: "Brown Style Fractal Zoom",
      description: "Exploring recursive geometry with animation.",
      duration: "1:03",
      thumbnail: "/vercel.svg",
    },
    {
      title: "Linear Algebra Transformations",
      description: "Matrix effects visualized with moving grids.",
      duration: "0:54",
      thumbnail: "/logo1.png",
    },
    {
      title: "Neural Network Basics",
      description: "From perceptrons to activations in 60 seconds.",
      duration: "0:47",
      thumbnail: "/logo3.png",
    },
    {
      title: "Fourier Series Animation",
      description: "Drawing complex curves using rotating vectors.",
      duration: "2:01",
      thumbnail: "/file.svg",
    },
  ];

  return (
    <>
      <SearchBar />
      <div className="mt-10 ">
        {videos.length > 0 ? (
          <VideosPage videos={videos} />
        ) : (
          <EmptyDemo className="min-h-[70vh]" />
        )}
      </div>
    </>
  );
}
