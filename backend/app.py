from __future__ import annotations

import asyncio
import json
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

from .config import get_settings
from .logging_config import setup_logging, get_logger
from .agents.supervisor import Supervisor


logger = get_logger("app")

# Active research runs (for cancellation)
_active_runs: dict[str, asyncio.Event] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    setup_logging(settings.log_level)
    logger.info("Server starting up")

    # Validate at least one provider is available
    try:
        _ = settings.active_provider
        logger.info(f"Default LLM provider: {settings.active_provider}")
    except ValueError as e:
        logger.warning(f"No LLM provider configured: {e}")

    if settings.firecrawl_api_key:
        logger.info("Firecrawl API key configured")
    else:
        logger.warning("No FIRECRAWL_API_KEY — search/scrape will fail")

    yield

    logger.info("Server shutting down")


app = FastAPI(
    title="Autonomous AI Research Agent",
    lifespan=lifespan,
)

# CORS
settings = get_settings()
origins = [o.strip() for o in settings.allowed_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)


class HealthResponse(BaseModel):
    status: str
    provider: str | None = None
    firecrawl: bool = False


# --- Endpoints ---


@app.get("/api/health")
async def health() -> HealthResponse:
    settings = get_settings()
    provider = None
    try:
        provider = settings.active_provider
    except ValueError:
        pass
    return HealthResponse(
        status="ok",
        provider=provider,
        firecrawl=bool(settings.firecrawl_api_key),
    )


@app.get("/")
async def root():
    return {"status": "ok", "docs": "/docs", "health": "/api/health"}


@app.post("/api/research")
async def research(request: ResearchRequest):
    """Start a research run, returning an SSE stream of events."""
    run_id = str(uuid.uuid4())
    cancel_event = asyncio.Event()
    _active_runs[run_id] = cancel_event

    async def event_stream() -> AsyncGenerator[str, None]:
        try:
            supervisor = Supervisor()
            async for event in supervisor.run(request.query, cancel_event=cancel_event):
                payload = event.model_dump(mode="json")
                # Include run_id in each event
                payload["run_id"] = run_id
                yield f"data: {json.dumps(payload)}\n\n"
        except asyncio.CancelledError:
            yield f'data: {json.dumps({"event": "error", "data": {"message": "Cancelled"}, "run_id": run_id})}\n\n'
        except Exception as e:
            logger.error(f"Research stream error: {e}", exc_info=True)
            yield f'data: {json.dumps({"event": "error", "data": {"message": str(e)}, "run_id": run_id})}\n\n'
        finally:
            _active_runs.pop(run_id, None)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Run-Id": run_id,
        },
    )


@app.post("/api/research/{run_id}/stop")
async def stop_research(run_id: str):
    """Cancel a running research task."""
    cancel = _active_runs.get(run_id)
    if cancel:
        cancel.set()
        return {"status": "cancelled", "run_id": run_id}
    return {"status": "not_found", "run_id": run_id}
