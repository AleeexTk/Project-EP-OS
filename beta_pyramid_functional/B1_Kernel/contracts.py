from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from enum import Enum
from datetime import datetime, timezone
import uuid

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskEnvelope(BaseModel):
    """The formal spine-kernel message contract for EvoPyramid OS."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_node: str
    target_node: str
    action: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    origin_z: int = 1   # Z-level of the source node
    metadata: Dict[str, Any] = Field(default_factory=dict)
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class SystemPolicy(BaseModel):
    """Permissions and policy layer for autonomous execution nodes."""
    allow_filesystem_write: bool = False
    allow_network_access: bool = False
    max_memory_mb: int = 512
    timeout_seconds: int = 60

class AgentSessionContract(BaseModel):
    """Formal contract for an agent session lifecycle."""
    session_id: str
    owner_id: str
    agent_type: str = "generic"
    active_policy: SystemPolicy = Field(default_factory=SystemPolicy)
    history: List[TaskEnvelope] = Field(default_factory=list)
    state: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
