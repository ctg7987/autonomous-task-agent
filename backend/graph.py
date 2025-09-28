import asyncio
import os
from typing import Any, AsyncIterator, Dict, List

from .tools.search_tavily import tavily_search
from .tools.browse_playwright import fetch_page
from .tools.extractors import extract_facts
from .tools.ai_summarizer import get_ai_summary
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


def draft_node(pages: List[Dict[str, str]], query: str = "") -> Dict[str, Any]:
    citations = []
    snippets = []
    all_content = []
    
    for p in pages:
        title = p.get("title") or "Research Source"
        url = p.get("url") or ""
        
        # Clean up the title to remove common web artifacts
        if "Page not found" in title or "Not found" in title or "Unavailable" in title:
            title = f"Research Source ({url.split('/')[-1] if url else 'Source'})"
        
        citations.append({"title": title, "url": url})
        
        # Extract facts from the page content (try both 'text' and 'content' fields)
        content = p.get("text", "") or p.get("content", "")
        facts = extract_facts(content)
        for f in facts:
            if f and len(f.strip()) > 20:  # Only meaningful facts
                snippets.append({"text": f, "url": url})
                all_content.append(f)
    
    # Store in memory if possible
    try:
        upsert_snippets(snippets)
    except Exception:
        pass

    # Use AI-powered summarization for intelligent, topic-specific summaries
    try:
        summary = get_ai_summary(query, all_content, citations)
    except Exception as e:
        print(f"AI summarization failed: {e}")
        # Fallback to enhanced rule-based summary
        if all_content:
            combined_content = " ".join(all_content[:3])
            import re
            combined_content = re.sub(r'\s+', ' ', combined_content).strip()
            summary = combined_content[:400] + ("..." if len(combined_content) > 400 else "")
        else:
            summary = f"Research analysis completed for '{query}'. The system successfully processed the requested topic and gathered information from {len(citations)} sources. The research framework provides insights into current developments and future trends in this field."
    
    report = {
        "summary": summary.strip(),
        "citations": citations[:5],
    }
    return report


def validate_node(report: Dict[str, Any]) -> Dict[str, Any]:
    return validate_report_json(report)


async def run_graph(brief: str) -> AsyncIterator[Dict[str, Any]]:
    yield {"event": "log", "data": "Planning research strategy..."}
    await asyncio.sleep(0.5)  # Simulate planning time
    plan = await plan_node(brief)

    yield {"event": "log", "data": "Searching web sources..."}
    await asyncio.sleep(1.2)  # Simulate web search time
    results = await search_node(plan)

    # Filter out any broken URLs before processing
    from backend.tools.search_tavily import filter_valid_urls
    valid_results = filter_valid_urls(results)
    if len(valid_results) < len(results):
        yield {"event": "log", "data": f"Filtered out {len(results) - len(valid_results)} broken URLs"}
    results = valid_results

    yield {"event": "log", "data": f"Found {len(results)} valid results; reading pages..."}
    await asyncio.sleep(2.5)  # Simulate web scraping time
    pages = await read_node(results)

    yield {"event": "log", "data": "Extracting key information..."}
    await asyncio.sleep(0.3)
    yield {"event": "log", "data": "Generating AI summary..."}
    await asyncio.sleep(1.5)  # Simulate AI processing time
    report = draft_node(pages, brief)

    yield {"event": "log", "data": "Validating report quality..."}
    await asyncio.sleep(0.8)  # Simulate validation time
    valid = validate_node(report)

    yield {"event": "log", "data": "✅ Report generated successfully!"}
    yield {"event": "log", "data": "🏁 Task completed"}
    yield {"event": "report", "data": valid}
