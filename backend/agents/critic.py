from __future__ import annotations

from typing import Any

from .base import BaseAgent, EmitFn
from ..models.research import ResearchReport
from ..models.agents import ReflectionResult
from ..models.events import AgentThinkingEvent, ReflectionEvent


class CriticAgent(BaseAgent):
    name = "critic"
    description = "Evaluates research report quality and provides critique for improvement"

    async def _execute(self, input_data: Any, emit: EmitFn) -> ReflectionResult:
        report: ResearchReport = input_data["report"]
        query: str = input_data["query"]
        retry_number: int = input_data.get("retry_number", 0)

        await emit(AgentThinkingEvent.create(
            agent_name=self.name,
            thought=f"Evaluating report quality (review #{retry_number + 1})",
            step=1,
        ))

        system_prompt = """You are a research quality reviewer. Evaluate the provided research report for:

1. COMPLETENESS: Does it answer the original research query?
2. ACCURACY: Are claims supported by cited sources?
3. CLARITY: Is the summary well-written and coherent?
4. DEPTH: Are the findings substantive (not vague)?
5. CITATIONS: Are sources properly attributed?

Return valid JSON with exactly these fields:
- is_satisfactory: boolean (true if report meets quality standards, false if it needs improvement)
- critique: string describing strengths and weaknesses
- suggestions: array of specific improvement suggestions (empty if satisfactory)
- score: float 0.0-1.0 (overall quality score, >0.7 is satisfactory)

Be constructive but honest. Only reject if there are genuine quality issues."""

        user_prompt = f"""Original query: {query}

Report summary ({len(report.summary)} chars):
{report.summary}

Key findings ({len(report.key_findings)}):
{chr(10).join(f'- {f}' for f in report.key_findings)}

Citations: {len(report.citations)} sources
Confidence score: {report.confidence_score}

Evaluate this report."""

        result = await self._llm_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=ReflectionResult,
            temperature=0.3,
            max_tokens=1024,
        )

        await emit(AgentThinkingEvent.create(
            agent_name=self.name,
            thought=f"Review complete: score={result.score:.2f}, satisfactory={result.is_satisfactory}",
            step=2,
        ))

        await emit(ReflectionEvent.create(
            critique=result.critique,
            suggestions=result.suggestions,
            retry_number=retry_number,
            score=result.score,
        ))

        return result
