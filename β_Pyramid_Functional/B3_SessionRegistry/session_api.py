from __future__ import annotations
print("SESSION API STARTING")
"""
Session Registry API - Z9 - Beta layer.
FastAPI routes for agent-session lifecycle and Swarm Terminal streaming.
"""

import asyncio
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, List, Optional
from urllib import error as urlerror
from urllib import request as urlrequest

import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Allow sibling and workspace imports
THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parents[2]

# Discovery of pyramid layers
core_layer = None
for d in PROJECT_ROOT.iterdir():
    if not d.is_dir(): continue
    if "pyramid_core" in d.name.lower(): 
        core_layer = d
        break

if core_layer is None:
    core_layer = PROJECT_ROOT / "α_Pyramid_Core"
    if not core_layer.exists(): core_layer = PROJECT_ROOT / "\u03b1_Pyramid_Core"

# Inject critical paths
sys.path.insert(0, str(THIS_DIR))
if core_layer and core_layer.exists():
    sys.path.insert(0, str(core_layer / "B_Structure"))
sys.path.insert(0, str(THIS_DIR.parent / "B2_ProviderMatrix"))

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=False)
load_dotenv(dotenv_path=THIS_DIR / ".env", override=False)

logger = logging.getLogger(__name__)

from session_models import (
    AgentSession,
    MessageCreateRequest,
    Provider,
    SessionCreateRequest,
    SessionRegistry,
    SessionStatus,
    StatusUpdateRequest,
)
from provider_matrix import ProviderMatrix
from β_Pyramid_Functional.B1_Kernel.contracts import AgentSessionContract, TaskStatus
from β_Pyramid_Functional.B1_Kernel.ws_manager import ConnectionManager
from β_Pyramid_Functional.B2_Orchestrator.llm_orchestrator import AgentOrchestrator, _session_routing_policy
from α_Pyramid_Core.B_Structure.models import NodeStatus


app = FastAPI(
    title="EvoPyramid OS - Session Registry",
    description="Z9 - Beta layer - Agent session lifecycle management",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173", 
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


manager = ConnectionManager()





@app.post("/sessions", response_model=AgentSession, summary="Create a new agent session")
async def create_session(req: SessionCreateRequest):
    """
    Creates a new agent session bound to a pyramid node.
    Accepts an attached browser-session URL, otherwise generates one from provider matrix.
    """
    attached_url = str(req.external_url or "").strip()
    external_url = attached_url or ProviderMatrix.generate_session_url(
        req.provider, req.task_title, req.node_id
    )
    req_with_url = req.model_copy(update={"external_url": external_url})

    session = SessionRegistry.create(req_with_url)

    await manager.broadcast({
        "event": "session.created",
        "session_id": session.id,
        "node_id": session.node_id,
        "node_z": session.node_z,
        "provider": session.provider,
        "task_title": session.task_title,
        "status": session.status,
        "external_url": session.external_url,
    })
    return session


@app.get("/sessions", response_model=List[AgentSession], summary="List all sessions")
def list_sessions(node_id: Optional[str] = None):
    if node_id:
        return SessionRegistry.list_by_node(node_id)
    return SessionRegistry.list_all()


@app.get("/sessions/{session_id}", response_model=AgentSession, summary="Get session by ID")
def get_session(session_id: str):
    session = SessionRegistry.get(session_id)
    if not session:
        raise HTTPException(404, detail=f"Session {session_id} not found")
    return session


@app.get("/sessions/{session_id}/routing", summary="Inspect routing policy for a session")
def get_session_routing(session_id: str):
    session = SessionRegistry.get(session_id)
    if not session:
        raise HTTPException(404, detail=f"Session {session_id} not found")
    return _session_routing_policy(session)


@app.post(
    "/sessions/{session_id}/messages",
    response_model=AgentSession,
    summary="Add a message to session history",
)
async def add_message(session_id: str, req: MessageCreateRequest, ai: bool = False):
    """
    Adds a message. If ai=true and sender is user,
    triggers an async LLM response.
    """
    session = SessionRegistry.add_message(session_id, req)
    if not session:
        raise HTTPException(404, detail=f"Session {session_id} not found")

    await manager.broadcast({
        "event": "session.message",
        "session_id": session_id,
        "role": req.role,
        "content": req.content[:150] + ("..." if len(req.content) > 150 else ""),
        "node_id": session.node_id,
        "provider": session.provider,
    })

    if ai and req.role == "user":

        async def trigger_ai():
            await asyncio.sleep(0.5)
            ai_text = await AgentOrchestrator.get_response(session)
            if ai_text:
                from session_models import MessageCreateRequest as MCR

                SessionRegistry.add_message(
                    session_id, MCR(role="assistant", content=ai_text)
                )

                if str(ai_text).startswith("[SYSTEM QUOTA]"):
                    updated_session = SessionRegistry.update_status(
                        session_id,
                        StatusUpdateRequest(status=SessionStatus.WAITING),
                    )
                    if updated_session:
                        await manager.broadcast({
                            "event": "session.status_changed",
                            "session_id": session_id,
                            "node_id": updated_session.node_id,
                            "new_status": SessionStatus.WAITING,
                            "provider": updated_session.provider,
                        })

                text_to_send = str(ai_text or "")
                if len(text_to_send) > 500:
                    content_snippet = text_to_send[0:500] + "..."
                else:
                    content_snippet = text_to_send

                await manager.broadcast({
                    "event": "session.message",
                    "session_id": session_id,
                    "role": "assistant",
                    "content": content_snippet,
                    "node_id": session.node_id,
                    "provider": session.provider,
                })

        asyncio.create_task(trigger_ai())

    return session


@app.patch(
    "/sessions/{session_id}/status",
    response_model=AgentSession,
    summary="Update session status",
)
async def update_status(session_id: str, req: StatusUpdateRequest):
    """
    Update session status and broadcast status-change event.
    """
    session = SessionRegistry.update_status(session_id, req)
    if not session:
        raise HTTPException(404, detail=f"Session {session_id} not found")

    await manager.broadcast({
        "event": "session.status_changed",
        "session_id": session_id,
        "node_id": session.node_id,
        "new_status": req.status,
        "provider": session.provider,
    })
    return session


@app.delete("/sessions/{session_id}", summary="Delete session")
def delete_session(session_id: str):
    ok = SessionRegistry.delete(session_id)
    if not ok:
        raise HTTPException(404, detail=f"Session {session_id} not found")
    return {"deleted": session_id}


@app.get("/providers", summary="List all provider configs with visual identity")
def list_providers():
    return ProviderMatrix.all_configs()


@app.get("/providers/{provider}/url", summary="Generate session URL for provider")
def provider_url(provider: Provider, task_title: Optional[str] = None, node_id: Optional[str] = None):
    url = ProviderMatrix.generate_session_url(provider, task_title, node_id)
    cfg = ProviderMatrix.get_config(provider)
    return {
        "provider": provider,
        "name": cfg.name,
        "url": url,
        "color_primary": cfg.color_primary,
        "visual_marker": cfg.visual_marker,
    }


@app.websocket("/ws/swarm")
async def swarm_terminal(ws: WebSocket):
    """
    Swarm terminal websocket:
    - Broadcast receives session events from manager
    - Incoming {"cmd": "status"} returns active/total session counters
    """
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_json()
            if data.get("cmd") == "status":
                sessions = SessionRegistry.list_all()
                await ws.send_json({
                    "event": "status.response",
                    "active_count": sum(
                        1 for s in sessions if s.status == SessionStatus.ACTIVE
                    ),
                    "total_count": len(sessions),
                })
    except WebSocketDisconnect:
        manager.disconnect(ws)
        logger.info(f"Swarm client left. Active connections: {len(manager.active_connections)}")

@app.get("/health", summary="Health check")
def health():
    sessions = SessionRegistry.list_all()
    return {
        "status": "ok",
        "layer": "beta",
        "z_level": 9,
        "sector": "GREEN",
        "module": "session_registry",
        "sessions_total": len(sessions),
        "sessions_active": sum(1 for s in sessions if s.status == SessionStatus.ACTIVE),
        "ws_connections": len(manager.active_connections),
    }









