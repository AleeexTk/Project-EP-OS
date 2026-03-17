from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class LayerType(str, Enum):
    ALPHA = "alpha"
    BETA = "beta"
    GAMMA = "gamma"

class NodeKind(str, Enum):
    MODULE = "module"
    SERVICE = "service"
    MEMORY = "memory"
    PROTOCOL = "protocol"
    AGENT = "agent"
    SUMMARY = "summary"
    CANON = "canon"
    RUNTIME = "runtime"
    ROUTER = "router"
    BUS = "bus"

class NodeState(str, Enum):
    ACTIVE = "active"
    IDLE = "idle"
    DEGRADED = "degraded"
    FAILED = "failed"
    QUARANTINED = "quarantined"
    ERROR = "error"

class CanonStatus(str, Enum):
    CANON = "canon"
    CANDIDATE = "candidate"
    RUNTIME = "runtime"

class LinkType(str, Enum):
    DEPENDS_ON = "depends_on"
    ORCHESTRATES = "orchestrates"
    FEEDS_INTO = "feeds_into"
    PART_OF = "part_of"
    CONTRADICTS = "contradicts"

class OrchestratorState(str, Enum):
    UNLINKED = "unlinked"
    READY = "ready"
    WAITING_FOR_LLM = "waiting_for_llm"
    ERROR_CAPTCHA = "error_captcha"
    RATE_LIMITED = "rate_limited"
    UI_BROKEN = "ui_broken"

class NodeCoords(BaseModel):
    x: int
    y: int
    z: int

class Node(BaseModel):
    id: str
    title: str
    z_level: int
    sector: str
    coords: NodeCoords
    layer_type: LayerType
    kind: NodeKind
    summary: str
    state: NodeState = NodeState.IDLE
    canon_status: CanonStatus = CanonStatus.RUNTIME
    artifacts: List[str] = []
    links: List[str] = [] # IDs of targets
    children: List[str] = []
    source_refs: List[str] = []
    metadata: Dict[str, Any] = {}
    
    # Canon / Runtime distinction (used by UI badge and PATCH /nodes/{id}/status)
    # "canon" = Architect-managed, immutable at runtime
    # "runtime" = live, mutable via PATCH
    runtime_canon_flag: str = "runtime"

    # Browser Orchestrator Support
    session_url: Optional[str] = None
    browser_profile_dir: Optional[str] = None
    orchestrator_state: OrchestratorState = OrchestratorState.UNLINKED

    # Cognitive / SK Engine metrics
    memory_color: str = "white"
    gravity: float = 1.0

class Link(BaseModel):
    source_id: str
    target_id: str
    link_type: LinkType
    metadata: Dict[str, Any] = {}

class PyramidState(BaseModel):
    nodes: Dict[str, Node] = {}
    links: List[Link] = []
