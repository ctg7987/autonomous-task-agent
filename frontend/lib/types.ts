// Agent phases matching backend StatusEvent
export type AgentPhase =
  | "idle"
  | "planning"
  | "searching"
  | "analyzing"
  | "synthesizing"
  | "reflecting"
  | "done"
  | "error";

// SSE event types from backend
export type EventType =
  | "status"
  | "plan"
  | "agent_thinking"
  | "agent_action"
  | "search_results"
  | "analysis"
  | "report"
  | "reflection"
  | "error"
  | "done";

export interface SSEEvent {
  event: EventType;
  data: any;
  timestamp: string;
  run_id?: string;
}

// Domain models (mirror backend Pydantic models)

export interface ResearchPlan {
  original_query: string;
  decomposed_questions: string[];
  search_strategies: string[];
  expected_source_types: string[];
}

export interface SearchResult {
  url: string;
  title: string;
  snippet: string;
}

export interface Citation {
  title: string;
  url: string;
  credibility_score: number;
  relevant_claims: string[];
}

export interface ResearchReport {
  summary: string;
  key_findings: string[];
  citations: Citation[];
  confidence_score: number;
  methodology_note: string;
}

export interface ThinkingEntry {
  agent_name: string;
  thought: string;
  step: number;
  timestamp: string;
}

export interface ReflectionEntry {
  critique: string;
  suggestions: string[];
  retry_number: number;
  score: number;
  timestamp: string;
}

// Centralized research state

export interface ResearchState {
  phase: AgentPhase;
  progress: number; // 0.0 - 1.0
  activeAgent: string;
  runId: string | null;
  plan: ResearchPlan | null;
  searchResults: SearchResult[];
  report: ResearchReport | null;
  reflections: ReflectionEntry[];
  thinkingLogs: ThinkingEntry[];
  errors: string[];
  isRunning: boolean;
}

export const initialResearchState: ResearchState = {
  phase: "idle",
  progress: 0,
  activeAgent: "",
  runId: null,
  plan: null,
  searchResults: [],
  report: null,
  reflections: [],
  thinkingLogs: [],
  errors: [],
  isRunning: false,
};
