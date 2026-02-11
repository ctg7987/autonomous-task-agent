"use client";

import { useState, useCallback, KeyboardEvent } from "react";
import { Search, Square, Trash2, Loader2 } from "lucide-react";

interface Props {
  onSubmit: (query: string) => void;
  onStop: () => void;
  onClear: () => void;
  isRunning: boolean;
}

export default function ResearchForm({ onSubmit, onStop, onClear, isRunning }: Props) {
  const [query, setQuery] = useState("");

  const handleSubmit = useCallback(() => {
    const trimmed = query.trim();
    if (trimmed && !isRunning) {
      onSubmit(trimmed);
    }
  }, [query, isRunning, onSubmit]);

  const handleKeyDown = useCallback(
    (e: KeyboardEvent<HTMLTextAreaElement>) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  return (
    <div className="space-y-3">
      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder='e.g., "Research the latest developments in quantum computing and their practical applications"'
        rows={3}
        maxLength={2000}
        disabled={isRunning}
        className="w-full px-4 py-3 rounded-xl border border-gray-200 bg-white text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent resize-none transition-all disabled:opacity-50 disabled:cursor-not-allowed"
      />
      <div className="flex items-center gap-3">
        {isRunning ? (
          <button
            onClick={onStop}
            className="flex items-center gap-2 px-5 py-2.5 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition-colors"
          >
            <Square size={16} />
            Stop
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={!query.trim()}
            className="flex items-center gap-2 px-5 py-2.5 bg-violet-600 hover:bg-violet-700 disabled:bg-gray-300 text-white rounded-lg font-medium transition-colors disabled:cursor-not-allowed"
          >
            {isRunning ? <Loader2 size={16} className="animate-spin" /> : <Search size={16} />}
            Run Research
          </button>
        )}
        <button
          onClick={() => {
            setQuery("");
            onClear();
          }}
          disabled={isRunning}
          className="flex items-center gap-2 px-4 py-2.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg font-medium transition-colors disabled:opacity-50"
        >
          <Trash2 size={16} />
          Clear
        </button>
        <span className="ml-auto text-xs text-gray-400">
          {isRunning ? "" : "Ctrl+Enter to submit"}
        </span>
      </div>
    </div>
  );
}
