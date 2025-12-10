"use client";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface PromptInputProps {
  prompt: string;
  setPrompt: (prompt: string) => void;
  onSubmit: () => void;
  isLoading?: boolean;
}

export default function PromptInput({
  prompt,
  setPrompt,
  onSubmit,
  isLoading = false,
}: PromptInputProps) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (prompt.trim() && !isLoading) {
      onSubmit();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full space-y-4">
      <Textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Enter your prompt here..."
        className="min-h-[120px] rounded-2xl border-gray-300 focus:ring-2 focus:ring-black transition-all resize-none"
        disabled={isLoading}
      />
      <Button
        type="submit"
        disabled={!prompt.trim() || isLoading}
        className="w-full rounded-2xl bg-black text-white hover:bg-gray-800 transition-all shadow-sm hover:shadow-md focus:ring-2 focus:ring-black"
      >
        {isLoading ? "Running Comparison..." : "Run Comparison"}
      </Button>
    </form>
  );
}

