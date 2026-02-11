from __future__ import annotations

import asyncio
from typing import AsyncGenerator

from ..config import Settings, get_settings
from ..models.events import (
    SSEEvent,
    StatusEvent,
    ErrorEvent,
    DoneEvent,
    AgentThinkingEvent,
)
from ..models.research import ResearchReport
from ..providers.registry import get_provider_for_agent
from ..tools.firecrawl_client import FirecrawlClient
from ..tools.content_extractor import ContentExtractor
from ..memory.research_store import ResearchStore
from ..logging_config import get_logger

from .planner import PlannerAgent
from .searcher import SearcherAgent
from .analyzer import AnalyzerAgent
from .synthesizer import SynthesizerAgent
from .critic import CriticAgent

logger = get_logger("agents.supervisor")


class Supervisor:
    """Orchestrates the multi-agent research pipeline with reflection loops."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    async def run(
        self,
        query: str,
        cancel_event: asyncio.Event | None = None,
    ) -> AsyncGenerator[SSEEvent, None]:
        """Run the full research pipeline, yielding SSE events."""
        store = ResearchStore()
        events: list[SSEEvent] = []

        async def emit(event: SSEEvent) -> None:
            events.append(event)

        def _cancelled() -> bool:
            return cancel_event is not None and cancel_event.is_set()

        try:
            # Initialize tools
            firecrawl = FirecrawlClient(
                api_key=self.settings.firecrawl_api_key,
                max_concurrent=self.settings.max_concurrent_fetches,
            )
            content_extractor = ContentExtractor()

            # --- Phase 1: Planning ---
            yield StatusEvent.create(phase="planning", progress=0.0, active_agent="planner")
            if _cancelled():
                return

            planner_provider, planner_model = get_provider_for_agent("planner")
            planner = PlannerAgent(provider=planner_provider, model=planner_model)
            plan = await planner.run(query, emit)
            for e in events:
                yield e
            events.clear()
            store.set_plan(plan)

            # --- Phase 2: Searching ---
            yield StatusEvent.create(phase="searching", progress=0.2, active_agent="searcher")
            if _cancelled():
                return

            searcher_provider, searcher_model = get_provider_for_agent("searcher")
            # Give content extractor a provider for LLM-based extraction
            analyzer_provider, analyzer_model = get_provider_for_agent("analyzer")
            content_extractor = ContentExtractor(provider=analyzer_provider, model=analyzer_model)

            searcher = SearcherAgent(
                provider=searcher_provider,
                model=searcher_model,
                firecrawl=firecrawl,
                content_extractor=content_extractor,
            )
            contents = await searcher.run(plan, emit)
            for e in events:
                yield e
            events.clear()
            store.add_extracted_content(contents)

            if not contents:
                yield ErrorEvent.create("No sources found. Try a different query.")
                yield DoneEvent()
                return

            # --- Phase 3: Analysis ---
            yield StatusEvent.create(phase="analyzing", progress=0.4, active_agent="analyzer")
            if _cancelled():
                return

            analyzer = AnalyzerAgent(
                provider=analyzer_provider,
                model=analyzer_model,
                content_extractor=content_extractor,
            )
            analysis = await analyzer.run(
                {"contents": contents, "query": query},
                emit,
            )
            for e in events:
                yield e
            events.clear()

            # Update store with analysis results
            store.add_extracted_content(analysis["contents"])
            store.set_cross_references(analysis["cross_references"])

            # --- Phase 4: Synthesis + Reflection Loop ---
            synth_provider, synth_model = get_provider_for_agent("synthesizer")
            critic_provider, critic_model = get_provider_for_agent("critic")

            synthesizer = SynthesizerAgent(provider=synth_provider, model=synth_model)
            critic = CriticAgent(provider=critic_provider, model=critic_model)

            critique_text = ""
            report: ResearchReport | None = None

            for retry in range(self.settings.max_reflection_retries + 1):
                if _cancelled():
                    return

                # Synthesize
                progress = 0.6 + (retry * 0.1)
                yield StatusEvent.create(
                    phase="synthesizing",
                    progress=min(progress, 0.9),
                    active_agent="synthesizer",
                )

                report = await synthesizer.run(
                    {"store": store, "critique": critique_text},
                    emit,
                )
                for e in events:
                    yield e
                events.clear()

                # Critique (skip on last iteration)
                if retry < self.settings.max_reflection_retries:
                    yield StatusEvent.create(
                        phase="reflecting",
                        progress=min(progress + 0.05, 0.9),
                        active_agent="critic",
                    )

                    reflection = await critic.run(
                        {"report": report, "query": query, "retry_number": retry},
                        emit,
                    )
                    for e in events:
                        yield e
                    events.clear()

                    if reflection.is_satisfactory:
                        logger.info(f"Report accepted by critic (score={reflection.score:.2f})")
                        break

                    critique_text = (
                        f"{reflection.critique}\nSuggestions: {', '.join(reflection.suggestions)}"
                    )
                    logger.info(f"Report rejected (score={reflection.score:.2f}), revising...")

            # --- Done ---
            yield StatusEvent.create(phase="done", progress=1.0, active_agent="")
            yield DoneEvent()

        except asyncio.CancelledError:
            logger.info("Research cancelled")
            yield ErrorEvent.create("Research was cancelled")
        except Exception as e:
            logger.error(f"Supervisor error: {e}", exc_info=True)
            yield ErrorEvent.create(f"Research failed: {str(e)}")
            yield DoneEvent()
