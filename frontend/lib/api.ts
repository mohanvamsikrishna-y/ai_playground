import type {
  ChatRequest,
  ChatResponse,
  CompareRequest,
  CompareResponse,
  ModelInfo,
} from "./types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

async function handleResponse<T>(response: Response): Promise<T> {
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
    // Read API keys from localStorage
    const geminiKey = localStorage.getItem("gemini_api_key");
    const deepseekKey = localStorage.getItem("deepseek_api_key");

    // Build headers with API keys if available
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    if (geminiKey) {
      headers["X-GEMINI-API-KEY"] = geminiKey;
    }
    if (deepseekKey) {
      headers["X-DEEPSEEK-API-KEY"] = deepseekKey;
    }

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
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
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
