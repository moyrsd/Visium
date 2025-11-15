"use client";

import Image from "next/image";
import React from "react";
import { usePathname, useRouter } from "next/navigation";
import { Button } from "../ui/button";

function Header() {
  const pathname = usePathname();
  const router = useRouter();

  const onVideosPage = pathname.startsWith("/videos");

  return (
    <div
      bg-background="true"
      className="
        fixed top-0 left-0 w-full
        z-50
        p-6 flex justify-between items-center
      "
    >
      <div className="flex gap-2">
        <Image src={"/logo3.png"} alt="Logo" width={40} height={40} />
        <h1 className="text-4xl font-bold text-blue-100">Visium</h1>
      </div>

      <div className="flex gap-5">
        {/* Replace Link with router.push */}
        {onVideosPage ? (
          <Button
            className="bg-blue-50 font-bold text-black"
            onClick={() => router.push("/")}
          >
            Generate Video
          </Button>
        ) : (
          <Button
            className="bg-blue-50 font-bold text-black"
            onClick={() => router.push("/videos")}
          >
            All Videos
          </Button>
        )}
      </div>
    </div>
  );
}

export default Header;
