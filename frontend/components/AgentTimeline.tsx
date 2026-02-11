"use client";

import {
  Lightbulb,
  Search,
  BarChart3,
  FileText,
  MessageCircle,
  Check,
  Loader2,
  Circle,
} from "lucide-react";
import type { AgentPhase, ResearchPlan } from "../lib/types";

interface Props {
  phase: AgentPhase;
  plan: ResearchPlan | null;
}

const STAGES: {
  id: AgentPhase;
  label: string;
  icon: typeof Lightbulb;
  color: string;
}[] = [
  { id: "planning", label: "Plan", icon: Lightbulb, color: "text-violet-500" },
  { id: "searching", label: "Search", icon: Search, color: "text-blue-500" },
  { id: "analyzing", label: "Analyze", icon: BarChart3, color: "text-amber-500" },
  { id: "synthesizing", label: "Synthesize", icon: FileText, color: "text-emerald-500" },
  { id: "reflecting", label: "Reflect", icon: MessageCircle, color: "text-pink-500" },
];

const PHASE_ORDER: AgentPhase[] = [
  "planning",
  "searching",
  "analyzing",
  "synthesizing",
  "reflecting",
  "done",
];

function getStageStatus(
  stageId: AgentPhase,
  currentPhase: AgentPhase
): "pending" | "active" | "done" {
  const stageIdx = PHASE_ORDER.indexOf(stageId);
  const currentIdx = PHASE_ORDER.indexOf(currentPhase);

  if (currentPhase === "done" || currentPhase === "error") return "done";
  if (stageIdx < currentIdx) return "done";
  if (stageIdx === currentIdx) return "active";
  return "pending";
}

export default function AgentTimeline({ phase, plan }: Props) {
  if (phase === "idle") return null;

  return (
    <div className="space-y-1">
      <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
        Pipeline
      </h3>
      <div className="space-y-0">
        {STAGES.map((stage, i) => {
          const status = getStageStatus(stage.id, phase);
          const Icon = stage.icon;

          return (
            <div key={stage.id} className="flex items-start gap-3">
              {/* Vertical line + icon */}
              <div className="flex flex-col items-center">
                <div
                  className={`w-8 h-8 rounded-full flex items-center justify-center transition-colors ${
                    status === "done"
                      ? "bg-green-100"
                      : status === "active"
                      ? "bg-white shadow-md border-2 border-current " + stage.color
                      : "bg-gray-100"
                  }`}
                >
                  {status === "done" ? (
                    <Check size={14} className="text-green-600" />
                  ) : status === "active" ? (
                    <Loader2 size={14} className={`${stage.color} animate-spin`} />
                  ) : (
                    <Circle size={14} className="text-gray-300" />
                  )}
                </div>
                {i < STAGES.length - 1 && (
                  <div
                    className={`w-0.5 h-6 ${
                      status === "done" ? "bg-green-300" : "bg-gray-200"
                    }`}
                  />
                )}
              </div>

              {/* Label + detail */}
              <div className="pt-1 pb-4 min-w-0">
                <span
                  className={`text-sm font-medium ${
                    status === "active"
                      ? stage.color
                      : status === "done"
                      ? "text-gray-600"
                      : "text-gray-400"
                  }`}
                >
                  {stage.label}
                </span>

                {/* Show plan details */}
                {stage.id === "planning" && plan && status === "done" && (
                  <div className="mt-1 text-xs text-gray-500 space-y-0.5">
                    {plan.decomposed_questions.map((q, qi) => (
                      <div key={qi} className="truncate">
                        &bull; {q}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
