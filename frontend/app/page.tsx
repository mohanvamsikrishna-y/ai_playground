"use client";

import { useEffect, useState } from "react";
import Header from "@/components/Header";
import ChatInput from "@/components/ChatInput";
import Sidebar from "@/components/Sidebar";
import ChatTabs from "@/components/ChatTabs";
import { getModels, compareModels } from "@/lib/api";
import type { ChatMessage, ModelInfo } from "@/lib/types";

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [conversations, setConversations] = useState<
    Record<string, ChatMessage[]>
  >({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [modelErrors, setModelErrors] = useState<Record<string, string>>({});
  const [activeTab, setActiveTab] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const refetchModels = async () => {
    try {
      const fetchedModels = await getModels();
      setModels(fetchedModels);
      // Preserve selection when possible; otherwise default to first model.
      if (fetchedModels.length === 0) {
        setSelectedModels([]);
        return;
      }
      if (selectedModels.length === 0) {
        setSelectedModels([fetchedModels[0].id]);
        return;
      }
      const availableIds = new Set(fetchedModels.map((m) => m.id));
      const stillValid = selectedModels.filter((id) => availableIds.has(id));
      if (stillValid.length > 0) {
        setSelectedModels(stillValid);
        // Update active tab if current one is no longer available
        if (activeTab && !availableIds.has(activeTab)) {
          setActiveTab(stillValid[0]);
        }
      } else {
        setSelectedModels([fetchedModels[0].id]);
        setActiveTab(fetchedModels[0].id);
      }
    } catch (err) {
      setError("Failed to load models. Make sure the backend is running.");
      console.error("Error fetching models:", err);
    }
  };

  // Fetch models on mount
  useEffect(() => {
    void refetchModels();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Set active tab when models are selected
  useEffect(() => {
    if (selectedModels.length > 0 && !activeTab) {
      setActiveTab(selectedModels[0]);
    } else if (selectedModels.length > 0 && activeTab && !selectedModels.includes(activeTab)) {
      setActiveTab(selectedModels[0]);
    }
  }, [selectedModels, activeTab]);

  const handleSend = async () => {
    if (!prompt.trim() || selectedModels.length === 0) {
      return;
    }

    setIsLoading(true);
    setError(null);
    setModelErrors({}); // Clear previous model errors

    // Create user message
    const userMessage: ChatMessage = {
      role: "user",
      content: prompt.trim(),
    };

    // Update conversations with user message for each selected model
    const updatedConversations: Record<string, ChatMessage[]> = {
      ...conversations,
    };
    for (const modelId of selectedModels) {
      if (!updatedConversations[modelId]) {
        updatedConversations[modelId] = [];
      }
      updatedConversations[modelId] = [
        ...updatedConversations[modelId],
        userMessage,
      ];
    }
    setConversations(updatedConversations);

    // Clear input immediately for better UX
    const currentPrompt = prompt;
    setPrompt("");

    // Build conversations dict with only selected models
    const conversationsToSend: Record<string, ChatMessage[]> = {};
    for (const modelId of selectedModels) {
      conversationsToSend[modelId] = updatedConversations[modelId];
    }

    try {
      // Send all conversations to /compare endpoint
      const response = await compareModels({
        conversations: conversationsToSend,
      });

      // Update conversations with assistant responses
      const finalConversations: Record<string, ChatMessage[]> = {
        ...updatedConversations,
      };
      const newModelErrors: Record<string, string> = {};

      for (const modelId of selectedModels) {
        if (response.results[modelId]) {
          // Success: append assistant message
          finalConversations[modelId] = [
            ...finalConversations[modelId],
            response.results[modelId],
          ];
        } else {
          // Model failed - use error message from backend if available
          const errorMessage =
            response.errors?.[modelId] || "No response received";
          newModelErrors[modelId] = errorMessage;
          // Revert user message for failed model
          if (finalConversations[modelId]) {
            finalConversations[modelId] = finalConversations[modelId].slice(
              0,
              -1
            );
          }
        }
      }

      setConversations(finalConversations);
      setModelErrors(newModelErrors);

      // Check if all models failed
      const successCount = Object.keys(response.results).length;
      if (successCount === 0 && selectedModels.length > 0) {
        setError("All models failed. Please check your configuration.");
      } else {
        setError(null);
      }
    } catch (err) {
      // Handle request-level errors
      const errorMessage =
        err instanceof Error
          ? err.message
          : "Failed to send message. Please try again.";

      // Revert user messages for all models on request failure
      const revertedConversations: Record<string, ChatMessage[]> = {
        ...updatedConversations,
      };
      for (const modelId of selectedModels) {
        if (revertedConversations[modelId]) {
          revertedConversations[modelId] = revertedConversations[modelId].slice(
            0,
            -1
          );
        }
      }

      const errorState: Record<string, string> = {};
      for (const modelId of selectedModels) {
        errorState[modelId] = errorMessage;
      }
      setConversations(revertedConversations);
      setModelErrors(errorState);
      setError(errorMessage);
      // Restore prompt on error
      setPrompt(currentPrompt);
      console.error("Error sending message:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50 overflow-hidden">
      <Header />
      
      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden relative" style={{ marginBottom: "88px" }}>
        {/* Sidebar */}
        <Sidebar
          models={models}
          selectedModels={selectedModels}
          setSelectedModels={setSelectedModels}
          onValidated={refetchModels}
          isOpen={sidebarOpen}
          setIsOpen={setSidebarOpen}
        />

        {/* Chat Area */}
        <div
          className={`flex-1 flex flex-col overflow-hidden transition-all duration-300 ${
            sidebarOpen ? "ml-80" : "ml-0"
          }`}
        >
          {/* Error Banner */}
          {error && (
            <div className="bg-red-50 border-b border-red-200 text-red-800 px-6 py-3 flex-shrink-0">
              <p className="text-sm font-medium">Error: {error}</p>
            </div>
          )}

          {/* Chat Tabs */}
          <div className="flex-1 overflow-hidden min-h-0">
            <ChatTabs
              conversations={conversations}
              selectedModels={selectedModels}
              activeTab={activeTab}
              setActiveTab={setActiveTab}
              isLoading={isLoading}
              modelErrors={modelErrors}
            />
          </div>
        </div>
      </div>

      {/* Fixed Input Bar */}
      <ChatInput
        prompt={prompt}
        setPrompt={setPrompt}
        onSubmit={handleSend}
        isLoading={isLoading}
      />
    </div>
  );
}
