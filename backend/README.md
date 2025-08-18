# Backend (FastAPI + minimal agent)

Run locally:

1. Create venv and install deps
   - python -m venv venv && source venv/bin/activate
   - pip install -r backend/requirements.txt
2. Install browser for Playwright (optional, fallback stubs exist)
   - playwright install chromium
3. Start server
   - uvicorn backend.app:app --reload

WebSocket endpoint: ws://localhost:8000/ws
- Send a text message or JSON {"brief":"..."}
- You'll receive log events {"event":"log","data":"..."}
- When complete, you'll get {"event":"report","data":{summary, citations}}

Env vars (optional):
- TAVILY_API_KEY: enable real web search
- LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY / LANGFUSE_HOST: enable Langfuse (stubbed)

Works without keys using mock search/fetch.
