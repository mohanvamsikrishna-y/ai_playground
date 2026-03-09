"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getApiKey, setApiKey, removeApiKey, hasApiKey as checkHasKey } from "@/lib/storage";

interface OpenAISettingsProps {
  onValidated?: () => void;
}

export default function OpenAISettings({ onValidated }: OpenAISettingsProps) {
  const { data: session } = useSession();

  // Gemini state
  const [geminiKey, setGeminiKey] = useState("");
  const [hasGeminiKey, setHasGeminiKey] = useState(false);
  const [geminiMessage, setGeminiMessage] = useState<string | null>(null);

  // DeepSeek state
  const [deepseekKey, setDeepseekKey] = useState("");
  const [hasDeepSeekKey, setHasDeepSeekKey] = useState(false);
  const [deepseekMessage, setDeepseekMessage] = useState<string | null>(null);

  // OpenAI state
  const [openaiKey, setOpenaiKey] = useState("");
  const [hasOpenAIKey, setHasOpenAIKey] = useState(false);
  const [openaiMessage, setOpenaiMessage] = useState<string | null>(null);

  // Claude state
  const [claudeKey, setClaudeKey] = useState("");
  const [hasClaudeKey, setHasClaudeKey] = useState(false);
  const [claudeMessage, setClaudeMessage] = useState<string | null>(null);

  useEffect(() => {
    const refreshKeyStatus = () => {
      setHasGeminiKey(checkHasKey("gemini"));
      setHasDeepSeekKey(checkHasKey("deepseek"));
      setHasOpenAIKey(checkHasKey("openai"));
      setHasClaudeKey(checkHasKey("claude"));
    };
    refreshKeyStatus();
    window.addEventListener("storage", refreshKeyStatus);
    return () => window.removeEventListener("storage", refreshKeyStatus);
  }, [session]);

  const handleGeminiSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!geminiKey.trim()) return;
    setApiKey("gemini", geminiKey.trim());
    setHasGeminiKey(true);
    setGeminiMessage("Gemini API key saved.");
    setGeminiKey("");
    onValidated?.();
    setTimeout(() => setGeminiMessage(null), 3000);
  };

  const handleGeminiClear = () => {
    removeApiKey("gemini");
    setHasGeminiKey(false);
    setGeminiMessage("Gemini API key cleared.");
    setTimeout(() => setGeminiMessage(null), 3000);
  };

  const handleDeepSeekSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!deepseekKey.trim()) return;
    setApiKey("deepseek", deepseekKey.trim());
    setHasDeepSeekKey(true);
    setDeepseekMessage("DeepSeek API key saved.");
    setDeepseekKey("");
    onValidated?.();
    setTimeout(() => setDeepseekMessage(null), 3000);
  };

  const handleDeepSeekClear = () => {
    removeApiKey("deepseek");
    setHasDeepSeekKey(false);
    setDeepseekMessage("DeepSeek API key cleared.");
    setTimeout(() => setDeepseekMessage(null), 3000);
  };

  const handleOpenAISubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!openaiKey.trim()) return;
    setApiKey("openai", openaiKey.trim());
    setHasOpenAIKey(true);
    setOpenaiMessage("OpenAI API key saved.");
    setOpenaiKey("");
    onValidated?.();
    setTimeout(() => setOpenaiMessage(null), 3000);
  };

  const handleOpenAIClear = () => {
    removeApiKey("openai");
    setHasOpenAIKey(false);
    setOpenaiMessage("OpenAI API key cleared.");
    setTimeout(() => setOpenaiMessage(null), 3000);
  };

  const handleClaudeSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!claudeKey.trim()) return;
    setApiKey("claude", claudeKey.trim());
    setHasClaudeKey(true);
    setClaudeMessage("Claude API key saved.");
    setClaudeKey("");
    onValidated?.();
    setTimeout(() => setClaudeMessage(null), 3000);
  };

  const handleClaudeClear = () => {
    removeApiKey("claude");
    setHasClaudeKey(false);
    setClaudeMessage("Claude API key cleared.");
    setTimeout(() => setClaudeMessage(null), 3000);
  };

  return (
    <div className="space-y-8">
      {/* Security Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-2xl px-4 py-3">
        <p className="text-sm text-blue-800">
          Keys are stored only in your browser and are never saved on the server.
        </p>
      </div>

      {/* OpenAI - near top so visible without scrolling */}
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
          Add your OpenAI API key to enable GPT-4o and GPT-4o Mini.
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
              className="rounded-2xl"
            />
          </div>
          <div className="flex items-center gap-2">
            <Button
              type="submit"
              disabled={!openaiKey.trim()}
              className="rounded-2xl"
            >
              Save
            </Button>
            {hasOpenAIKey && (
              <Button
                type="button"
                variant="outline"
                onClick={handleOpenAIClear}
                className="rounded-2xl"
              >
                Clear Key
              </Button>
            )}
          </div>
        </form>
        {openaiMessage && (
          <p className="text-sm text-emerald-700 bg-emerald-50 border border-emerald-100 rounded-2xl px-3 py-2">
            {openaiMessage}
          </p>
        )}
      </div>

      {/* Claude - near top so visible without scrolling */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-slate-900">
            Claude Settings
          </h2>
          <span
            className={`rounded-full px-3 py-1 text-xs font-medium ${
              hasClaudeKey
                ? "bg-emerald-100 text-emerald-700"
                : "bg-gray-100 text-gray-600"
            }`}
          >
            {hasClaudeKey ? "Configured" : "Not configured"}
          </span>
        </div>
        <p className="text-sm text-gray-600">
          Add your Anthropic API key to enable Claude 3 Haiku and Sonnet.
        </p>
        <form onSubmit={handleClaudeSubmit} className="space-y-3">
          <div className="space-y-1">
            <label
              htmlFor="claude-api-key"
              className="block text-sm font-medium text-slate-900"
            >
              Claude API Key
            </label>
            <Input
              id="claude-api-key"
              type="password"
              placeholder="sk-ant-..."
              value={claudeKey}
              onChange={(e) => setClaudeKey(e.target.value)}
              className="rounded-2xl"
            />
          </div>
          <div className="flex items-center gap-2">
            <Button
              type="submit"
              disabled={!claudeKey.trim()}
              className="rounded-2xl"
            >
              Save
            </Button>
            {hasClaudeKey && (
              <Button
                type="button"
                variant="outline"
                onClick={handleClaudeClear}
                className="rounded-2xl"
              >
                Clear Key
              </Button>
            )}
          </div>
        </form>
        {claudeMessage && (
          <p className="text-sm text-emerald-700 bg-emerald-50 border border-emerald-100 rounded-2xl px-3 py-2">
            {claudeMessage}
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

