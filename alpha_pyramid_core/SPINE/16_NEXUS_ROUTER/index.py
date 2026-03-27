"""
EvoPyramid Node: GLOBAL NEXUS ROUTER
Z-Level: 16 | Sector: SPINE

Acts as the central router for the Hybrid System.
Routes tasks into the Z-Bus and manages synchronous API responses 
via futures for asynchronous execution.
"""
import logging
import asyncio
import sys
from pathlib import Path

# Resolve paths
THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger(__name__)

class NexusRouter:
    """
    Routes commands from the Global Control Plane into the Policy Bus (Z-Bus),
    allowing for asynchronous execution while bridging synchronous HTTP boundaries.
    """
    def __init__(self, zbus_instance):
        self.zbus = zbus_instance
        self.pending_tasks = {}
        
        # Subscribe to execution results to resolve HTTP wait futures
        self.zbus.subscribe("TASK_RESULT", self._on_task_result)

    async def _on_task_result(self, event_dict):
        payload = event_dict.get("payload", {})
        task_id = payload.get("task_id")
        if task_id in self.pending_tasks:
            future = self.pending_tasks[task_id]
            if not future.done():
                future.set_result(payload)

    async def dispatch_sync(self, envelope) -> dict:
        """
        Dispatches a task to the Z-Bus and awaits its result.
        This provides the synchronous illusion needed by REST APIs.
        """
        task_id = envelope.task_id
        future = asyncio.Future()
        self.pending_tasks[task_id] = future
        
        # Publish to the Z-Bus for the Kernel (or any worker) to process
        await self.zbus.publish({
            "topic": "EXECUTE_TASK",
            "payload": {
                "task_id": task_id,
                "envelope": envelope.model_dump()
            }
        })
        
        try:
            # Wait for execution with a 30 second timeout
            result_payload = await asyncio.wait_for(future, timeout=30.0)
            return result_payload
        except asyncio.TimeoutError:
            return {
                "status": "ERROR",
                "task_id": task_id,
                "reason": "Z-Bus Execution Timeout"
            }
        finally:
            self.pending_tasks.pop(task_id, None)

    async def dispatch_async(self, envelope) -> dict:
        """
        Dispatches a task asynchronously and returns immediately.
        The UI will receive the result via WebSocket.
        """
        await self.zbus.publish({
            "topic": "EXECUTE_TASK",
            "payload": {
                "task_id": envelope.task_id,
                "envelope": envelope.model_dump()
            }
        })
        return {
            "status": "ACCEPTED_ASYNC",
            "task_id": envelope.task_id,
            "message": "Dispatched to Z-Bus"
        }

# Global singleton will be initialized when needed by the API
nexus_router_instance = None

def get_router(zbus_instance):
    global nexus_router_instance
    if nexus_router_instance is None:
        nexus_router_instance = NexusRouter(zbus_instance)
    return nexus_router_instance
