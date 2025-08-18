import asyncio
import json
import os
from typing import AsyncIterator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .graph import run_graph

app = FastAPI(title="Autonomous Multi-Tool AI Task Agent")

# Allow local dev from Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Brief(BaseModel):
    text: str


async def stream_run(brief: str) -> AsyncIterator[dict]:
    async for evt in run_graph(brief):
        yield evt


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        # Wait for initial brief message from client
        init = await ws.receive_text()
        try:
            data = json.loads(init)
            brief = data.get("brief") or data.get("text") or ""
        except Exception:
            brief = init

        if not brief:
            await ws.send_text(json.dumps({"event": "log", "data": "No brief provided; using default demo brief."}))
            brief = "Summarize a couple of AI news items with citations."

        await ws.send_text(json.dumps({"event": "log", "data": f"Starting run for brief: {brief[:120]}"}))

        async for evt in stream_run(brief):
            await ws.send_text(json.dumps(evt))

        await ws.close()
    except WebSocketDisconnect:
        # Client disconnected; nothing else to do
        return
    except Exception as e:
        await ws.send_text(json.dumps({"event": "log", "data": f"Error: {e}"}))
        await ws.close()


@app.get("/")
async def root():
    return {"status": "ok", "ws": "/ws"}
