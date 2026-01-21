"use client";

import ChatWindow from "@/components/ChatWindow";
import type { ChatMessage } from "@/lib/types";

interface ChatResultsProps {
  chatHistory: Record<string, ChatMessage[]>;
  selectedModels: string[];
  isLoading: boolean;
  modelErrors: Record<string, string>;
}

export default function ChatResults({
  chatHistory,
  selectedModels,
  isLoading,
  modelErrors,
}: ChatResultsProps) {
  if (selectedModels.length === 0) {
    return null;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {selectedModels.map((modelId) => (
        <ChatWindow
          key={modelId}
          modelId={modelId}
          messages={chatHistory[modelId] || []}
          isLoading={isLoading}
          error={modelErrors[modelId]}
        />
      ))}
    </div>
  );
}

