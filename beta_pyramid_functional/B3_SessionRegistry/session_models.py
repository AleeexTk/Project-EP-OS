"""
Session Registry вЂ” Z9 В· ОІ_Pyramid_Functional В· GREEN sector
Core service for managing agent session lifecycle.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel, Field


# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
#  Domain Enums
# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

class Provider(str, Enum):
    GPT       = "gpt"
    GEMINI    = "gemini"
    CLAUDE    = "claude"
    COPILOT   = "copilot"
    OLLAMA    = "ollama"


class SessionStatus(str, Enum):
    PENDING  = "pending"
    ACTIVE   = "active"
    WAITING  = "waiting"
    REVIEW   = "review"
    DONE     = "done"
    PAUSED   = "paused"
    CONFLICT = "conflict"


class MessageRole(str, Enum):
    USER      = "user"
    ASSISTANT = "assistant"
    SYSTEM    = "system"


# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
#  Data Models
# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

class Message(BaseModel):
    id:        str           = Field(default_factory=lambda: str(uuid.uuid4()))
    role:      MessageRole
    content:   str
    ts:        str           = Field(default_factory=lambda: _now())
    agent_ref: Optional[str] = None  # agent model label, e.g. "gemini-1.5-pro"


class AgentSession(BaseModel):
    # Identity
    id:            str           = Field(default_factory=lambda: f"sess_{str(uuid.uuid4().hex)[0:8]}")
    # Pyramid binding
    node_id:       str
    node_z:        int
    node_sector:   str           = "GREEN"
    # Agent config
    provider:      Provider
    account_hint:  Optional[str] = None   # e.g. "work@gmail.com"
    model_hint:    Optional[str] = None   # e.g. "gemini-1.5-pro"
    # Task context
    task_title:    str
    task_context:  Optional[str] = None   # full prompt / brief for the session
    # Lifecycle
    status:        SessionStatus = SessionStatus.PENDING
    created_at:    str           = Field(default_factory=lambda: _now())
    updated_at:    str           = Field(default_factory=lambda: _now())
    # Communication
    messages:      List[Message] = Field(default_factory=list)
    
    # --- [v1.1] Attached Workspace Tab Metadata ---
    external_url:         Optional[str] = None
    external_origin:      Optional[str] = None   # e.g. "gemini.google.com"
    external_title:       Optional[str] = None   # e.g. "Gemini - Z13 Status"
    bridge_mode:          str           = "hybrid" # linked_tab | hybrid | managed
    bridge_status:        str           = "connected" # connected | lost | reattach | detached
    supervisor_enabled:   bool          = True
    focusable:            bool          = True


class SessionCreateRequest(BaseModel):
    node_id:      str
    node_z:       int
    node_sector:  str           = "GREEN"
    provider:     Provider
    account_hint: Optional[str] = None
    model_hint:   Optional[str] = None
    task_title:   str
    task_context: Optional[str] = None
    external_url: Optional[str] = None
    bridge_mode:  Optional[str] = "hybrid"


class MessageCreateRequest(BaseModel):
    role:      MessageRole = MessageRole.USER
    content:   str
    agent_ref: Optional[str] = None


class StatusUpdateRequest(BaseModel):
    status: SessionStatus


# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
#  Helpers
# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
#  Storage (JSON file вЂ” no DB dependency)
# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

STORE_PATH = Path(__file__).parent / "sessions_store.json"


def _load_store() -> dict:
    if not STORE_PATH.exists():
        return {"sessions": {}}
    return json.loads(STORE_PATH.read_text(encoding="utf-8"))


def _save_store(store: dict) -> None:
    STORE_PATH.write_text(
        json.dumps(store, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ
#  Service Layer
# в”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђв”Ђ

class SessionRegistry:
    """Pure service вЂ” no FastAPI dependency here."""

    @staticmethod
    def create(req: SessionCreateRequest) -> AgentSession:
        session = AgentSession(
            node_id=req.node_id,
            node_z=req.node_z,
            node_sector=req.node_sector,
            provider=req.provider,
            account_hint=req.account_hint,
            model_hint=req.model_hint,
            task_title=req.task_title,
            task_context=req.task_context,
            external_url=req.external_url,
            bridge_mode=req.bridge_mode or "hybrid",
            external_origin=SessionRegistry._extract_origin(req.external_url),
            status=SessionStatus.ACTIVE,
        )
        store = _load_store()
        store["sessions"][session.id] = session.model_dump()
        _save_store(store)
        return session

    @staticmethod
    def _extract_origin(url: Optional[str]) -> Optional[str]:
        if not url: return None
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return None

    @staticmethod
    def get(session_id: str) -> Optional[AgentSession]:
        store = _load_store()
        data = store["sessions"].get(session_id)
        if not data:
            return None
        return AgentSession(**data)

    @staticmethod
    def list_all() -> List[AgentSession]:
        store = _load_store()
        return [AgentSession(**v) for v in store["sessions"].values()]

    @staticmethod
    def list_by_node(node_id: str) -> List[AgentSession]:
        return [s for s in SessionRegistry.list_all() if s.node_id == node_id]

    @staticmethod
    def add_message(session_id: str, req: MessageCreateRequest) -> Optional[AgentSession]:
        store = _load_store()
        data = store["sessions"].get(session_id)
        if not data:
            return None
        session = AgentSession(**data)
        msg = Message(role=req.role, content=req.content, agent_ref=req.agent_ref)
        session.messages.append(msg)
        session.updated_at = _now()
        store["sessions"][session_id] = session.model_dump()
        _save_store(store)
        return session

    @staticmethod
    def update_status(session_id: str, req: StatusUpdateRequest) -> Optional[AgentSession]:
        store = _load_store()
        data = store["sessions"].get(session_id)
        if not data:
            return None
        session = AgentSession(**data)
        session.status = req.status
        session.updated_at = _now()
        store["sessions"][session_id] = session.model_dump()
        _save_store(store)
        return session

    @staticmethod
    def delete(session_id: str) -> bool:
        store = _load_store()
        if session_id not in store["sessions"]:
            return False
        del store["sessions"][session_id]
        _save_store(store)
        return True



