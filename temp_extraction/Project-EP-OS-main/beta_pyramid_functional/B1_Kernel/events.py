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
    
    class Config:
        use_enum_values = True

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
