"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  getGeminiConfig,
  getOpenAIConfig,
  updateGeminiKey,
  updateOpenAIKey,
} from "@/lib/api";

interface OpenAISettingsProps {
  onValidated?: () => void;
}

export default function OpenAISettings({ onValidated }: OpenAISettingsProps) {
  // OpenAI state
  const [openaiKey, setOpenaiKey] = useState("");
  const [hasOpenAIKey, setHasOpenAIKey] = useState(false);
  const [isSavingOpenAI, setIsSavingOpenAI] = useState(false);
  const [openaiMessage, setOpenaiMessage] = useState<string | null>(null);
  const [openaiError, setOpenaiError] = useState<string | null>(null);

  // Gemini state
  const [geminiKey, setGeminiKey] = useState("");
  const [hasGeminiKey, setHasGeminiKey] = useState(false);
  const [isSavingGemini, setIsSavingGemini] = useState(false);
  const [geminiMessage, setGeminiMessage] = useState<string | null>(null);
  const [geminiError, setGeminiError] = useState<string | null>(null);

  useEffect(() => {
    async function loadConfig() {
      try {
        const [openaiCfg, geminiCfg] = await Promise.all([
          getOpenAIConfig(),
          getGeminiConfig(),
        ]);
        setHasOpenAIKey(openaiCfg.has_key);
        setHasGeminiKey(geminiCfg.has_key);
      } catch (err) {
        console.error("Failed to load provider config:", err);
      }
    }
    loadConfig();
  }, []);

  const handleOpenAISubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!openaiKey.trim()) {
      setOpenaiError("Please enter an API key.");
      return;
    }
    setIsSavingOpenAI(true);
    setOpenaiError(null);
    setOpenaiMessage(null);

    try {
      const result = await updateOpenAIKey(openaiKey.trim());
      setHasOpenAIKey(result.has_key);
      setOpenaiMessage("OpenAI API key saved and verified successfully.");
      setOpenaiKey("");
      if (onValidated) {
        onValidated();
      }
    } catch (err) {
      const description =
        err instanceof Error ? err.message : "Failed to save API key.";
      setOpenaiError(description);
      console.error("Failed to save OpenAI API key:", err);
    } finally {
      setIsSavingOpenAI(false);
    }
  };

  const handleGeminiSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!geminiKey.trim()) {
      setGeminiError("Please enter an API key.");
      return;
    }
    setIsSavingGemini(true);
    setGeminiError(null);
    setGeminiMessage(null);

    try {
      const result = await updateGeminiKey(geminiKey.trim());
      setHasGeminiKey(result.has_key);
      setGeminiMessage("Gemini API key saved and verified successfully.");
      setGeminiKey("");
      if (onValidated) {
        onValidated();
      }
    } catch (err) {
      const description =
        err instanceof Error ? err.message : "Failed to save API key.";
      setGeminiError(description);
      console.error("Failed to save Gemini API key:", err);
    } finally {
      setIsSavingGemini(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* OpenAI */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">
            OpenAI Settings
          </h2>
          <span
            className={`rounded-full px-3 py-1 text-xs font-medium ${
              hasOpenAIKey
                ? "bg-emerald-100 text-emerald-700"
                : "bg-gray-100 text-gray-600"
            }`}
          >
            {hasOpenAIKey ? "Configured" : "Not configured"}
          </span>
        </div>
        <p className="text-sm text-gray-600">
          Add your OpenAI API key to enable comparing local models with GPT-4o
          and GPT-4o Mini. Keys are stored locally on this machine only.
        </p>
        <form onSubmit={handleOpenAISubmit} className="space-y-3">
          <div className="space-y-1">
            <label
              htmlFor="openai-api-key"
              className="block text-sm font-medium text-slate-900"
            >
              OpenAI API Key
            </label>
            <Input
              id="openai-api-key"
              type="password"
              placeholder="sk-..."
              value={openaiKey}
              onChange={(e) => setOpenaiKey(e.target.value)}
              disabled={isSavingOpenAI}
              className="rounded-2xl"
            />
          </div>
          <div className="flex items-center justify-between">
            <Button
              type="submit"
              disabled={isSavingOpenAI || !openaiKey.trim()}
              className="rounded-2xl"
            >
              {isSavingOpenAI ? "Saving..." : "Save & Test"}
            </Button>
          </div>
        </form>
        {openaiMessage && (
          <p className="text-sm text-emerald-700 bg-emerald-50 border border-emerald-100 rounded-2xl px-3 py-2">
            {openaiMessage}
          </p>
        )}
        {openaiError && (
          <p className="text-sm text-red-700 bg-red-50 border border-red-100 rounded-2xl px-3 py-2">
            {openaiError}
          </p>
        )}
      </div>

      {/* Gemini */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">
            Gemini Settings
          </h2>
          <span
            className={`rounded-full px-3 py-1 text-xs font-medium ${
              hasGeminiKey
                ? "bg-emerald-100 text-emerald-700"
                : "bg-gray-100 text-gray-600"
            }`}
          >
            {hasGeminiKey ? "Configured" : "Not configured"}
          </span>
        </div>
        <p className="text-sm text-gray-600">
          Add your Gemini API key to enable Gemini 1.5 Flash comparisons. Keys
          are stored locally on this machine only.
        </p>
        <form onSubmit={handleGeminiSubmit} className="space-y-3">
          <div className="space-y-1">
            <label
              htmlFor="gemini-api-key"
              className="block text-sm font-medium text-slate-900"
            >
              Gemini API Key
            </label>
            <Input
              id="gemini-api-key"
              type="password"
              placeholder="AIza..."
              value={geminiKey}
              onChange={(e) => setGeminiKey(e.target.value)}
              disabled={isSavingGemini}
              className="rounded-2xl"
            />
          </div>
          <div className="flex items-center justify-between">
            <Button
              type="submit"
              disabled={isSavingGemini || !geminiKey.trim()}
              className="rounded-2xl"
            >
              {isSavingGemini ? "Saving..." : "Save & Test"}
            </Button>
          </div>
        </form>
        {geminiMessage && (
          <p className="text-sm text-emerald-700 bg-emerald-50 border border-emerald-100 rounded-2xl px-3 py-2">
            {geminiMessage}
          </p>
        )}
        {geminiError && (
          <p className="text-sm text-red-700 bg-red-50 border border-red-100 rounded-2xl px-3 py-2">
            {geminiError}
          </p>
        )}
      </div>
    </div>
  );
}

