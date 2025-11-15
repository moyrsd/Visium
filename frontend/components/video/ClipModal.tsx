"use client";
import VideoPlayer from "./VideoPlayer";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import Editor from "@monaco-editor/react";
import { ClipData } from "@/types/video";

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

        <div className="h-[65vh] overflow-hidden flex flex-col gap-4 items-center">
          {/* Thumbnail */}
          <div className="h-50 w-85">
            <VideoPlayer
              key={clip.id}
              src={`http://127.0.0.1:8000/${clip.clip_path}`}
            />
          </div>

          {/* Tabs */}
          <Tabs defaultValue="prompt" className="w-full ">
            <div className="flex justify-center" >
              <TabsList className="grid grid-cols-4 bg-muted rounded-lg mb-4 width-90">
                <TabsTrigger value="prompt">Prompt</TabsTrigger>
                <TabsTrigger value="code">Code</TabsTrigger>
                <TabsTrigger value="narration">Narration</TabsTrigger>
                <TabsTrigger value="visuals">Visuals</TabsTrigger>
              </TabsList>
            </div>

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
                placeholder={`${clip.prompt}`}
              />
            </TabsContent>

            {/* Code Editor */}
            <TabsContent value="code">
              <div className="h-80 border border-border rounded-lg overflow-hidden">
                <Editor
                  height="100%"
                  defaultLanguage="python"
                  theme="vs-dark"
                  defaultValue={`${clip.code}`}
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
                placeholder={`${clip.narration_text}`}
              />
            </TabsContent>

            {/* Visuals */}
            <TabsContent value="visuals">
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
                placeholder={`${clip.visuals}`}
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
