"use client";

import React from "react";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

export default function FilterBar() {
  return (
    <Select>
      <SelectTrigger className="w-[180px]">
        <SelectValue placeholder="Sort By" />
      </SelectTrigger>
      <SelectContent>
        <SelectGroup>
          <SelectLabel>Sort By</SelectLabel>
          <SelectItem value="Latest">Latest</SelectItem>
          <SelectItem value="Oldest">Oldest</SelectItem>
          <SelectItem value="Longest">Longest</SelectItem>
          <SelectItem value="Bookmarks">Bookmarks</SelectItem>
        </SelectGroup>
      </SelectContent>
    </Select>
  );
}
