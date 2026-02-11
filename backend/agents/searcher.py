from __future__ import annotations

import asyncio
from typing import Any

from .base import BaseAgent, EmitFn
from ..models.research import ResearchPlan, ExtractedContent, SearchResult
from ..models.events import AgentThinkingEvent, AgentActionEvent, SearchResultsEvent
from ..tools.firecrawl_client import FirecrawlClient
from ..tools.content_extractor import ContentExtractor


class SearcherAgent(BaseAgent):
    name = "searcher"
    description = "Executes parallel web searches and scrapes results via Firecrawl"

    def __init__(self, *args, firecrawl: FirecrawlClient, content_extractor: ContentExtractor, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.firecrawl = firecrawl
        self.content_extractor = content_extractor

    async def _execute(self, input_data: Any, emit: EmitFn) -> list[ExtractedContent]:
        plan: ResearchPlan = input_data

        await emit(AgentThinkingEvent.create(
            agent_name=self.name,
            thought=f"Searching for {len(plan.decomposed_questions)} sub-questions in parallel",
            step=1,
        ))

        # Search all sub-questions in parallel
        queries = plan.decomposed_questions or [plan.original_query]

        async def search_one(query: str) -> list[ExtractedContent]:
            await emit(AgentActionEvent.create(
                agent_name=self.name,
                action="search",
                input_summary=query[:100],
            ))
            return await self.firecrawl.search_and_scrape(query, num_results=3)

        results_lists = await asyncio.gather(
            *[search_one(q) for q in queries],
            return_exceptions=True,
        )

        # Collect results, skip failures
        all_contents: list[ExtractedContent] = []
        seen_urls: set[str] = set()

        for result in results_lists:
            if isinstance(result, Exception):
                self.logger.warning(f"Search failed: {result}")
                continue
            for content in result:
                if content.url not in seen_urls:
                    seen_urls.add(content.url)
                    # Score credibility
                    content.credibility_score = self.content_extractor.score_credibility(content.url)
                    all_contents.append(content)

        await emit(AgentThinkingEvent.create(
            agent_name=self.name,
            thought=f"Found {len(all_contents)} unique sources across {len(queries)} queries",
            step=2,
        ))

        # Emit search results for frontend
        search_results = [
            SearchResult(url=c.url, title=c.title, snippet=c.content[:200])
            for c in all_contents
        ]
        await emit(SearchResultsEvent.create(results=search_results, query_used=plan.original_query))

        return all_contents
