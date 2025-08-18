import asyncio
from typing import Tuple

async def fetch_page(url: str) -> Tuple[str, str]:
    try:
        from playwright.async_api import async_playwright  # type: ignore
    except Exception:
        return (f"Could not fetch {url}", "Unavailable")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.goto(url, timeout=15000)
            title = await page.title()
            # extract readable text
            content = await page.content()
            await browser.close()
            # naive text extraction: strip HTML tags
            import re
            text = re.sub("<[^<]+?>", " ", content)
            text = " ".join(text.split())[:4000]
            return (text or f"Fetched {url}", title or url)
    except Exception:
        return (f"Could not fetch {url}", "Unavailable")
