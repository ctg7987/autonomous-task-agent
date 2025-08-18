import os
from typing import List, Dict

try:
    from tavily import TavilyClient  # type: ignore
except Exception:  # library may be missing
    TavilyClient = None  # type: ignore


def tavily_search(query: str, k: int = 5) -> List[Dict[str, str]]:
    api_key = os.getenv("TAVILY_API_KEY")
    if api_key and TavilyClient is not None:
        try:
            client = TavilyClient(api_key=api_key)
            res = client.search(query=query, search_depth="basic", max_results=k)
            out: List[Dict[str, str]] = []
            for it in res.get("results", [])[:k]:
                out.append({
                    "url": it.get("url", ""),
                    "title": it.get("title", it.get("url", "")),
                    "content": it.get("content", ""),
                })
            if out:
                return out
        except Exception:
            pass

    # Fallback mock results
    return [
        {
            "url": "https://example.com/ai-news-1",
            "title": "AI News One",
            "content": "Recent developments in AI...",
        },
        {
            "url": "https://example.com/ai-news-2",
            "title": "AI News Two",
            "content": "Another update in the AI space...",
        },
        {
            "url": "https://example.com/ai-news-3",
            "title": "AI News Three",
            "content": "More AI headlines...",
        },
    ][:k]
