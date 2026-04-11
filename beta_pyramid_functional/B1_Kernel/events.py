from enum import Enum
from typing import Any, Dict, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

class EventSeverity(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class EventType(str, Enum):
    # --- Lifecycle ---
    NODE_START = "node_start"
    NODE_PROGRESS = "node_progress"
    NODE_COMPLETE = "node_complete"
    NODE_FAILURE = "node_failure"
    
    # --- Provider / Logic ---
    PROVIDER_SELECTED = "provider_selected"
    PROVIDER_TIMEOUT = "provider_timeout"
    PROVIDER_UNAVAILABLE = "provider_unavailable"
    
    # --- Fallback / Recovery ---
    NODE_FALLBACK_INIT = "node_fallback_init"
    NODE_RECOVERY_SUCCESS = "node_recovery_success"
    NODE_RECOVERY_FAILED = "node_recovery_failed"
    
    # --- System / Chaos ---
    SYSTEM_ANOMALY = "system_anomaly"
    CHAOS_IMPULSE = "chaos_impulse"

    # --- Z-SPINE Observability (Z6 → Z2 → Z10) ---
    AUDIT_STREAM = "AUDIT_STREAM"            # Z6 → Z2: telemetry packets
    AUDIT_VIOLATION = "AUDIT_VIOLATION"      # Z2 → broadcast: policy breach detected
    CANON_GATE_REQUEST = "CANON_GATE_REQUEST"   # Alpha → Z10: formal cross-layer intent
    CANON_GATE_APPROVED = "CANON_GATE_APPROVED" # Z10 → Beta: approved for execution
    CANON_GATE_REJECTED = "CANON_GATE_REJECTED" # Z10 → Alpha: rejected at boundary

class BaseEvoEvent(BaseModel):
    """Канонический контракт события EvoPyramid OS."""
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Контекстные идентификаторы
    trace_id: str  # Сквозной ID операции (от Z17 до исполнения)
    node_id: str   # Узел-источник
    task_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Состояние
    severity: EventSeverity = EventSeverity.INFO
    simulation: bool = False  # Работает ли узел в режиме симуляции/chaos
    
    # Полезная нагрузка
    payload: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = {"use_enum_values": True}

# --- Специализированные схемы полезной нагрузки (Payloads) ---

class ProviderPayload(BaseModel):
    provider_name: str
    model: str
    latency_ms: Optional[float] = None
    error_message: Optional[str] = None

class FailurePayload(BaseModel):
    error_code: str
    message: str
    stack_trace: Optional[str] = None
    retry_count: int = 0

class FallbackPayload(BaseModel):
    from_provider: str
    to_provider: str
    reason: str
    trigger_node: str

def create_event(
    event_type: EventType,
    trace_id: str,
    node_id: str,
    severity: EventSeverity = EventSeverity.INFO,
    payload: Dict[str, Any] = None,
    **kwargs
) -> BaseEvoEvent:
    """Helper для быстрого создания типизированных событий."""
    return BaseEvoEvent(
        event_type=event_type,
        trace_id=trace_id,
        node_id=node_id,
        severity=severity,
        payload=payload or {},
        **kwargs
    )
