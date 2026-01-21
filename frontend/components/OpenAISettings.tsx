"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface OpenAISettingsProps {
  onValidated?: () => void;
}

export default function OpenAISettings({ onValidated }: OpenAISettingsProps) {
  // Gemini state
  const [geminiKey, setGeminiKey] = useState("");
  const [hasGeminiKey, setHasGeminiKey] = useState(false);
  const [geminiMessage, setGeminiMessage] = useState<string | null>(null);

  // DeepSeek state
  const [deepseekKey, setDeepseekKey] = useState("");
  const [hasDeepSeekKey, setHasDeepSeekKey] = useState(false);
  const [deepseekMessage, setDeepseekMessage] = useState<string | null>(null);

  // Load status from localStorage on mount
  useEffect(() => {
    const checkKeys = () => {
      setHasGeminiKey(localStorage.getItem("gemini_api_key") !== null);
      setHasDeepSeekKey(localStorage.getItem("deepseek_api_key") !== null);
    };
    checkKeys();
    // Also check when storage changes (e.g., from another tab)
    window.addEventListener("storage", checkKeys);
    return () => window.removeEventListener("storage", checkKeys);
  }, []);

  const handleGeminiSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!geminiKey.trim()) {
      return;
    }
    localStorage.setItem("gemini_api_key", geminiKey.trim());
    setHasGeminiKey(true);
    setGeminiMessage("Gemini API key saved.");
    setGeminiKey("");
    if (onValidated) {
      onValidated();
    }
    // Clear message after 3 seconds
    setTimeout(() => setGeminiMessage(null), 3000);
  };

  const handleGeminiClear = () => {
    localStorage.removeItem("gemini_api_key");
    setHasGeminiKey(false);
    setGeminiMessage("Gemini API key cleared.");
    setTimeout(() => setGeminiMessage(null), 3000);
  };

  const handleDeepSeekSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!deepseekKey.trim()) {
      return;
    }
    localStorage.setItem("deepseek_api_key", deepseekKey.trim());
    setHasDeepSeekKey(true);
    setDeepseekMessage("DeepSeek API key saved.");
    setDeepseekKey("");
    if (onValidated) {
      onValidated();
    }
    // Clear message after 3 seconds
    setTimeout(() => setDeepseekMessage(null), 3000);
  };

  const handleDeepSeekClear = () => {
    localStorage.removeItem("deepseek_api_key");
    setHasDeepSeekKey(false);
    setDeepseekMessage("DeepSeek API key cleared.");
    setTimeout(() => setDeepseekMessage(null), 3000);
  };

  return (
    <div className="space-y-8">
      {/* Security Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-2xl px-4 py-3">
        <p className="text-sm text-blue-800">
          Keys are stored only in your browser and are never saved on the server.
        </p>
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
          Add your Gemini API key to enable Gemini 2.5 Flash comparisons.
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
              className="rounded-2xl"
            />
          </div>
          <div className="flex items-center gap-2">
            <Button
              type="submit"
              disabled={!geminiKey.trim()}
              className="rounded-2xl"
            >
              Save
            </Button>
            {hasGeminiKey && (
              <Button
                type="button"
                variant="outline"
                onClick={handleGeminiClear}
                className="rounded-2xl"
              >
                Clear Key
              </Button>
            )}
          </div>
        </form>
        {geminiMessage && (
          <p className="text-sm text-emerald-700 bg-emerald-50 border border-emerald-100 rounded-2xl px-3 py-2">
            {geminiMessage}
          </p>
        )}
      </div>

      {/* DeepSeek */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">
            DeepSeek Settings
          </h2>
          <span
            className={`rounded-full px-3 py-1 text-xs font-medium ${
              hasDeepSeekKey
                ? "bg-emerald-100 text-emerald-700"
                : "bg-gray-100 text-gray-600"
            }`}
          >
            {hasDeepSeekKey ? "Configured" : "Not configured"}
          </span>
        </div>
        <p className="text-sm text-gray-600">
          Add your DeepSeek API key to enable DeepSeek Chat comparisons.
        </p>
        <form onSubmit={handleDeepSeekSubmit} className="space-y-3">
          <div className="space-y-1">
            <label
              htmlFor="deepseek-api-key"
              className="block text-sm font-medium text-slate-900"
            >
              DeepSeek API Key
            </label>
            <Input
              id="deepseek-api-key"
              type="password"
              placeholder="sk-..."
              value={deepseekKey}
              onChange={(e) => setDeepseekKey(e.target.value)}
              className="rounded-2xl"
            />
          </div>
          <div className="flex items-center gap-2">
            <Button
              type="submit"
              disabled={!deepseekKey.trim()}
              className="rounded-2xl"
            >
              Save
            </Button>
            {hasDeepSeekKey && (
              <Button
                type="button"
                variant="outline"
                onClick={handleDeepSeekClear}
                className="rounded-2xl"
              >
                Clear Key
              </Button>
            )}
          </div>
        </form>
        {deepseekMessage && (
          <p className="text-sm text-emerald-700 bg-emerald-50 border border-emerald-100 rounded-2xl px-3 py-2">
            {deepseekMessage}
          </p>
        )}
      </div>
    </div>
  );
}

