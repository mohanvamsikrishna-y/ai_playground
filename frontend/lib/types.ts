export interface ModelInfo {
  id: string;
  name: string;
  provider: string;
}

export interface CompareRequest {
  conversations: Record<string, ChatMessage[]>;
}

export interface ModelResponse {
  model_id: string;
  output: string;
  latency_ms: number;
  tokens_in?: number;
  tokens_out?: number;
  estimated_cost_usd?: number;
}

export interface CompareResponse {
  results: Record<string, ChatMessage>;
  latency_ms: Record<string, number>;
  errors?: Record<string, string>;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatRequest {
  model_id: string;
  messages: ChatMessage[];
}

export interface ChatResponse {
  model_id: string;
  message: string;
}

