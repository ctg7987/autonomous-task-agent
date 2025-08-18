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

Project structure:

```
.
├─ backend/
│  ├─ app.py
│  ├─ graph.py
│  ├─ tools/
│  │  ├─ search_tavily.py
│  │  ├─ browse_playwright.py
│  │  └─ extractors.py
│  ├─ memory/
│  │  └─ chroma_store.py
│  ├─ guards/
│  │  └─ schema.py
│  ├─ tracing/
│  │  └─ langfuse_client.py
│  ├─ requirements.txt
│  ├─ pyproject.toml
│  └─ README.md
├─ frontend/
│  ├─ package.json
│  ├─ package-lock.json
│  ├─ next.config.mjs
│  ├─ tsconfig.json
│  ├─ next-env.d.ts
│  └─ app/
│     ├─ layout.tsx
│     └─ page.tsx
├─ infra/
│  ├─ Dockerfile.backend
│  ├─ docker-compose.yml
│  ├─ .env.example
│  └─ README.md
├─ .gitignore
├─ LICENSE
└─ README.md
```

How to use the UI: enter a brief, click Run, watch logs and the final report with clickable sources.