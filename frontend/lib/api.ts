import type { CompareRequest, CompareResponse, ModelInfo } from "./types";

const API_BASE_URL = "http://localhost:8000";

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
    const response = await fetch(`${API_BASE_URL}/compare`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    return handleResponse<CompareResponse>(response);
  } catch (error) {
    console.error("Failed to compare models:", error);
    throw error;
  }
}

