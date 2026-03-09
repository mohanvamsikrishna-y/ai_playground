import { getApiKey, clearSessionData } from "./storage";
import type {
  ChatRequest,
  ChatResponse,
  CompareRequest,
  CompareResponse,
  ModelInfo,
} from "./types";

const getApiBaseUrl = (): string => {
  const envUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  const isProduction = process.env.NODE_ENV === 'production';
  const isBrowser = typeof window !== 'undefined';
  
  if (!envUrl && isProduction && isBrowser) {
    console.error('NEXT_PUBLIC_API_BASE_URL is not set in production!');
    console.error('Falling back to localhost - this will fail in production!');
  }
  
  const apiUrl = envUrl || 'http://localhost:8000';
  if (isBrowser) {
    console.log(`[API] Using base URL: ${apiUrl}`);
  }
  return apiUrl;
};

export const API_BASE_URL = getApiBaseUrl();

export function getAuthHeaders(): Record<string, string> {
  if (typeof window === "undefined") return {};
  const idToken = sessionStorage.getItem("id_token");
  if (idToken) {
    return { Authorization: `Bearer ${idToken}` };
  }
  return {};
}

function getProviderHeaders(): Record<string, string> {
  const headers: Record<string, string> = {};
  const geminiKey = getApiKey("gemini");
  const deepseekKey = getApiKey("deepseek");
  const openaiKey = getApiKey("openai");
  const claudeKey = getApiKey("claude");
  if (geminiKey) headers["X-GEMINI-API-KEY"] = geminiKey;
  if (deepseekKey) headers["X-DEEPSEEK-API-KEY"] = deepseekKey;
  if (openaiKey) headers["X-OPENAI-API-KEY"] = openaiKey;
  if (claudeKey) headers["X-CLAUDE-API-KEY"] = claudeKey;
  return headers;
}

export class AuthError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "AuthError";
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (response.status === 401) {
    clearSessionData();
    throw new AuthError("Session expired. Please sign in again.");
  }
  if (!response.ok) {
    const errorText = await response.text().catch(() => "Unknown error");
    throw new Error(`API error: ${response.status} ${errorText}`);
  }
  return response.json();
}

export async function getModels(): Promise<ModelInfo[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/models`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(),
      },
    });
    return handleResponse<ModelInfo[]>(response);
  } catch (error) {
    console.error("Failed to fetch models:", error);
    throw error;
  }
}

export async function compareModels(
  payload: CompareRequest
): Promise<CompareResponse> {
  try {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
      ...getProviderHeaders(),
    };

    const response = await fetch(`${API_BASE_URL}/compare`, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
    });
    return handleResponse<CompareResponse>(response);
  } catch (error) {
    console.error("Failed to compare models:", error);
    throw error;
  }
}

export async function chatModel(payload: ChatRequest): Promise<ChatResponse> {
  try {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...getAuthHeaders(),
      ...getProviderHeaders(),
    };

    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
    });
    return handleResponse<ChatResponse>(response);
  } catch (error) {
    console.error("Failed to chat with model:", error);
    throw error;
  }
}

export async function getOllamaModels(): Promise<ModelInfo[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/ollama/models`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });
    return handleResponse<ModelInfo[]>(response);
  } catch (error) {
    console.error("Failed to fetch Ollama models:", error);
    throw error;
  }
}

export async function pullOllamaModel(
  modelName: string
): Promise<{ status: string; model: string }> {
  try {
    const response = await fetch(`${API_BASE_URL}/ollama/pull`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ model: modelName }),
    });
    return handleResponse<{ status: string; model: string }>(response);
  } catch (error) {
    console.error("Failed to pull Ollama model:", error);
    throw error;
  }
}
