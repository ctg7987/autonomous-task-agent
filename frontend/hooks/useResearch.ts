"use client";

import { useCallback, useReducer, useRef } from "react";
import { useSSE } from "./useSSE";
import type {
  SSEEvent,
  ResearchState,
  ThinkingEntry,
  ReflectionEntry,
  AgentPhase,
} from "../lib/types";
import { initialResearchState } from "../lib/types";

type Action =
  | { type: "START"; query: string }
  | { type: "EVENT"; event: SSEEvent }
  | { type: "ERROR"; message: string }
  | { type: "DONE" }
  | { type: "CLEAR" };

function reducer(state: ResearchState, action: Action): ResearchState {
  switch (action.type) {
    case "START":
      return {
        ...initialResearchState,
        isRunning: true,
        phase: "planning",
      };

    case "EVENT": {
      const { event } = action;
      const updates: Partial<ResearchState> = {};

      if (event.run_id) updates.runId = event.run_id;

      switch (event.event) {
        case "status":
          updates.phase = event.data.phase as AgentPhase;
          updates.progress = event.data.progress;
          updates.activeAgent = event.data.active_agent || "";
          break;

        case "plan":
          updates.plan = event.data;
          break;

        case "agent_thinking": {
          const entry: ThinkingEntry = {
            agent_name: event.data.agent_name,
            thought: event.data.thought,
            step: event.data.step,
            timestamp: event.timestamp,
          };
          updates.thinkingLogs = [...state.thinkingLogs, entry];
          break;
        }

        case "agent_action": {
          const entry: ThinkingEntry = {
            agent_name: event.data.agent_name,
            thought: `Action: ${event.data.action} — ${event.data.input_summary}`,
            step: 0,
            timestamp: event.timestamp,
          };
          updates.thinkingLogs = [...state.thinkingLogs, entry];
          break;
        }

        case "search_results":
          updates.searchResults = event.data.results || [];
          break;

        case "report":
          updates.report = event.data;
          break;

        case "reflection": {
          const ref: ReflectionEntry = {
            critique: event.data.critique,
            suggestions: event.data.suggestions,
            retry_number: event.data.retry_number,
            score: event.data.score,
            timestamp: event.timestamp,
          };
          updates.reflections = [...state.reflections, ref];
          break;
        }

        case "error":
          updates.errors = [...state.errors, event.data.message || "Unknown error"];
          updates.phase = "error";
          break;

        case "done":
          updates.phase = state.phase === "error" ? "error" : "done";
          updates.isRunning = false;
          updates.progress = 1.0;
          break;
      }

      return { ...state, ...updates };
    }

    case "ERROR":
      return {
        ...state,
        errors: [...state.errors, action.message],
        phase: "error",
        isRunning: false,
      };

    case "DONE":
      return { ...state, isRunning: false };

    case "CLEAR":
      return initialResearchState;

    default:
      return state;
  }
}

export function useResearch() {
  const [state, dispatch] = useReducer(reducer, initialResearchState);
  const stateRef = useRef(state);
  stateRef.current = state;

  const handleEvent = useCallback((event: SSEEvent) => {
    dispatch({ type: "EVENT", event });
  }, []);

  const handleError = useCallback((message: string) => {
    dispatch({ type: "ERROR", message });
  }, []);

  const handleDone = useCallback(() => {
    dispatch({ type: "DONE" });
  }, []);

  const { startResearch: sseStart, stopResearch: sseStop, isConnected } = useSSE({
    onEvent: handleEvent,
    onError: handleError,
    onDone: handleDone,
  });

  const startResearch = useCallback(
    (query: string) => {
      if (!query.trim()) return;
      dispatch({ type: "START", query });
      sseStart(query);
    },
    [sseStart]
  );

  const stopResearch = useCallback(() => {
    sseStop();
    dispatch({ type: "DONE" });
  }, [sseStop]);

  const clearResults = useCallback(() => {
    dispatch({ type: "CLEAR" });
  }, []);

  return {
    state,
    isConnected,
    startResearch,
    stopResearch,
    clearResults,
  };
}
