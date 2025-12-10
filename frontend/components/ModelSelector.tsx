"use client";

import { Checkbox } from "@/components/ui/checkbox";
import type { ModelInfo } from "@/lib/types";

interface ModelSelectorProps {
  models: ModelInfo[];
  selected: string[];
  setSelected: (selected: string[]) => void;
}

export default function ModelSelector({
  models,
  selected,
  setSelected,
}: ModelSelectorProps) {
  const handleToggle = (modelId: string) => {
    if (selected.includes(modelId)) {
      setSelected(selected.filter((id) => id !== modelId));
    } else {
      setSelected([...selected, modelId]);
    }
  };

  const handleContainerClick = (
    e: React.MouseEvent<HTMLDivElement>,
    modelId: string
  ) => {
    // Only handle click if it didn't originate from the checkbox
    const target = e.target as HTMLElement;
    if (
      target.closest('button[role="checkbox"]') ||
      target.closest('[data-slot="checkbox"]') ||
      target.closest('input[type="checkbox"]')
    ) {
      return; // Let the checkbox handle its own click via onCheckedChange
    }
    handleToggle(modelId);
  };

  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold text-slate-900">Select Models</h2>
      <div className="space-y-2">
        {models.map((model) => (
          <div
            key={model.id}
            className="flex items-center space-x-3 p-3 rounded-2xl bg-white border border-gray-200 hover:shadow-sm transition-all cursor-pointer"
            onClick={(e) => handleContainerClick(e, model.id)}
          >
            <div onClick={(e) => e.stopPropagation()}>
              <Checkbox
                id={model.id}
                checked={selected.includes(model.id)}
                onCheckedChange={() => handleToggle(model.id)}
                className="focus:ring-2 focus:ring-black"
              />
            </div>
            <label
              htmlFor={model.id}
              className="flex-1 cursor-pointer text-slate-900 font-medium"
            >
              {model.name}
            </label>
            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
              {model.provider}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

