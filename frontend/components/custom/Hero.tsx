"use client";
import { ArrowRight, Plus } from "lucide-react";
import React, { useState } from "react";

function Hero() {
  const [userInput, setUserInput] = useState<string>("");
  return (
    <div className="flex flex-col items-center mt-30 xl:mt-35 gap-2">
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
              className={`
      p-2 h-8 w-9  rounded-md cursor-pointer ml-auto
      ${userInput ? "bg-blue-500" : "bg-blue-400"}
    `}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default Hero;
