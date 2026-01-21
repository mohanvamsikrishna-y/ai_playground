"use client";

import ChatWindow from "@/components/ChatWindow";
import type { ChatMessage } from "@/lib/types";

interface ChatTabsProps {
  conversations: Record<string, ChatMessage[]>;
  selectedModels: string[];
  activeTab: string | null;
  setActiveTab: (modelId: string) => void;
  isLoading: boolean;
  modelErrors: Record<string, string>;
}

export default function ChatTabs({
  conversations,
  selectedModels,
  activeTab,
  setActiveTab,
  isLoading,
  modelErrors,
}: ChatTabsProps) {
  if (selectedModels.length === 0) {
    return (
      <div className="flex items-center justify-center h-full text-gray-500">
        <p>Select at least one model to start chatting</p>
      </div>
    );
  }

  // Fallback to first model if activeTab is not set
  const displayTab = activeTab || selectedModels[0];

  return (
    <div className="flex flex-col h-full bg-white">
      {/* Tab Bar */}
      <div className="flex border-b border-gray-200 bg-white">
        {selectedModels.map((modelId) => (
          <button
            key={modelId}
            onClick={() => setActiveTab(modelId)}
            className={`px-6 py-3 text-sm font-medium transition-colors border-b-2 ${
              displayTab === modelId
                ? "border-black text-black"
                : "border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300"
            }`}
          >
            {modelId}
          </button>
        ))}
      </div>

      {/* Active Tab Content */}
      {displayTab && (
        <div className="flex-1 overflow-hidden">
          <ChatWindow
            modelId={displayTab}
            messages={conversations[displayTab] || []}
            isLoading={isLoading}
            error={modelErrors[displayTab]}
          />
        </div>
      )}
    </div>
  );
}

