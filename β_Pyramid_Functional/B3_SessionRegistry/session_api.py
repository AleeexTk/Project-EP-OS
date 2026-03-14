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


app = FastAPI(
    title="EvoPyramid OS - Session Registry",
    description="Z9 - Beta layer - Agent session lifecycle management",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, data: dict):
        for ws in list(self.active):
            try:
                await ws.send_json(data)
            except Exception:
                if ws in self.active:
                    self.active.remove(ws)


manager = ConnectionManager()


_GEMINI_MODEL_CACHE: Optional[str] = None
_GEMINI_MODEL_LOCK = asyncio.Lock()
_GEMINI_QUOTA_BLOCK_UNTIL = 0.0
_GEMINI_QUOTA_BLOCK_REASON = ""
_PREFERRED_GEMINI_MODELS = (
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
)
_OLLAMA_MODEL_CACHE: Optional[str] = None
_OLLAMA_MODEL_LOCK = asyncio.Lock()
_PREFERRED_OLLAMA_MODELS = (
    "qwen2.5:7b",
    "llama3.2:3b",
    "llama3.1:8b",
    "mistral:7b",
    "gemma3:4b",
)

def _normalize_model_name(raw_name: Any) -> Optional[str]:
    if raw_name is None:
        return None
    value = str(raw_name).strip()
    if not value:
        return None
    if "/" in value:
        value = value.split("/")[-1]
    return value


def _supports_generate_content(model: Any) -> bool:
    methods = getattr(model, "supported_generation_methods", None)
    if not methods:
        return True
    return any("generatecontent" in str(method).lower() for method in methods)


def _model_names_from_registry(models: List[Any]) -> List[str]:
    names: List[str] = []
    for model in models:
        if not _supports_generate_content(model):
            continue
        raw_name = getattr(model, "name", None) or getattr(model, "model_name", None)
        normalized = _normalize_model_name(raw_name)
        if normalized and normalized not in names:
            names.append(normalized)
    return names


async def _resolve_gemini_model(model_hint: Optional[str], force_refresh: bool = False) -> str:
    global _GEMINI_MODEL_CACHE

    hinted = _normalize_model_name(model_hint)
    if hinted:
        return hinted

    env_model = _normalize_model_name(os.getenv("GEMINI_MODEL"))
    if env_model:
        return env_model

    if _GEMINI_MODEL_CACHE and not force_refresh:
        return _GEMINI_MODEL_CACHE

    async with _GEMINI_MODEL_LOCK:
        if _GEMINI_MODEL_CACHE and not force_refresh:
            return _GEMINI_MODEL_CACHE

        available: List[str] = []
        try:
            registry = await asyncio.to_thread(lambda: list(genai.list_models()))
            available = _model_names_from_registry(registry)
        except Exception as exc:
            logger.warning("Gemini model discovery failed: %s", exc)

        for candidate in _PREFERRED_GEMINI_MODELS:
            if candidate in available:
                _GEMINI_MODEL_CACHE = candidate
                return candidate

        for name in available:
            if "flash" in name.lower():
                _GEMINI_MODEL_CACHE = name
                return name

        if available:
            _GEMINI_MODEL_CACHE = available[0]
        else:
            _GEMINI_MODEL_CACHE = _PREFERRED_GEMINI_MODELS[0]

        return _GEMINI_MODEL_CACHE

def _normalize_ollama_model_name(raw_name: Any) -> Optional[str]:
    if raw_name is None:
        return None
    value = str(raw_name).strip()
    return value or None


def _ollama_api_base() -> str:
    return os.getenv("OLLAMA_API_BASE", "http://127.0.0.1:11434").rstrip("/")


def _ollama_request(method: str, path: str, payload: Optional[dict] = None, timeout: int = 30) -> dict:
    base = _ollama_api_base()
    url = f"{base}{path}"
    body = None
    headers = {"Accept": "application/json"}
    auth_header = os.getenv("OLLAMA_AUTH_HEADER", "").strip()
    api_key = os.getenv("OLLAMA_API_KEY", "").strip()
    if auth_header:
        headers["Authorization"] = auth_header
    elif api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urlrequest.Request(url=url, data=body, headers=headers, method=method)

    try:
        with urlrequest.urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except urlerror.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace").strip()
        if len(detail) > 220:
            detail = detail[:220] + "..."
        raise RuntimeError(f"Ollama HTTP {exc.code} on {path}: {detail}") from exc
    except urlerror.URLError as exc:
        raise RuntimeError(
            f"Ollama is not reachable at {_ollama_api_base()}. Start 'ollama serve'."
        ) from exc

    if not raw.strip():
        return {}

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Ollama returned non-JSON payload from {path}.") from exc

    if isinstance(parsed, dict):
        return parsed
    return {}


def _ollama_list_models() -> List[str]:
    data = _ollama_request("GET", "/api/tags", timeout=12)
    models = data.get("models") if isinstance(data, dict) else None
    if not isinstance(models, list):
        return []

    names: List[str] = []
    for item in models:
        if not isinstance(item, dict):
            continue
        model_name = _normalize_ollama_model_name(item.get("name"))
        if model_name and model_name not in names:
            names.append(model_name)
    return names


async def _resolve_ollama_model(model_hint: Optional[str], force_refresh: bool = False) -> str:
    global _OLLAMA_MODEL_CACHE

    hinted = _normalize_ollama_model_name(model_hint)
    if hinted:
        return hinted

    env_model = _normalize_ollama_model_name(os.getenv("OLLAMA_MODEL"))
    if env_model:
        return env_model

    if _OLLAMA_MODEL_CACHE and not force_refresh:
        return _OLLAMA_MODEL_CACHE

    async with _OLLAMA_MODEL_LOCK:
        if _OLLAMA_MODEL_CACHE and not force_refresh:
            return _OLLAMA_MODEL_CACHE

        available: List[str] = []
        try:
            available = await asyncio.to_thread(_ollama_list_models)
        except Exception as exc:
            logger.warning("Ollama model discovery failed: %s", exc)

        for candidate in _PREFERRED_OLLAMA_MODELS:
            if candidate in available:
                _OLLAMA_MODEL_CACHE = candidate
                return candidate

        if available:
            _OLLAMA_MODEL_CACHE = available[0]
        else:
            _OLLAMA_MODEL_CACHE = "llama3.2:3b"

        return _OLLAMA_MODEL_CACHE

def _is_quota_error(text: str) -> bool:
    lowered = text.lower()
    markers = (
        "quota exceeded",
        "resource_exhausted",
        "rate limit",
        "429",
    )
    return any(marker in lowered for marker in markers)


def _is_hard_quota_lock(text: str) -> bool:
    lowered = text.lower()
    return bool(re.search(r"limit:\s*0\b", lowered))


def _extract_retry_seconds(text: str, default_seconds: int = 60) -> int:
    patterns = (
        r"please retry in\s+([0-9]+(?:\.[0-9]+)?)s",
        r"retry_delay\s*\{\s*seconds:\s*([0-9]+)",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if not match:
            continue
        try:
            return max(1, int(float(match.group(1))))
        except Exception:
            continue
    return default_seconds


def _quota_cooldown_message(
    session: AgentSession, retry_seconds: int, block_reason: str = ""
) -> str:
    if block_reason == "limit_zero":
        return (
            "[SYSTEM QUOTA] Gemini API quota is disabled for this project (limit=0). "
            f"Session moved to WAITING for {retry_seconds}s. "
            "Enable billing/quota in Google AI Studio for this key/project, then retry. "
            f"Use 'Open' to continue externally ({session.provider.upper()})."
        )

    return (
        "[SYSTEM QUOTA] Gemini API quota is exhausted for this project. "
        f"Session moved to WAITING for {retry_seconds}s. "
        f"Use 'Open' to continue externally ({session.provider.upper()}) "
        "or retry after cooldown."
    )



def _session_routing_policy(session: AgentSession) -> dict:
    linked_external = bool(str(session.external_url or "").strip())

    if session.provider == Provider.OLLAMA:
        return {
            "mode": "local_ollama",
            "reason": "provider_ollama",
            "linked_external": linked_external,
            "provider": session.provider,
        }

    if linked_external:
        return {
            "mode": "local_ollama",
            "reason": "external_url_attached",
            "linked_external": True,
            "provider": session.provider,
        }

    if session.provider in (Provider.GPT, Provider.CLAUDE, Provider.COPILOT):
        return {
            "mode": "local_ollama",
            "reason": "browser_provider_bridge",
            "linked_external": False,
            "provider": session.provider,
        }

    return {
        "mode": "gemini_api",
        "reason": "gemini_cloud",
        "linked_external": linked_external,
        "provider": session.provider,
    }


class AgentOrchestrator:
    """
    Handles internal LLM logic for sessions.
    Connects nodes to local/cloud providers (Ollama/Gemini).
    """

    @staticmethod
    def _system_context(session: AgentSession) -> str:
        is_genesis = session.node_id and session.node_id.startswith("gen-")
        if is_genesis:
            return (
                "You are an EvoGenesis Architect Agent. You operate under the GLOBAL NEXUS master-orchestration layer. "
                "Principles: PEAR loop (Perception, Evolution, Action, Reflection). "
                f"Binding: NODE '{session.node_id}' (EvoGenesis Child Pyramid). "
                "Current Goal: Develop a professional architecture for an asynchronous GCP-hosted backend "
                "calling Replicate video functions. Focus on Cloud Tasks, Pub/Sub, and polling/pushing queues. "
                "Provide highly technical, structured advice aligned with evopyramid-ai and Nexus/Bridge architecture."
            )
        return (
            f"You are an EvoPyramid OS Agent. Role: {session.provider.upper()}. "
            f"You are currently bound to NODE: '{session.node_id}' at Z-LEVEL: {session.node_z}. "
            f"Task Context: {session.task_context or 'No specific brief.'}. "
            "Keep responses professional, concise, and focused on system architecture and the specific node duties."
        )

    @staticmethod
    def _history(session: AgentSession) -> List[dict]:
        history: List[dict] = []
        for msg in session.messages[-11:-1]:
            history.append({
                "role": "user" if msg.role == "user" else "model",
                "parts": [msg.content],
            })
        return history

    @staticmethod
    async def _send(model_name: str, system_ctx: str, history: List[dict], user_message: str) -> str:
        model = genai.GenerativeModel(model_name)
        chat = model.start_chat(history=history)
        response = await asyncio.to_thread(chat.send_message, f"{system_ctx}\n\nUSER: {user_message}")
        return response.text

    @staticmethod
    def _build_ollama_messages(session: AgentSession, system_ctx: str) -> List[dict]:
        messages: List[dict] = [{"role": "system", "content": system_ctx}]
        for msg in session.messages[-12:]:
            content = str(msg.content or "").strip()
            if not content:
                continue
            role = "assistant" if msg.role == "assistant" else "user" if msg.role == "user" else "system"
            messages.append({"role": role, "content": content})
        return messages

    @staticmethod
    def _ollama_messages_to_prompt(messages: List[dict]) -> str:
        lines: List[str] = []
        for message in messages:
            role = str(message.get("role", "user")).upper()
            content = str(message.get("content", "")).strip()
            if content:
                lines.append(f"{role}: {content}")
        lines.append("ASSISTANT:")
        return "\n\n".join(lines)

    @staticmethod
    def _send_ollama_sync(model_name: str, messages: List[dict]) -> str:
        payload = {
            "model": model_name,
            "messages": messages,
            "stream": False,
        }

        try:
            chat_data = _ollama_request("POST", "/api/chat", payload=payload, timeout=90)
            message = chat_data.get("message") if isinstance(chat_data, dict) else None
            text = str((message or {}).get("content", "")).strip()
            if text:
                return text
        except RuntimeError as exc:
            text = str(exc)
            if "not reachable" in text.lower():
                raise
            if "HTTP 404" not in text and "HTTP 405" not in text:
                logger.warning("Ollama /api/chat failed, fallback to /api/generate: %s", text)

        prompt = AgentOrchestrator._ollama_messages_to_prompt(messages)
        generate_data = _ollama_request(
            "POST",
            "/api/generate",
            payload={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
            },
            timeout=90,
        )
        generated_text = str(generate_data.get("response", "")).strip()
        if generated_text:
            return generated_text
        raise RuntimeError("Ollama returned an empty response.")

    @staticmethod
    async def _send_ollama(model_name: str, messages: List[dict]) -> str:
        return await asyncio.to_thread(AgentOrchestrator._send_ollama_sync, model_name, messages)

    @staticmethod
    async def get_response(session: AgentSession) -> Optional[str]:
        global _GEMINI_QUOTA_BLOCK_UNTIL, _GEMINI_QUOTA_BLOCK_REASON

        if not session.messages:
            return "[SYSTEM DEBUG] Session has no user message yet."

        system_ctx = AgentOrchestrator._system_context(session)

        policy = _session_routing_policy(session)

        if policy["mode"] == "local_ollama":
            try:
                model_hint = session.model_hint if session.provider == Provider.OLLAMA else None
                model_name = await _resolve_ollama_model(model_hint)
                messages = AgentOrchestrator._build_ollama_messages(session, system_ctx)
                return await AgentOrchestrator._send_ollama(model_name, messages)
            except Exception as exc:
                if policy.get("reason") == "external_url_attached":
                    return (
                        "[SYSTEM LINKED] This session is attached to an external browser chat. "
                        "Use 'Open' to continue directly there. "
                        f"Local bridge unavailable: {exc}"
                    )
                return f"[SYSTEM OLLAMA] {exc}"

        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            return f"[SYSTEM DEBUG] GEMINI_API_KEY not found. Static simulation only node {session.node_id} (Z{session.node_z})."

        now = time.time()
        if _GEMINI_QUOTA_BLOCK_UNTIL > now:
            retry_seconds = max(1, int(_GEMINI_QUOTA_BLOCK_UNTIL - now))
            return _quota_cooldown_message(session, retry_seconds, _GEMINI_QUOTA_BLOCK_REASON)

        genai.configure(api_key=api_key)

        history = AgentOrchestrator._history(session)
        last_msg = session.messages[-1].content

        model_name = "unknown"
        try:
            model_name = await _resolve_gemini_model(session.model_hint)
            text = await AgentOrchestrator._send(model_name, system_ctx, history, last_msg)
            _GEMINI_QUOTA_BLOCK_UNTIL = 0.0
            _GEMINI_QUOTA_BLOCK_REASON = ""
            return text
        except Exception as exc:
            error_text = str(exc)
            lowered = error_text.lower()

            if _is_quota_error(error_text):
                retry_seconds = _extract_retry_seconds(error_text)
                block_reason = "limit_zero" if _is_hard_quota_lock(error_text) else ""
                if block_reason == "limit_zero":
                    retry_seconds = max(retry_seconds, 300)

                _GEMINI_QUOTA_BLOCK_REASON = block_reason
                _GEMINI_QUOTA_BLOCK_UNTIL = max(_GEMINI_QUOTA_BLOCK_UNTIL, now + retry_seconds)
                logger.warning(
                    "Gemini quota exceeded for session %s (node=%s, model=%s). cooldown=%ss reason=%s",
                    session.id,
                    session.node_id,
                    model_name,
                    retry_seconds,
                    _GEMINI_QUOTA_BLOCK_REASON or "temporary",
                )
                return _quota_cooldown_message(session, retry_seconds, _GEMINI_QUOTA_BLOCK_REASON)

            if ("not found" in lowered or "not supported" in lowered) and not session.model_hint:
                try:
                    fallback_model = await _resolve_gemini_model(None, force_refresh=True)
                    if fallback_model != model_name:
                        return await AgentOrchestrator._send(fallback_model, system_ctx, history, last_msg)
                except Exception as retry_exc:
                    return f"⚠ AI Orchestration Error: {retry_exc}"

            return f"⚠ AI Orchestration Error: {error_text}"


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
        "ws_connections": len(manager.active),
    }









