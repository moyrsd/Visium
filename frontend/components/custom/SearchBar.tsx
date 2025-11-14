"use client";
import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";
import FilterBar from "./FilterBar";
import { Button } from "../ui/button";

export default function SearchBar() {
  return (
    <div
      className="w-full max-w-4xl mx-auto mt-14 flex flex-row items-center gap-3 
     sticky top-20 bg-background z-50 py-2 rounded-3xl h-10"
    >
      <div className="relative flex-1 flex items-center bg-background">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 h-5 w-5" />
        <Input
          type="text"
          placeholder="Search for videos..."
          className="w-full bg-background border border-gray-700 rounded-xl py-3 pl-10 pr-4 text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>
      <div>
        <Button variant="outline" bg-background>
          Search
        </Button>
      </div>
      <div>
        <FilterBar bg-background />
      </div>
    </div>
  );
}
