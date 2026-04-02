import sys
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any

logger = logging.getLogger("TemporalDispatcher")

class TemporalDispatcher:
    """
    ATC (Air Traffic Control) for EvoPyramid OS.
    Enforces the Temporal Route API to prevent module collisions.
    """
    def __init__(self):
        self.active_slots: Dict[str, Dict[str, Any]] = {}
        self.lock = asyncio.Lock()

    async def validate_or_block(self, event_dict: Dict[str, Any]) -> bool:
        """
        Validates event transit through the ATC.
        Checks if the event can safely secure an architectural time slot.
        """
        topic = event_dict.get("topic", "")
        # Only critically monitor EXECUTE_TASK and PROMPT_DISPATCH
        if topic not in ["EXECUTE_TASK", "PROMPT_DISPATCH", "prompt.dispatch"]:
            return True 
            
        payload = event_dict.get("payload", {})
        
        # Deduce identifiers
        module_id = event_dict.get("node_id") or event_dict.get("session_id") or "external_agent"
        route = payload.get("route_request", {})
        location = route.get("location") or "global_bus"
        action = route.get("action") or topic
        
        async with self.lock:
            # Check for collision
            if location in self.active_slots:
                current_owner = self.active_slots[location]
                if current_owner["module_id"] != module_id:
                    logger.critical(f"[ATC] ROUTE DENIED! '{module_id}' attempted to hijack '{location}' from '{current_owner['module_id']}'.")
                    return False
            
            # Secure Slot
            self.active_slots[location] = {
                "module_id": module_id,
                "action": action,
                "time": datetime.now(timezone.utc).isoformat()
            }
            logger.info(f"[ATC] Route Approved: {module_id} -> {location} [{action}]")
            
            try:
                from beta_pyramid_functional.B1_Kernel.ws_manager import manager
                asyncio.create_task(manager.broadcast({
                    "type": "atc_route_locked",
                    "location": location,
                    "payload": self.active_slots[location]
                }))
            except Exception as e:
                logger.warning(f"[ATC] Failed to emit socket event: {e}")
            
            # Auto-release after a grace period to prevent deadlocks
            asyncio.create_task(self._auto_release_slot(location, module_id))
            return True
            
    async def _auto_release_slot(self, location: str, module_id: str):
        await asyncio.sleep(8)
        async with self.lock:
            if location in self.active_slots and self.active_slots[location]["module_id"] == module_id:
                del self.active_slots[location]
                logger.info(f"[ATC] Slot Released automatically: {location}")
                
                try:
                    from beta_pyramid_functional.B1_Kernel.ws_manager import manager
                    asyncio.create_task(manager.broadcast({
                        "type": "atc_route_released",
                        "location": location
                    }))
                except Exception:
                    pass

temporal_dispatcher = TemporalDispatcher()
