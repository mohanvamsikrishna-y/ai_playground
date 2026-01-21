"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { pullOllamaModel } from "@/lib/api";

interface OllamaDownloadProps {
  onModelAdded: () => void;
}

export default function OllamaDownload({ onModelAdded }: OllamaDownloadProps) {
  const [modelName, setModelName] = useState("");
  const [isPulling, setIsPulling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!modelName.trim() || isPulling) {
      return;
    }

    setIsPulling(true);
    setError(null);
    setSuccess(null);

    try {
      await pullOllamaModel(modelName.trim());
      setSuccess(`Model "${modelName.trim()}" downloaded successfully!`);
      setModelName("");
      // Refresh models list
      onModelAdded();
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      let errorMessage = "Failed to download model.";
      if (err instanceof Error) {
        errorMessage = err.message;
        // Check if it's an Ollama not running error
        if (
          errorMessage.includes("Ollama is not running") ||
          errorMessage.includes("Failed to fetch")
        ) {
          errorMessage =
            "Ollama is not running. Start Ollama to use local models.";
        }
      }
      setError(errorMessage);
    } finally {
      setIsPulling(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-900">
          Add Local Model (Ollama)
        </h2>
      </div>
      <p className="text-sm text-gray-600">
        Download any Ollama model by name (e.g., llama3.2, qwen2.5, mistral:latest)
      </p>
      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="space-y-1">
          <label
            htmlFor="ollama-model-name"
            className="block text-sm font-medium text-slate-900"
          >
            Model Name
          </label>
          <Input
            id="ollama-model-name"
            type="text"
            placeholder="llama3.2"
            value={modelName}
            onChange={(e) => setModelName(e.target.value)}
            disabled={isPulling}
            className="rounded-2xl"
          />
        </div>
        <Button
          type="submit"
          disabled={!modelName.trim() || isPulling}
          className="w-full rounded-2xl"
        >
          {isPulling ? (
            <div className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              <span>Downloading...</span>
            </div>
          ) : (
            "Download"
          )}
        </Button>
      </form>
      {success && (
        <p className="text-sm text-emerald-700 bg-emerald-50 border border-emerald-100 rounded-2xl px-3 py-2">
          {success}
        </p>
      )}
      {error && (
        <p className="text-sm text-red-700 bg-red-50 border border-red-100 rounded-2xl px-3 py-2">
          {error}
        </p>
      )}
    </div>
  );
}
