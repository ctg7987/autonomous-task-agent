import asyncio
import os
from typing import Any, AsyncIterator, Dict, List

from .tools.search_tavily import tavily_search
from .tools.browse_playwright import fetch_page
from .tools.extractors import extract_facts
from .memory.chroma_store import upsert_snippets
from .guards.schema import validate_report_json


async def plan_node(brief: str) -> Dict[str, Any]:
    plan = {
        "query": brief.strip(),
        "steps": ["search", "read", "draft", "validate"],
    }
    return plan


async def search_node(plan: Dict[str, Any]) -> List[Dict[str, str]]:
    query = plan["query"]
    results = tavily_search(query, k=3)
    return results


async def read_node(results: List[Dict[str, str]]) -> List[Dict[str, str]]:
    pages: List[Dict[str, str]] = []
    for r in results:
        url = r.get("url", "")
        text, title = await fetch_page(url)
        pages.append({"url": url, "title": title or r.get("title", url), "text": text})
    return pages


def draft_node(pages: List[Dict[str, str]]) -> Dict[str, Any]:
    citations = []
    snippets = []
    for p in pages:
        citations.append({"title": p.get("title") or p.get("url"), "url": p.get("url")})
        facts = extract_facts(p.get("text", ""))
        for f in facts:
            snippets.append({"text": f, "url": p.get("url")})

    # memory (best-effort; if chroma missing, stub stores in-memory)
    try:
        upsert_snippets(snippets)
    except Exception:
        pass

    summary = " ".join(s.get("text") for s in snippets[:5]) or "short summary here"
    report = {
        "summary": summary.strip(),
        "citations": citations[:5],
    }
    return report


def validate_node(report: Dict[str, Any]) -> Dict[str, Any]:
    return validate_report_json(report)


async def run_graph(brief: str) -> AsyncIterator[Dict[str, Any]]:
    yield {"event": "log", "data": "Planning..."}
    plan = await plan_node(brief)

    yield {"event": "log", "data": "Searching..."}
    results = await search_node(plan)

    yield {"event": "log", "data": f"Found {len(results)} results; reading pages..."}
    pages = await read_node(results)

    yield {"event": "log", "data": "Drafting report..."}
    report = draft_node(pages)

    yield {"event": "log", "data": "Validating report..."}
    valid = validate_node(report)

    yield {"event": "report", "data": valid}
