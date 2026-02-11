from __future__ import annotations

import re
from urllib.parse import urlparse
from typing import Optional

from ..models.research import ExtractedContent
from ..providers.base import LLMProvider
from ..logging_config import get_logger

logger = get_logger("tools.content_extractor")

# Domain authority scores for credibility heuristics
DOMAIN_AUTHORITY = {
    ".edu": 0.9,
    ".gov": 0.9,
    ".org": 0.7,
    "nature.com": 0.95,
    "science.org": 0.95,
    "arxiv.org": 0.85,
    "ieee.org": 0.85,
    "acm.org": 0.85,
    "reuters.com": 0.85,
    "bbc.com": 0.8,
    "bbc.co.uk": 0.8,
    "nytimes.com": 0.8,
    "washingtonpost.com": 0.8,
    "wikipedia.org": 0.7,
}


class ContentExtractor:
    def __init__(self, provider: Optional[LLMProvider] = None, model: str = "") -> None:
        self.provider = provider
        self.model = model

    async def extract_facts(
        self, content: ExtractedContent, query: str
    ) -> list[str]:
        """Extract key facts from content using LLM or fallback to heuristics."""
        if self.provider and self.model:
            return await self._llm_extract_facts(content, query)
        return self._heuristic_extract_facts(content.content, query)

    async def _llm_extract_facts(
        self, content: ExtractedContent, query: str
    ) -> list[str]:
        """Use LLM to extract relevant facts."""
        text = content.content[:4000]  # Limit context size
        system = "You are a research analyst. Extract key facts from the provided text that are relevant to the research query. Return a JSON array of strings, each being a concise factual statement."
        user = f"Research query: {query}\n\nSource ({content.url}):\n{text}\n\nExtract 3-8 key relevant facts as a JSON array of strings."

        try:
            raw = await self.provider.complete(
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=1024,
            )
            # Parse JSON array from response
            raw = raw.strip()
            if raw.startswith("```"):
                lines = raw.split("\n")[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                raw = "\n".join(lines)

            import json
            facts = json.loads(raw)
            if isinstance(facts, list):
                return [str(f) for f in facts if isinstance(f, str) and len(f) > 10]
        except Exception as e:
            logger.warning(f"LLM fact extraction failed: {e}, falling back to heuristic")

        return self._heuristic_extract_facts(content.content, query)

    def _heuristic_extract_facts(self, text: str, query: str) -> list[str]:
        """Fallback: extract facts using sentence splitting and keyword matching."""
        # Clean markdown artifacts
        clean = re.sub(r'#+\s', '', text)
        clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean)
        clean = re.sub(r'[*_`~]', '', clean)
        clean = re.sub(r'\n{2,}', '\n', clean)

        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', clean)
        query_terms = set(query.lower().split())

        facts = []
        for s in sentences:
            s = s.strip()
            if len(s) < 30 or len(s) > 500:
                continue
            # Score by query term overlap
            words = set(s.lower().split())
            overlap = len(query_terms & words)
            if overlap > 0 or len(facts) < 3:
                facts.append(s)
            if len(facts) >= 8:
                break

        return facts

    def score_credibility(self, url: str) -> float:
        """Score source credibility based on domain authority."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().lstrip("www.")

            # Check exact domain matches
            for known_domain, score in DOMAIN_AUTHORITY.items():
                if known_domain.startswith("."):
                    if domain.endswith(known_domain):
                        return score
                elif known_domain in domain:
                    return score

            # HTTPS gives slight boost
            base = 0.5
            if parsed.scheme == "https":
                base += 0.05

            return min(base, 1.0)
        except Exception:
            return 0.3

    async def cross_reference(
        self, facts_by_source: dict[str, list[str]]
    ) -> dict[str, list[str]]:
        """Identify facts that appear across multiple sources."""
        corroborated = []
        single_source = []

        all_facts = []
        for url, facts in facts_by_source.items():
            for f in facts:
                all_facts.append((url, f))

        # Simple overlap detection using keyword matching
        for i, (url1, fact1) in enumerate(all_facts):
            words1 = set(fact1.lower().split())
            found_corroboration = False
            for j, (url2, fact2) in enumerate(all_facts):
                if i == j or url1 == url2:
                    continue
                words2 = set(fact2.lower().split())
                overlap = len(words1 & words2)
                if overlap >= 3 and overlap / min(len(words1), len(words2)) > 0.3:
                    if fact1 not in corroborated:
                        corroborated.append(fact1)
                    found_corroboration = True
                    break
            if not found_corroboration and fact1 not in single_source:
                single_source.append(fact1)

        return {
            "corroborated": corroborated,
            "single_source": single_source,
        }
