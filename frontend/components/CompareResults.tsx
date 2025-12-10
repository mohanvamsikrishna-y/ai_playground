"use client";

import type { ModelResponse } from "@/lib/types";
import ResultCard from "./ResultCard";

interface CompareResultsProps {
  results: ModelResponse[];
}

export default function CompareResults({ results }: CompareResultsProps) {
  if (results.length === 0) {
    return null;
  }

  return (
    <div className="w-full">
      <h2 className="text-2xl font-semibold text-slate-900 mb-6">
        Comparison Results
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {results.map((result) => (
          <ResultCard key={result.model_id} result={result} />
        ))}
      </div>
    </div>
  );
}

