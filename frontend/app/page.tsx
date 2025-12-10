"use client";

import { useEffect, useState } from "react";
import Header from "@/components/Header";
import PromptInput from "@/components/PromptInput";
import ModelSelector from "@/components/ModelSelector";
import CompareResults from "@/components/CompareResults";
import { getModels, compareModels } from "@/lib/api";
import type { ModelInfo, ModelResponse } from "@/lib/types";

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [results, setResults] = useState<ModelResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch models on mount
  useEffect(() => {
    async function fetchModels() {
      try {
        const fetchedModels = await getModels();
        setModels(fetchedModels);
        // Auto-select all models by default
        setSelectedModels(fetchedModels.map((m) => m.id));
      } catch (err) {
        setError("Failed to load models. Make sure the backend is running.");
        console.error("Error fetching models:", err);
      }
    }
    fetchModels();
  }, []);

  const handleCompare = async () => {
    if (!prompt.trim() || selectedModels.length === 0) {
      return;
    }

    setIsLoading(true);
    setError(null);
    setResults([]);

    try {
      const response = await compareModels({
        prompt: prompt.trim(),
        model_ids: selectedModels,
      });
      setResults(response.results);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to compare models. Please try again."
      );
      console.error("Error comparing models:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#f5f5f7]">
      <Header />
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="space-y-8">
          {/* Prompt Input Section */}
          <div className="bg-white rounded-2xl shadow-sm shadow-gray-300/50 p-6">
            <PromptInput
              prompt={prompt}
              setPrompt={setPrompt}
              onSubmit={handleCompare}
              isLoading={isLoading}
            />
          </div>

          {/* Model Selection Section */}
          <div className="bg-white rounded-2xl shadow-sm shadow-gray-300/50 p-6">
            <ModelSelector
              models={models}
              selected={selectedModels}
              setSelected={setSelectedModels}
            />
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 rounded-2xl p-4">
              <p className="font-medium">Error: {error}</p>
            </div>
          )}

          {/* Results Section */}
          {results.length > 0 && (
            <div className="bg-white rounded-2xl shadow-sm shadow-gray-300/50 p-6">
              <CompareResults results={results} />
            </div>
          )}

          {/* Loading State */}
          {isLoading && (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-black"></div>
              <p className="mt-4 text-slate-900">Running comparison...</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
