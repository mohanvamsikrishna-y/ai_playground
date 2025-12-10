export interface ModelInfo {
  id: string;
  name: string;
  provider: string;
}

export interface CompareRequest {
  prompt: string;
  model_ids: string[];
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
  results: ModelResponse[];
}

