"use client";

import { useResearch } from "../hooks/useResearch";
import ResearchForm from "../components/ResearchForm";
import StatusIndicator from "../components/StatusIndicator";
import AgentTimeline from "../components/AgentTimeline";
import ThinkingPanel from "../components/ThinkingPanel";
import ReportView from "../components/ReportView";
import { Zap } from "lucide-react";

export default function Home() {
  const { state, isConnected, startResearch, stopResearch, clearResults } =
    useResearch();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-gradient-to-r from-violet-600 to-purple-700 text-white">
        <div className="max-w-6xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3 mb-2">
            <Zap size={28} className="text-violet-200" />
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">
              Autonomous AI Research Agent
            </h1>
          </div>
          <p className="text-violet-200 text-sm sm:text-base">
            Multi-agent pipeline with planning, parallel search, analysis,
            synthesis, and self-critique
          </p>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-6xl mx-auto px-4 py-6 sm:px-6 lg:px-8 space-y-6">
        {/* Input */}
        <section className="bg-white rounded-2xl shadow-sm border border-gray-200 p-5">
          <ResearchForm
            onSubmit={startResearch}
            onStop={stopResearch}
            onClear={clearResults}
            isRunning={state.isRunning}
          />
        </section>

        {/* Status bar */}
        {state.phase !== "idle" && (
          <StatusIndicator
            phase={state.phase}
            progress={state.progress}
            activeAgent={state.activeAgent}
            isConnected={isConnected}
          />
        )}

        {/* Errors */}
        {state.errors.length > 0 && (
          <div className="bg-red-50 border border-red-200 rounded-xl px-4 py-3">
            {state.errors.map((err, i) => (
              <p key={i} className="text-sm text-red-700">
                {err}
              </p>
            ))}
          </div>
        )}

        {/* Two-column layout when active */}
        {state.phase !== "idle" && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            {/* Left: Timeline */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-5 sticky top-6">
                <AgentTimeline phase={state.phase} plan={state.plan} />
              </div>
            </div>

            {/* Right: Thinking + Report */}
            <div className="lg:col-span-3 space-y-6">
              {/* Thinking panel */}
              <ThinkingPanel logs={state.thinkingLogs} />

              {/* Report */}
              {state.report && (
                <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
                  <ReportView
                    report={state.report}
                    reflections={state.reflections}
                  />
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
