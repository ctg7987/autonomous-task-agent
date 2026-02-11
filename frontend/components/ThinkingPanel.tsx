"use client";

import { useState, useRef, useEffect } from "react";
import { ChevronDown, ChevronRight, Brain } from "lucide-react";
import type { ThinkingEntry } from "../lib/types";

interface Props {
  logs: ThinkingEntry[];
}

const AGENT_COLORS: Record<string, string> = {
  planner: "text-violet-600 bg-violet-50",
  searcher: "text-blue-600 bg-blue-50",
  analyzer: "text-amber-600 bg-amber-50",
  synthesizer: "text-emerald-600 bg-emerald-50",
  critic: "text-pink-600 bg-pink-50",
};

export default function ThinkingPanel({ logs }: Props) {
  const [isExpanded, setIsExpanded] = useState(true);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  if (logs.length === 0) return null;

  return (
    <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center gap-2 px-4 py-3 text-left hover:bg-gray-50 transition-colors"
      >
        <Brain size={16} className="text-gray-500" />
        <span className="text-sm font-semibold text-gray-700 flex-1">
          Agent Reasoning
        </span>
        <span className="text-xs text-gray-400">{logs.length} entries</span>
        {isExpanded ? (
          <ChevronDown size={16} className="text-gray-400" />
        ) : (
          <ChevronRight size={16} className="text-gray-400" />
        )}
      </button>

      {isExpanded && (
        <div
          ref={scrollRef}
          className="max-h-64 overflow-y-auto scrollbar-thin border-t border-gray-100 px-4 py-2 space-y-2"
        >
          {logs.map((log, i) => {
            const colorClass =
              AGENT_COLORS[log.agent_name] || "text-gray-600 bg-gray-50";
            const [textColor, bgColor] = colorClass.split(" ");

            return (
              <div key={i} className="flex items-start gap-2 animate-fade-in">
                <span
                  className={`shrink-0 text-[10px] font-bold uppercase px-1.5 py-0.5 rounded ${colorClass}`}
                >
                  {log.agent_name}
                </span>
                <span className="text-sm text-gray-600 leading-relaxed">
                  {log.thought}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
