from __future__ import annotations

from typing import Any

from .base import BaseAgent, EmitFn
from ..models.research import ResearchReport, Citation
from ..models.events import AgentThinkingEvent, ReportEvent
from ..memory.research_store import ResearchStore


class SynthesizerAgent(BaseAgent):
    name = "synthesizer"
    description = "Generates a structured research report from analyzed content"

    async def _execute(self, input_data: Any, emit: EmitFn) -> ResearchReport:
        store: ResearchStore = input_data["store"]
        critique: str = input_data.get("critique", "")

        context = store.get_context_summary()
        citations = store.get_citations()

        revision_note = ""
        if critique:
            revision_note = f"\n\nPREVIOUS CRITIQUE TO ADDRESS:\n{critique}\nPlease improve the report based on this feedback."

        await emit(AgentThinkingEvent.create(
            agent_name=self.name,
            thought="Synthesizing research findings into a comprehensive report"
            + (" (addressing critique)" if critique else ""),
            step=1,
        ))

        system_prompt = """You are an expert research analyst. Synthesize the provided research data into a comprehensive report.

Return valid JSON with exactly these fields:
- summary: A well-written 200-400 word executive summary of the research findings. Be specific, cite sources by name.
- key_findings: Array of 4-6 bullet-point findings (each a concise string). Start each with a strong claim.
- confidence_score: Float 0.0-1.0 indicating confidence in the findings. Higher if multiple sources corroborate.
- methodology_note: One sentence describing how the research was conducted (e.g., "Analysis of N sources including...")

Do NOT include citations in the JSON — they are handled separately.
Be factual. Reference specific data points from the sources. Avoid vague statements."""

        user_prompt = f"""Research context:
{context}

Available citations: {len(citations)} sources
{revision_note}

Generate the research report as JSON."""

        report = await self._llm_structured(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=ResearchReport,
            temperature=0.3,
            max_tokens=2048,
        )

        # Attach citations from store
        report.citations = citations

        await emit(AgentThinkingEvent.create(
            agent_name=self.name,
            thought=f"Report generated: {len(report.key_findings)} findings, confidence={report.confidence_score:.2f}",
            step=2,
        ))
        await emit(ReportEvent.create(report))

        return report
