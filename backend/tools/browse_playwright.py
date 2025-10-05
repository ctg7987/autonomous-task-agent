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
            resp = await page.goto(url, timeout=20000, wait_until="domcontentloaded")
            title = await page.title()
            # extract readable text
            content = await page.content()
            await browser.close()
            # naive text extraction: strip HTML tags
            import re
            text = re.sub("<[^<]+?>", " ", content)
            text = " ".join(text.split())[:4000]
            # If the page looks like an error page, mark the title accordingly
            lower = (title or "").lower()
            status = resp.status if resp else 200
            if status >= 400 or any(k in lower for k in ["error", "not found", "access denied", "forbidden"]):
                clean_title = (title or url) + " (May be an error page)"
                return (text or f"Fetched {url}", clean_title)
            return (text or f"Fetched {url}", title or url)
    except Exception:
        return (f"Could not fetch {url}", "Unavailable")
