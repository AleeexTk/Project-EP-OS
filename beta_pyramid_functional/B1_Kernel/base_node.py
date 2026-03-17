import asyncio
import logging
import sys
import uuid
import time
from pathlib import Path
from typing import Optional, Dict, Any

# --- Kernel Path Initialization ---
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR / "beta_pyramid_functional" / "B1_Kernel") not in sys.path:
    sys.path.append(str(ROOT_DIR / "beta_pyramid_functional" / "B1_Kernel"))

from events import (
    EventType, EventSeverity, BaseEvoEvent, create_event
)

try:
    from zbus import zbus
except ImportError:
    zbus = None

class BaseServiceNode:
    """
    Канонический базовый класс для всех автономных узлов EvoPyramid OS.
    Обеспечивает автоматическую работу с путями, коммуникацию через ZBus
    и жизненный цикл событий.
    """
    
    def __init__(self, node_id: str, trace_id: Optional[str] = None, simulation: bool = False):
        self.node_id = node_id
        self.trace_id = trace_id or f"trace-{uuid.uuid4().hex[:8]}"
        self.simulation = simulation
        self.logger = logging.getLogger(self.node_id)
        
    async def publish(self, event_type: EventType, severity: EventSeverity = EventSeverity.INFO, 
                      task_id: Optional[str] = None, session_id: Optional[str] = None, 
                      payload: Optional[Dict[str, Any]] = None):
        """Создает и публикует каноническое событие."""
        event = create_event(
            event_type=event_type,
            trace_id=self.trace_id,
            node_id=self.node_id,
            severity=severity,
            task_id=task_id,
            session_id=session_id,
            simulation=self.simulation,
            payload=payload or {}
        )
        
        event_dict = event.model_dump()
        self.logger.info(f"==> [ZBUS] {event.event_type} | {event.severity}")

        # 1. Memory Broadcast
        try:
            if zbus and hasattr(zbus, 'manager') and zbus.manager:
                await zbus.broadcast_event(event_dict)
                return
        except Exception:
            pass

        # 2. HTTP Gateway
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                await client.post("http://127.0.0.1:8000/zbus/publish", json=event_dict, timeout=1.0)
        except Exception as e:
            self.logger.debug(f"ZBus Gateway offline: {e}")

    async def run(self, *args, **kwargs):
        """Основной метод выполнения, должен быть переопределен в подклассах."""
        raise NotImplementedError("Service node must implement run() method.")

def node_entry(cls):
    """Декоратор для автоматической инициализации окружения узла."""
    # Резерв для будущих автоматических регистраций и инжекций зависимостей
    return cls
