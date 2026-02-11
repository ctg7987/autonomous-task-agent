from __future__ import annotations

from typing import Any

from .base import BaseAgent, EmitFn
from ..models.research import ResearchPlan
from ..models.events import AgentThinkingEvent, PlanEvent


class PlannerAgent(BaseAgent):
    name = "planner"
    description = "Decomposes research queries into sub-questions and search strategies"

    async def _execute(self, input_data: Any, emit: EmitFn) -> ResearchPlan:
        query = str(input_data)

        await emit(AgentThinkingEvent.create(
            agent_name=self.name,
            thought=f"Analyzing query: '{query}' — decomposing into sub-questions and choosing search strategies",
            step=1,
        ))

        system_prompt = """You are a research planning expert. Given a research query, create a detailed research plan.

Return valid JSON with exactly these fields:
- original_query: the original query string
- decomposed_questions: array of 2-4 specific sub-questions that together answer the main query
- search_strategies: array of 2-3 search strategy descriptions (e.g., "search academic sources", "find recent news")
- expected_source_types: array of expected source types (e.g., "academic papers", "news articles", "official documentation")

Be specific and actionable. Each sub-question should target a different aspect of the topic."""

        user_prompt = f"Create a research plan for this query: {query}"

        plan = await self._llm_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=ResearchPlan,
            temperature=0.3,
            max_tokens=1024,
        )

        # Ensure original_query is set
        plan.original_query = query

        await emit(AgentThinkingEvent.create(
            agent_name=self.name,
            thought=f"Created plan with {len(plan.decomposed_questions)} sub-questions",
            step=2,
        ))
        await emit(PlanEvent.create(plan))

        return plan
