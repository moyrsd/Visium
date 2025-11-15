"use client";
import { ArrowRight, Plus } from "lucide-react";
import { useRouter } from "next/dist/client/components/navigation";
import React, { useState } from "react";

function Hero() {
  const [userInput, setUserInput] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleGenerate() {
    if (!userInput.trim() || loading) {
      return;
    }

    try {
      setLoading(true);

      const response = await fetch("http://localhost:8000/generate_video", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ topic: userInput }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate video");
      }

      const data = await response.json();

      router.push(`/videos/${data.video_id}/generating`);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col items-center mt-30 xl:mt-70 gap-2">
      <h2 className="font-bold text-4xl text-blue-100">
        {" "}
        Your concepts, made visible.
      </h2>
      <h2 className="text-gray-400 font-medium">
        Prompt to make 3Blue1Brown Style Videos
      </h2>
      <div className="p-3 border-4 rounded-xl max-w-2xl w-full mt-4 ">
        <div className="flex gap-3">
          <textarea
            placeholder="What do you want to animate ? "
            className="outline-none bg-transparent w-full h-32 max-h-52 resize-none"
            onChange={(event) => setUserInput(event.target.value)}
          ></textarea>
        </div>
        <div>
          <div className="flex flex-row justify-between">
            <div className="h-8 w-8 cursor-pointer rounded-2xl bg-transparent hover:bg-gray-900 flex justify-center items-center">
              <Plus className="h-6 w-6 text-gray-400 bg-transparent cursor-pointer" />
            </div>
            <ArrowRight
              onClick={() => {
                if (!loading) {
                  handleGenerate();
                }
              }}
              className={`
    p-2 h-8 w-9 rounded-md ml-auto transition
    ${loading ? "bg-gray-500 cursor-not-allowed opacity-60" : ""}
    ${!loading && userInput ? "bg-blue-500 cursor-pointer" : ""}
    ${!loading && !userInput ? "bg-blue-400 cursor-not-allowed opacity-60" : ""}
  `}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default Hero;
