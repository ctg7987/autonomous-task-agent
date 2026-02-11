from __future__ import annotations

from ..models.research import (
    ResearchPlan,
    SearchResult,
    ExtractedContent,
    Citation,
)
from ..logging_config import get_logger

logger = get_logger("memory.research_store")


class ResearchStore:
    """Session-scoped in-memory store shared across agents during a research run."""

    def __init__(self) -> None:
        self.plan: ResearchPlan | None = None
        self.search_results: list[SearchResult] = []
        self.extracted_contents: list[ExtractedContent] = []
        self.all_facts: list[str] = []
        self.cross_reference_results: dict[str, list[str]] = {}

    def set_plan(self, plan: ResearchPlan) -> None:
        self.plan = plan
        logger.info(f"Plan stored: {len(plan.decomposed_questions)} sub-questions")

    def add_search_results(self, results: list[SearchResult]) -> None:
        # Deduplicate by URL
        existing_urls = {r.url for r in self.search_results}
        new = [r for r in results if r.url not in existing_urls]
        self.search_results.extend(new)
        logger.info(f"Added {len(new)} search results (total: {len(self.search_results)})")

    def add_extracted_content(self, contents: list[ExtractedContent]) -> None:
        existing_urls = {c.url for c in self.extracted_contents}
        new = [c for c in contents if c.url not in existing_urls]
        self.extracted_contents.extend(new)
        for c in new:
            self.all_facts.extend(c.facts)
        logger.info(
            f"Added {len(new)} extracted contents, {len(self.all_facts)} total facts"
        )

    def set_cross_references(self, refs: dict[str, list[str]]) -> None:
        self.cross_reference_results = refs

    def get_citations(self) -> list[Citation]:
        citations = []
        for content in self.extracted_contents:
            citations.append(Citation(
                title=content.title,
                url=content.url,
                credibility_score=content.credibility_score,
                relevant_claims=content.facts[:3],
            ))
        return citations

    def get_context_summary(self) -> str:
        """Build a summary of all gathered research for the synthesizer."""
        parts = []
        if self.plan:
            parts.append(f"Original query: {self.plan.original_query}")
            parts.append(f"Sub-questions: {', '.join(self.plan.decomposed_questions)}")

        parts.append(f"\nSources analyzed: {len(self.extracted_contents)}")

        for i, content in enumerate(self.extracted_contents, 1):
            parts.append(f"\n--- Source {i}: {content.title} ({content.url}) ---")
            parts.append(f"Credibility: {content.credibility_score:.1f}")
            if content.facts:
                parts.append("Key facts:")
                for fact in content.facts[:5]:
                    parts.append(f"  - {fact}")
            elif content.content:
                parts.append(content.content[:500])

        if self.cross_reference_results.get("corroborated"):
            parts.append("\n--- Corroborated findings (multiple sources) ---")
            for f in self.cross_reference_results["corroborated"][:5]:
                parts.append(f"  * {f}")

        return "\n".join(parts)

    def clear(self) -> None:
        self.__init__()
