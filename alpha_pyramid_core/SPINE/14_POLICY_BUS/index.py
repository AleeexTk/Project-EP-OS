"""
EvoPyramid Node: POLICY BUS (Z-Bus)
Z-Level: 14 | Sector: SPINE

The Event-Bus Broker for routing multi-provider execution, 
streaming events to/from extensions, and synchronizing state across the Hybrid Model.
"""
import asyncio
import logging
from typing import Dict, Any, Callable, List
import sys
from pathlib import Path

# Resolve paths
THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
REG_DIR = PROJECT_ROOT / "beta_pyramid_functional" / "B3_SessionRegistry"
if str(REG_DIR) not in sys.path:
    sys.path.insert(0, str(REG_DIR))

class ZBus:
    """
    Asynchronous Pub/Sub Event Bus enforcing the Hybrid Truth layer.
    """
    def __init__(self):
        self.queue = asyncio.Queue()
        self.running = False
        self.subscribers: Dict[str, List[Callable]] = {}
        self.manager = None

    def subscribe(self, topic: str, callback: Callable):
        """Subscribe a local processor to a specific topic."""
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)

    async def publish(self, event: Any):
        """Publish a ZBusEvent (or dict) to the queue."""
        await self.queue.put(event)

    async def dispatch_llm_task(self, task_id: str, session_id: str, provider: str, prompt: str, target_url: str = "", routing: str = "single"):
        try:
            from session_models import ZBusEvent, ZBusTopic
            from datetime import datetime, timezone
            
            event = ZBusEvent(
                topic=ZBusTopic.PROMPT_DISPATCH.value,
                session_id=session_id,
                task_id=task_id,
                payload={
                    "provider": provider,
                    "prompt": prompt,
                    "url": target_url,
                    "routing": routing
                },
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            await self.publish(event)
        except ImportError as e:
            logging.error(f"[Z14 Policy Bus] Failed to import ZBusEvent: {e}")
            await self.publish({
                "topic": "prompt.dispatch",
                "session_id": session_id,
                "task_id": task_id,
                "payload": {"provider": provider, "prompt": prompt, "url": target_url, "routing": routing}
            })
            
    async def run_worker(self, websocket_manager, current_state=None):
        """Background worker that routes events to subscribers and broadcasts them."""
        self.running = True
        self.manager = websocket_manager
        logging.info("[Z14 Policy Bus] Enhanced Event-Bus worker initialized.")
        while self.running:
            try:
                event = await self.queue.get()
                
                # Normalize event to dict for routing and broadcast
                if hasattr(event, "model_dump"):
                    event_dict = event.model_dump()
                else:
                    event_dict = event if isinstance(event, dict) else dict(event)
                
                topic = event_dict.get("topic")
                logging.info(f"[Z14 Policy Bus] Routing Event: {topic} (Payload keys: {list(event_dict.get('payload', {}).keys())})")
                
                # 1. Trigger local subscribers if any
                if topic in self.subscribers:
                    for callback in self.subscribers[topic]:
                        try:
                            if asyncio.iscoroutinefunction(callback):
                                await callback(event_dict)
                            else:
                                callback(event_dict)
                        except Exception as cb_e:
                            logging.error(f"[Z14 Policy Bus] Subscriber error on {topic}: {cb_e}")
                
                # 2. Transmit to external clients (Extension, UI) via WS manager
                if self.manager:
                    await self.manager.broadcast({
                        "type": "zbus_event",
                        "data": event_dict
                    })
                
                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"[Z14 Policy Bus] Worker error: {e}")

    async def broadcast_event(self, event_data: Dict[str, Any]):
        """Direct broadcast bypassing the queue, typically used for immediate node state changes."""
        if hasattr(self, 'manager') and self.manager:
            await self.manager.broadcast({
                "type": "zbus_event",
                "data": event_data
            })
        else:
            logging.warning("[Z14 Policy Bus] Manager not initialized. Dropping event.")

zbus_instance = ZBus()
