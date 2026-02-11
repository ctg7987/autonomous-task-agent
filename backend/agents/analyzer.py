from __future__ import annotations

import asyncio
from typing import Any

from .base import BaseAgent, EmitFn
from ..models.research import ExtractedContent
from ..models.events import AgentThinkingEvent, AgentActionEvent
from ..tools.content_extractor import ContentExtractor


class AnalyzerAgent(BaseAgent):
    name = "analyzer"
    description = "Analyzes scraped content, extracts facts, and cross-references claims"

    def __init__(self, *args, content_extractor: ContentExtractor, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.content_extractor = content_extractor

    async def _execute(self, input_data: Any, emit: EmitFn) -> dict:
        contents: list[ExtractedContent] = input_data["contents"]
        query: str = input_data["query"]

        await emit(AgentThinkingEvent.create(
            agent_name=self.name,
            thought=f"Analyzing {len(contents)} sources for relevant facts",
            step=1,
        ))

        # Extract facts from each source in parallel
        async def extract_one(content: ExtractedContent) -> ExtractedContent:
            await emit(AgentActionEvent.create(
                agent_name=self.name,
                action="extract_facts",
                input_summary=f"Extracting from: {content.title[:60]}",
            ))
            facts = await self.content_extractor.extract_facts(content, query)
            content.facts = facts
            return content

        analyzed = await asyncio.gather(
            *[extract_one(c) for c in contents],
            return_exceptions=True,
        )

        valid_contents = [c for c in analyzed if isinstance(c, ExtractedContent)]

        await emit(AgentThinkingEvent.create(
            agent_name=self.name,
            thought=f"Extracted facts from {len(valid_contents)} sources. Cross-referencing...",
            step=2,
        ))

        # Cross-reference facts
        facts_by_source = {}
        for c in valid_contents:
            if c.facts:
                facts_by_source[c.url] = c.facts

        cross_refs = await self.content_extractor.cross_reference(facts_by_source)

        corroborated_count = len(cross_refs.get("corroborated", []))
        await emit(AgentThinkingEvent.create(
            agent_name=self.name,
            thought=f"Analysis complete: {corroborated_count} corroborated findings across sources",
            step=3,
        ))

        return {
            "contents": valid_contents,
            "cross_references": cross_refs,
            "query": query,
        }
