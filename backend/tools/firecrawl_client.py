from __future__ import annotations

import asyncio
from typing import Optional

import httpx

from ..models.research import SearchResult, ExtractedContent
from ..resilience import retry, circuit_breaker
from ..logging_config import get_logger

logger = get_logger("tools.firecrawl")

FIRECRAWL_BASE_URL = "https://api.firecrawl.dev/v1"


class FirecrawlClient:
    def __init__(self, api_key: str, max_concurrent: int = 5) -> None:
        self._api_key = api_key
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            headers=self._headers,
            timeout=httpx.Timeout(30.0, connect=10.0),
        )

    @retry(max_attempts=3, base_delay=1.0, retry_on=(httpx.HTTPError, httpx.TimeoutException))
    @circuit_breaker(name="firecrawl_search", failure_threshold=5, recovery_timeout=60.0)
    async def search(self, query: str, num_results: int = 5) -> list[SearchResult]:
        """Search the web via Firecrawl and return results."""
        logger.info(f"Searching for: {query!r} (limit={num_results})")
        async with self._client() as client:
            resp = await client.post(
                f"{FIRECRAWL_BASE_URL}/search",
                json={
                    "query": query,
                    "limit": num_results,
                    "scrapeOptions": {"formats": ["markdown"]},
                },
            )
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("data", []):
            results.append(SearchResult(
                url=item.get("url", ""),
                title=item.get("metadata", {}).get("title", item.get("url", "")),
                snippet=item.get("metadata", {}).get("description", ""),
                raw_content=item.get("markdown", ""),
            ))
        logger.info(f"Search returned {len(results)} results")
        return results[:num_results]

    @retry(max_attempts=2, base_delay=1.0, retry_on=(httpx.HTTPError, httpx.TimeoutException))
    @circuit_breaker(name="firecrawl_scrape", failure_threshold=5, recovery_timeout=60.0)
    async def scrape(self, url: str) -> ExtractedContent:
        """Scrape a single URL and extract content as markdown."""
        async with self._semaphore:
            logger.info(f"Scraping: {url}")
            async with self._client() as client:
                resp = await client.post(
                    f"{FIRECRAWL_BASE_URL}/scrape",
                    json={
                        "url": url,
                        "formats": ["markdown"],
                    },
                )
                resp.raise_for_status()
                data = resp.json()

            page_data = data.get("data", {})
            return ExtractedContent(
                url=url,
                title=page_data.get("metadata", {}).get("title", url),
                content=page_data.get("markdown", ""),
                extraction_method="firecrawl_scrape",
            )

    async def scrape_many(self, urls: list[str]) -> list[ExtractedContent]:
        """Scrape multiple URLs in parallel with concurrency control."""
        logger.info(f"Scraping {len(urls)} URLs in parallel")

        async def _safe_scrape(url: str) -> Optional[ExtractedContent]:
            try:
                return await self.scrape(url)
            except Exception as e:
                logger.warning(f"Failed to scrape {url}: {e}")
                return None

        results = await asyncio.gather(*[_safe_scrape(u) for u in urls])
        return [r for r in results if r is not None]

    async def search_and_scrape(self, query: str, num_results: int = 5) -> list[ExtractedContent]:
        """Combined search + scrape: search for query, then scrape each result."""
        search_results = await self.search(query, num_results)

        # If search returned markdown content, use it directly
        contents = []
        urls_to_scrape = []
        for sr in search_results:
            if sr.raw_content and len(sr.raw_content) > 100:
                contents.append(ExtractedContent(
                    url=sr.url,
                    title=sr.title,
                    content=sr.raw_content,
                    extraction_method="firecrawl_search",
                ))
            else:
                urls_to_scrape.append(sr.url)

        # Scrape any results that didn't include content
        if urls_to_scrape:
            scraped = await self.scrape_many(urls_to_scrape)
            contents.extend(scraped)

        return contents
