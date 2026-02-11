"use client";

import type { AgentPhase } from "../lib/types";

interface Props {
  phase: AgentPhase;
  progress: number;
  activeAgent: string;
  isConnected: boolean;
}

const PHASE_CONFIG: Record<AgentPhase, { label: string; color: string; bg: string }> = {
  idle: { label: "Ready", color: "bg-gray-400", bg: "bg-gray-50" },
  planning: { label: "Planning", color: "bg-violet-500", bg: "bg-violet-50" },
  searching: { label: "Searching", color: "bg-blue-500", bg: "bg-blue-50" },
  analyzing: { label: "Analyzing", color: "bg-amber-500", bg: "bg-amber-50" },
  synthesizing: { label: "Synthesizing", color: "bg-emerald-500", bg: "bg-emerald-50" },
  reflecting: { label: "Reflecting", color: "bg-pink-500", bg: "bg-pink-50" },
  done: { label: "Complete", color: "bg-green-500", bg: "bg-green-50" },
  error: { label: "Error", color: "bg-red-500", bg: "bg-red-50" },
};

export default function StatusIndicator({ phase, progress, activeAgent, isConnected }: Props) {
  const config = PHASE_CONFIG[phase];
  const pct = Math.round(progress * 100);

  return (
    <div className={`rounded-xl px-4 py-3 ${config.bg} transition-colors`}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div
            className={`w-2.5 h-2.5 rounded-full ${config.color} ${
              phase !== "idle" && phase !== "done" && phase !== "error"
                ? "animate-pulse-slow"
                : ""
            }`}
          />
          <span className="text-sm font-medium text-gray-700">{config.label}</span>
          {activeAgent && (
            <span className="text-xs text-gray-500">({activeAgent})</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <div
            className={`w-2 h-2 rounded-full ${
              isConnected ? "bg-green-400" : "bg-gray-300"
            }`}
          />
          <span className="text-xs text-gray-500">
            {isConnected ? "Connected" : "Disconnected"}
          </span>
        </div>
      </div>

      {/* Progress bar */}
      {phase !== "idle" && (
        <div className="w-full h-1.5 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full ${config.color} rounded-full transition-all duration-500 ease-out`}
            style={{ width: `${pct}%` }}
          />
        </div>
      )}
    </div>
  );
}
