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

class CascadeStatus(str, Enum):
    """Status of the Inter-level Z-Pair Cascading Validation."""
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    PASSED = "PASSED"
    BLOCKED = "BLOCKED"
    DEGRADED = "DEGRADED"
    CRYSTALLIZED = "CRYSTALLIZED"

class TaskEnvelope(BaseModel):
    """The formal spine-kernel message contract for EvoPyramid OS."""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_node: str
    target_node: str
    action: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    status: TaskStatus = TaskStatus.PENDING
    cascade_status: Optional[CascadeStatus] = None
    origin_z: int = 1   # Z-level of the source node
    location_sector: str = "GENERIC"  # Sector/Zone within the Pyramid (e.g., CORE, SPINE, REFLECTIVE)
    intent: Optional[str] = None  # Original Architect's intent (canonical goal)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    signature: Optional[str] = None  # Zero-Trust Cryptographic Signature
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    slot_id: Optional[str] = None  # Temporal Slot ID for ATC coordination
    next_action_slot: Optional[str] = None # Pointer to the next intended step in the flight plan
    temporal_trace: List[Dict[str, Any]] = Field(default_factory=list) # 4D history trace
    coherence_score: float = 1.0  # TRINITY RESONANCE v3.0 logic
    trinity_state: str = "DORMANT"  # FSM State (LISTENING, PARSING, etc.)

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
