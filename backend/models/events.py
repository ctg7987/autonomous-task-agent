from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

from .research import ResearchPlan, ResearchReport, SearchResult


EventType = Literal[
    "status",
    "plan",
    "agent_thinking",
    "agent_action",
    "search_results",
    "analysis",
    "report",
    "reflection",
    "error",
    "done",
]


class SSEEvent(BaseModel):
    event: EventType
    data: Any
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_sse(self) -> str:
        import json
        payload = self.model_dump(mode="json")
        return f"data: {json.dumps(payload)}\n\n"


class StatusEvent(SSEEvent):
    event: Literal["status"] = "status"
    data: dict = Field(default_factory=dict)

    @classmethod
    def create(cls, phase: str, progress: float, active_agent: str = "") -> StatusEvent:
        return cls(data={"phase": phase, "progress": progress, "active_agent": active_agent})


class PlanEvent(SSEEvent):
    event: Literal["plan"] = "plan"

    @classmethod
    def create(cls, plan: ResearchPlan) -> PlanEvent:
        return cls(data=plan.model_dump())


class AgentThinkingEvent(SSEEvent):
    event: Literal["agent_thinking"] = "agent_thinking"

    @classmethod
    def create(cls, agent_name: str, thought: str, step: int = 0) -> AgentThinkingEvent:
        return cls(data={"agent_name": agent_name, "thought": thought, "step": step})


class AgentActionEvent(SSEEvent):
    event: Literal["agent_action"] = "agent_action"

    @classmethod
    def create(cls, agent_name: str, action: str, input_summary: str = "") -> AgentActionEvent:
        return cls(data={"agent_name": agent_name, "action": action, "input_summary": input_summary})


class SearchResultsEvent(SSEEvent):
    event: Literal["search_results"] = "search_results"

    @classmethod
    def create(cls, results: list[SearchResult], query_used: str = "") -> SearchResultsEvent:
        return cls(data={"results": [r.model_dump() for r in results], "query_used": query_used})


class ReportEvent(SSEEvent):
    event: Literal["report"] = "report"

    @classmethod
    def create(cls, report: ResearchReport) -> ReportEvent:
        return cls(data=report.model_dump())


class ReflectionEvent(SSEEvent):
    event: Literal["reflection"] = "reflection"

    @classmethod
    def create(cls, critique: str, suggestions: list[str], retry_number: int, score: float) -> ReflectionEvent:
        return cls(data={
            "critique": critique,
            "suggestions": suggestions,
            "retry_number": retry_number,
            "score": score,
        })


class ErrorEvent(SSEEvent):
    event: Literal["error"] = "error"

    @classmethod
    def create(cls, message: str, agent_name: str = "") -> ErrorEvent:
        return cls(data={"message": message, "agent_name": agent_name})


class DoneEvent(SSEEvent):
    event: Literal["done"] = "done"
    data: dict = Field(default_factory=lambda: {"status": "complete"})
