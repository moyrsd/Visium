import { IconFolderCode } from "@tabler/icons-react";
import { ArrowUpRightIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Empty,
  EmptyContent,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty";

export function EmptyDemo({ className = "" }: { className?: string }) {
  return (
    <div
      className={`w-full h-full flex justify-center items-center ${className}`}
    >
      <Empty>
        <EmptyHeader>
          <EmptyMedia variant="icon">
            <IconFolderCode />
          </EmptyMedia>
          <EmptyTitle>No Videos Yet</EmptyTitle>
          <EmptyDescription>
            You haven&apos;t created any videos yet. Get started by creating
            your first video.
          </EmptyDescription>
        </EmptyHeader>
        <EmptyContent>
          <div className="flex gap-2 font-bold">
            <Button className="font-semibold ">Create Video</Button>
            <Button className="font-semibold " variant="outline">Browse Templates</Button>
          </div>
        </EmptyContent>
        {/* <Button
          variant="link"
          asChild
          className="text-muted-foreground"
          size="sm"
        >
          <a href="#">
            Learn More <ArrowUpRightIcon />
          </a>
        </Button> */}
      </Empty>{" "}
    </div>
  );
}
