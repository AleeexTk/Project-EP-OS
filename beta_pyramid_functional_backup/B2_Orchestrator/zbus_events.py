"""
Z-Bus Event Contract (Vertical Slice)
Defines the rigid schema for all events flowing between EvoPyramid OS and the Browser Bridge.
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone
import uuid

# ─────────────────────────────────────────
# Inbound Topics (Evo OS -> Extension)
# ─────────────────────────────────────────
class InboundTopic:
    PROMPT_DISPATCH = "PROMPT_DISPATCH"
    ATTACH_SESSION = "ATTACH_SESSION"
    DETACH_SESSION = "DETACH_SESSION"
    PING = "PING"

# ─────────────────────────────────────────
# Outbound Topics (Extension -> Evo OS)
# ─────────────────────────────────────────
class OutboundTopic:
    BRIDGE_HEARTBEAT = "BRIDGE_HEARTBEAT"
    TAB_DISCOVERED = "TAB_DISCOVERED"
    SESSION_ATTACHED = "SESSION_ATTACHED"
    PROMPT_ACCEPTED = "PROMPT_ACCEPTED"
    TOKEN_STREAM = "TOKEN_STREAM"
    RESPONSE_COMPLETE = "RESPONSE_COMPLETE"
    
    # Error states (Crucial for Truth Layer)
    BRIDGE_ERROR = "BRIDGE_ERROR"
    DOM_ERROR = "DOM_ERROR"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    CAPTCHA_REQUIRED = "CAPTCHA_REQUIRED"

# ─────────────────────────────────────────
# Canonical Event Schema
# ─────────────────────────────────────────
class ZBusMessage(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    topic: str
    
    # Correlation Identifiers
    session_id: Optional[str] = None
    provider_id: Optional[str] = None
    tab_id: Optional[int] = None
    task_id: Optional[str] = None  # Crucial for prompt flow
    
    # Diagnostics
    severity: str = "info" # info | warning | error | critical
    
    # Data Payload
    payload: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        extra = "allow"
