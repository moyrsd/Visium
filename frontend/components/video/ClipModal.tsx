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
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function ClipModal({
  clip,
  onClose,
}: {
  clip: ClipData;
  onClose: () => void;
}) {
  const router = useRouter();

  const [prompt, setPrompt] = useState(clip.prompt || "");
  const [code, setCode] = useState(clip.code || "");
  const [narration, setNarration] = useState(clip.narration_text || "");
  const [visuals, setVisuals] = useState(clip.visuals || "");
  const [isApplying, setIsApplying] = useState(false);

  const handleApply = async () => {
    setIsApplying(true);
    try {
      const params = new URLSearchParams();
      params.append("prompt", prompt);
      params.append("code", code);
      params.append("narration_text", narration);
      params.append("visuals", visuals);

      const res = await fetch(`http://127.0.0.1:8000/modify_clip/${clip.id}`, {
        method: "POST",
        body: params,
      });

      if (!res.ok) {
        const errorData = await res.json();
        console.error("API Error:", errorData);
        throw new Error("Failed to modify clip");
      }

      onClose();
      // Task : implement a better state update instead of full reload
      window.location.reload();
    } catch (error) {
      console.error("Error applying changes:", error);
      setIsApplying(false);
    }
  };

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-4xl bg-card text-card-foreground border border-border rounded-xl p-6 overflow-hidden">
        <DialogHeader>
          <DialogTitle>Edit Clip</DialogTitle>
        </DialogHeader>

        <div className="h-[65vh] overflow-hidden flex flex-col gap-4 items-center">
          <div className="h-50 w-85">
            <VideoPlayer
              key={clip.id}
              src={`http://127.0.0.1:8000/${clip.clip_path}`}
            />
          </div>

          <Tabs defaultValue="prompt" className="w-full ">
            <div className="flex justify-center">
              <TabsList className="grid grid-cols-4 bg-muted rounded-lg mb-4 width-90">
                <TabsTrigger value="prompt">Prompt</TabsTrigger>
                <TabsTrigger value="code">Code</TabsTrigger>
                <TabsTrigger value="narration">Narration</TabsTrigger>
                <TabsTrigger value="visuals">Visuals</TabsTrigger>
              </TabsList>
            </div>

            <TabsContent value="prompt">
              <textarea
                className="w-full h-40 bg-input text-foreground border border-border rounded-lg p-3 resize-none"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
              />
            </TabsContent>

            <TabsContent value="code">
              <div className="h-80 border border-border rounded-lg overflow-hidden">
                <Editor
                  height="100%"
                  defaultLanguage="python"
                  theme="vs-dark"
                  value={code}
                  onChange={(value) => setCode(value || "")}
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    lineNumbers: "on",
                  }}
                />
              </div>
            </TabsContent>

            <TabsContent value="narration">
              <textarea
                className="w-full h-40 bg-input text-foreground border border-border rounded-lg p-3 resize-none"
                value={narration}
                onChange={(e) => setNarration(e.target.value)}
              />
            </TabsContent>

            <TabsContent value="visuals">
              <textarea
                className="w-full h-40 bg-input text-foreground border border-border rounded-lg p-3 resize-none"
                value={visuals}
                onChange={(e) => setVisuals(e.target.value)}
              />
            </TabsContent>
          </Tabs>
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t border-border">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-muted text-muted-foreground hover:bg-muted/70"
            disabled={isApplying}
          >
            Cancel
          </button>

          <button
            className="px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/80"
            onClick={handleApply}
            disabled={isApplying}
          >
            {isApplying ? "Applying..." : "Apply"}
          </button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
