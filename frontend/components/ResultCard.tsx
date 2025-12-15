"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { ModelResponse } from "@/lib/types";

interface ResultCardProps {
  result: ModelResponse;
}

export default function ResultCard({ result }: ResultCardProps) {
  return (
    <Card className="rounded-2xl shadow-sm shadow-gray-300/50 hover:shadow-md transition-all border-gray-200 flex flex-col h-full">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg font-semibold text-slate-900">
          {result.model_id}
        </CardTitle>
        <div className="flex items-center gap-4 text-sm text-gray-600 mt-2">
          <span>
            <span className="font-medium">Latency:</span>{" "}
            {result.latency_ms.toFixed(0)}ms
          </span>
          {result.tokens_in !== undefined && result.tokens_out !== undefined && (
            <span>
              <span className="font-medium">Tokens:</span> {result.tokens_in}/
              {result.tokens_out}
            </span>
          )}
          {typeof result.estimated_cost_usd === "number" && (
            <span>
              <span className="font-medium">Cost:</span> $
              {result.estimated_cost_usd.toFixed(4)}
            </span>
          )}
        </div>
      </CardHeader>
      <CardContent className="flex-1 overflow-auto">
        <div className="text-slate-900 whitespace-pre-wrap leading-relaxed">
          {result.output || "No output generated."}
        </div>
      </CardContent>
    </Card>
  );
}

