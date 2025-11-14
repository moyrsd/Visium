import VideoSection from "@/components/video/VideoSection";

export default async function VideoPage({
  params,
}: {
  params: { id: string };
}) {
  const id = params.id;

  // Fetch data server side (mock for now)
  const video = {
    id,
    title: "Futuristic Cityscape – Blue Style",
    description: "A sweeping shot through towering plated structures...",
    url: "https://www.w3schools.com/html/mov_bbb.mp4",
    clips: [
      { id: "c1", thumb: "/clip1.jpg", duration: "5s" },
      { id: "c2", thumb: "/clip2.jpg", duration: "4s" },
      { id: "c3", thumb: "/clip3.jpg", duration: "6s" },
      { id: "c4", thumb: "/clip4.jpg", duration: "8s" },
      { id: "c5", thumb: "/clip4.jpg", duration: "8s" },
      { id: "c6", thumb: "/clip4.jpg", duration: "8s" },
      { id: "c7", thumb: "/clip4.jpg", duration: "8s" },
      { id: "c8", thumb: "/clip4.jpg", duration: "8s" },
      { id: "c9", thumb: "/clip4.jpg", duration: "8s" },
      { id: "c10", thumb: "/clip4.jpg", duration: "8s" },
      { id: "c11", thumb: "/clip4.jpg", duration: "8s" },
      { id: "c12", thumb: "/clip4.jpg", duration: "8s" },
    ],
  };

  return <VideoSection video={video} />;
}
