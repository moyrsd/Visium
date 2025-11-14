"use client";

import Image from "next/image";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import Editor from "@monaco-editor/react";

interface ClipData {
  id: string;
  thumb: string;
  duration: string;
}

export default function ClipModal({
  clip,
  onClose,
}: {
  clip: ClipData;
  onClose: () => void;
}) {
  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent
        className="
          sm:max-w-4xl
          bg-card
          text-card-foreground
          border border-border
          rounded-xl
          p-6
          overflow-hidden
        "
      >
        <DialogHeader>
          <DialogTitle>Edit Clip</DialogTitle>
        </DialogHeader>

        <div className="h-[65vh] overflow-hidden flex flex-col gap-6">
          {/* Thumbnail */}
          <Image
            src={clip.thumb}
            width={800}
            height={300}
            alt="clip"
            className="rounded-lg mx-auto h-56"
          />

          {/* Tabs */}
          <Tabs defaultValue="prompt" className="w-full">
            <TabsList className="grid grid-cols-3 bg-muted rounded-lg mb-4">
              <TabsTrigger value="prompt">Prompt</TabsTrigger>
              <TabsTrigger value="code">Code</TabsTrigger>
              <TabsTrigger value="narration">Narration</TabsTrigger>
            </TabsList>

            {/* Prompt */}
            <TabsContent value="prompt">
              <textarea
                className="
                  w-full
                  h-40
                  bg-input
                  text-foreground
                  border border-border
                  rounded-lg
                  p-3
                  resize-none
                "
                placeholder="Describe how to edit this clip..."
              />
            </TabsContent>

            {/* Code Editor */}
            <TabsContent value="code">
              <div className="h-80 border border-border rounded-lg overflow-hidden">
                <Editor
                  height="100%"
                  defaultLanguage="python"
                  theme="vs-dark"
                  defaultValue={`# Write your manim code here\nfrom manim import *\n\nclass MyScene(Scene):\n    def construct(self):\n        circle = Circle()\n        self.play(Create(circle))`}
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    lineNumbers: "on",
                    scrollBeyondLastLine: true,
                    tabSize: 4,
                    insertSpaces: true,
                    detectIndentation: false,
                    autoIndent: "full",
                    formatOnType: true,
                    formatOnPaste: true,
                  }}
                />
              </div>
            </TabsContent>

            {/* Narration */}
            <TabsContent value="narration">
              <textarea
                className="
                  w-full
                  h-40
                  bg-input
                  text-foreground
                  border border-border
                  rounded-lg
                  p-3
                  resize-none
                "
                placeholder="What should the narrator say in this clip?"
              />
            </TabsContent>
          </Tabs>
        </div>

        {/* Buttons */}
        <div className="flex justify-end gap-3 pt-4 border-t border-border">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-muted text-muted-foreground hover:bg-muted/70"
          >
            Cancel
          </button>

          <button className="px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/80">
            Apply
          </button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
