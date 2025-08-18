# Autonomous Multi-Tool AI Task Agent

Minimal full-stack MVP: FastAPI backend + Next.js frontend. Streams logs over WebSocket and returns a final JSON report with citations. Works offline via mock search/fetch.

Quickstart:

```bash
# Backend
python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
playwright install chromium
uvicorn backend.app:app --reload

# Frontend
cd frontend && npm install && npm run dev
```

How to use the UI: enter a brief, click Run, watch logs and the final report with clickable sources.