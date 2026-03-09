"use client";

import ModelSelector from "@/components/ModelSelector";
import OllamaDownload from "@/components/OllamaDownload";
import OpenAISettings from "@/components/OpenAISettings";
import UserSection from "@/components/UserSection";
import { API_BASE_URL } from "@/lib/api";
import type { ModelInfo } from "@/lib/types";

interface SidebarProps {
  models: ModelInfo[];
  selectedModels: string[];
  setSelectedModels: (selected: string[]) => void;
  onValidated: () => void;
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

export default function Sidebar({
  models,
  selectedModels,
  setSelectedModels,
  onValidated,
  isOpen,
  setIsOpen,
}: SidebarProps) {

  return (
    <>
      {/* Toggle Button (visible when sidebar is closed) */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed left-0 z-20 bg-white border-r border-t border-b border-gray-200 rounded-r-lg px-2 py-4 shadow-sm hover:bg-gray-50 transition-colors"
          style={{ top: "50%", transform: "translateY(-50%)" }}
          aria-label="Open sidebar"
        >
          <svg
            className="w-5 h-5 text-gray-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </button>
      )}

      {/* Sidebar */}
      <div
        className={`${
          isOpen ? "translate-x-0" : "-translate-x-full"
        } fixed left-0 w-80 bg-white border-r border-gray-200 z-10 transition-transform duration-300 ease-in-out overflow-y-auto`}
        style={{ top: "73px", bottom: "88px" }}
      >
        <div className="p-4 space-y-6">
          {/* Header with close button */}
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900">Settings</h2>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 rounded-lg hover:bg-gray-100 transition-colors"
              aria-label="Close sidebar"
            >
              <svg
                className="w-5 h-5 text-gray-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {/* User Section */}
          <div>
            <UserSection />
          </div>

          {/* Model Selection */}
          <div>
            <ModelSelector
              models={models}
              selected={selectedModels}
              setSelected={setSelectedModels}
            />
          </div>

          {/* Ollama Download (only show if Ollama models exist) */}
          {models.some((m) => m.provider === "ollama") && (
            <div>
              <OllamaDownload onModelAdded={onValidated} />
            </div>
          )}

          {/* Provider Settings */}
          <div>
            <OpenAISettings onValidated={onValidated} />
          </div>

          {/* Debug Info */}
          {(process.env.NODE_ENV !== 'production' || 
            process.env.NEXT_PUBLIC_SHOW_DEBUG === '1') && (
            <div className="pt-4 border-t border-gray-200">
              <div className="text-xs text-gray-500 space-y-1">
                <div className="font-medium text-gray-700">Debug Info</div>
                <div>API Base URL: {API_BASE_URL}</div>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

