"use client";

import { useEffect, useRef } from "react";
import type { ChatMessage } from "@/lib/types";

interface ChatWindowProps {
  modelId: string;
  messages: ChatMessage[];
  isLoading?: boolean;
  error?: string;
}

export default function ChatWindow({
  modelId,
  messages,
  isLoading,
  error,
}: ChatWindowProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="flex flex-col h-full bg-gray-50">
      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="space-y-4 max-w-4xl mx-auto">
          {messages.length === 0 ? (
            <div className="text-gray-500 text-sm text-center py-12">
              No messages yet. Start a conversation!
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[75%] rounded-3xl px-4 py-3 ${
                    msg.role === "user"
                      ? "bg-blue-500 text-white"
                      : "bg-white text-slate-900 shadow-sm"
                  }`}
                >
                  <div className="whitespace-pre-wrap leading-relaxed text-sm">
                    {msg.content}
                  </div>
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white text-slate-900 rounded-3xl px-4 py-3 shadow-sm">
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-slate-900"></div>
                  <span className="text-sm">Thinking...</span>
                </div>
              </div>
            </div>
          )}
          {error && (
            <div className="flex justify-start">
              <div className="bg-red-50 border-2 border-red-300 text-red-900 rounded-3xl px-4 py-3 max-w-[75%] shadow-sm">
                <div className="flex items-start gap-2">
                  <svg
                    className="w-5 h-5 text-red-600 shrink-0 mt-0.5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  <div className="flex-1">
                    <div className="font-semibold text-xs text-red-700 mb-1">
                      Error
                    </div>
                    <div className="text-sm whitespace-pre-wrap leading-relaxed">
                      {error}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>
    </div>
  );
}

