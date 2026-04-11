from __future__ import annotations
import logging
# Session Registry API - Z9 - Beta layer.
logger = logging.getLogger(__name__)
logger.info("SESSION API STARTING")
"""
FastAPI routes for agent-session lifecycle and Swarm Terminal streaming.
"""

import asyncio
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, List, Optional
from urllib import error as urlerror
from urllib import request as urlrequest


from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

# Allow sibling and workspace imports
THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parents[1]

# Discovery of pyramid layers
core_layer = None
for d in PROJECT_ROOT.iterdir():
    if not d.is_dir(): continue
    if "pyramid_core" in d.name.lower(): 
        core_layer = d
        break

if core_layer is None:
    core_layer = PROJECT_ROOT / "alpha_pyramid_core"

# Inject critical paths
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

sys.path.insert(0, str(THIS_DIR))
if core_layer and core_layer.exists():
    sys.path.insert(0, str(core_layer / "B_Structure"))
sys.path.insert(0, str(THIS_DIR.parent / "B2_ProviderMatrix"))

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
    MemoryCrystal,
    CrystalManager,
    CrystalScope,
)
from provider_matrix import ProviderMatrix
from beta_pyramid_functional.B1_Kernel.contracts import AgentSessionContract, TaskStatus
from beta_pyramid_functional.B1_Kernel.ws_manager import manager
from beta_pyramid_functional.B2_Orchestrator.llm_orchestrator import AgentOrchestrator, _session_routing_policy
from alpha_pyramid_core.B_Structure.models import NodeState


router = APIRouter(prefix="/v1", tags=["sessions"])


# manager = ConnectionManager() - Now using singleton export





@router.post("/sessions", response_model=AgentSession, summary="Create a new agent session")
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


@router.get("/sessions", response_model=List[AgentSession], summary="List all sessions")
def list_sessions(node_id: Optional[str] = None):
    if node_id:
        return SessionRegistry.list_by_node(node_id)
    return SessionRegistry.list_all()


@router.get("/sessions/{session_id}", response_model=AgentSession, summary="Get session by ID")
def get_session(session_id: str):
    session = SessionRegistry.get(session_id)
    if not session:
        raise HTTPException(404, detail=f"Session {session_id} not found")
    return session


@router.get("/sessions/{session_id}/routing", summary="Inspect routing policy for a session")
def get_session_routing(session_id: str):
    session = SessionRegistry.get(session_id)
    if not session:
        raise HTTPException(404, detail=f"Session {session_id} not found")
    return _session_routing_policy(session)


@router.post(
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

                _is_system_pause = (
                    str(ai_text).startswith("[SYSTEM QUOTA]")
                    or str(ai_text).startswith("[SYSTEM FALLBACK]")
                )
                if _is_system_pause:
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


@router.patch(
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


@router.delete("/sessions/{session_id}", summary="Delete session")
def delete_session(session_id: str):
    ok = SessionRegistry.delete(session_id)
    if not ok:
        raise HTTPException(404, detail=f"Session {session_id} not found")
    return {"deleted": session_id}


@router.get("/providers", summary="List all provider configs with visual identity")
def list_providers():
    return ProviderMatrix.all_configs()


@router.get("/providers/{provider}/url", summary="Generate session URL for provider")
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


@router.websocket("/ws/swarm")
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

@router.get("/health", summary="Health check")
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


# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
#  Memory Crystals API 
# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

@router.post("/memory/crystal", response_model=MemoryCrystal, summary="Create a new Memory Crystal")
def create_crystal(crystal: MemoryCrystal):
    """
    Stores a new memory crystal (container) with the essence of a session or task.
    """
    return CrystalManager.create(crystal)


@router.get("/memory/crystals", response_model=List[MemoryCrystal], summary="List all Memory Crystals")
def list_crystals(scope: Optional[CrystalScope] = None):
    """
    Lists Memory Crystals, optionally filtered by scope.
    """
    if scope:
        return CrystalManager.list_by_scope(scope)
    return CrystalManager.list_all()


@router.delete("/memory/crystals/{crystal_id}", summary="Delete a Memory Crystal")
def delete_crystal(crystal_id: str):
    """
    Deletes a specific memory crystal.
    """
    ok = CrystalManager.delete(crystal_id)
    if not ok:
        raise HTTPException(404, detail=f"Crystal {crystal_id} not found")
    return {"deleted": crystal_id}








