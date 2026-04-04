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
from datetime import datetime, timezone

# Canonical path resolution
THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parents[3]  # alpha_pyramid_core/SPINE/_16_NEXUS_ROUTER -> project root
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from beta_pyramid_functional.B1_Kernel.timeline import TimelineManager  # noqa: E402

logger = logging.getLogger(__name__)

class NexusRouter:
    """
    Routes commands from the Global Control Plane into the Policy Bus (Z-Bus),
    allowing for asynchronous execution while bridging synchronous HTTP boundaries.
    """
    BLACKLIST = {} # node_id -> cooldown_until (timestamp)
    MISBEHAVIOR_SCORES = {} # node_id -> count
    
    EVOLUTION_JOURNAL_PATH = PROJECT_ROOT / "gamma_pyramid_reflective" / "B_Evo_Log" / "evolution_journal.md"

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

    def _check_blacklist(self, node_id: str) -> tuple[bool, str]:
        """Checks if a node is currently blacklisted."""
        if node_id in self.BLACKLIST:
            cooldown = self.BLACKLIST[node_id]
            if datetime.now().timestamp() < cooldown:
                remaining = int(cooldown - datetime.now().timestamp())
                return True, f"Node {node_id} is blacklisted for {remaining}s due to repeated TRP violations."
            else:
                del self.BLACKLIST[node_id]
                self.MISBEHAVIOR_SCORES[node_id] = 0
        return False, ""

    def _handle_misbehavior(self, node_id: str, reason: str):
        """Increments misbehavior score and blacklists if threshold reached."""
        self.MISBEHAVIOR_SCORES[node_id] = self.MISBEHAVIOR_SCORES.get(node_id, 0) + 1
        if self.MISBEHAVIOR_SCORES[node_id] >= 3:
            cooldown = datetime.now().timestamp() + 60 # 1 minute ban
            self.BLACKLIST[node_id] = cooldown
            self._log_to_evolution_journal(node_id, reason)

    def _log_to_evolution_journal(self, node_id: str, reason: str):
        """Records the blacklisting event in the Evolution Journal."""
        if not self.EVOLUTION_JOURNAL_PATH.exists():
            return
        
        entry = (
            f"\n### [EVENT] Temporal Blacklist Active\n"
            f"- **Node**: `{node_id}`\n"
            f"- **Action**: 60s Execution Ban\n"
            f"- **Reason**: {reason}\n"
            f"- **Timestamp**: `{datetime.now(timezone.utc).isoformat()}`\n"
        )
        with open(self.EVOLUTION_JOURNAL_PATH, "a", encoding="utf-8") as f:
            f.write(entry)

    async def dispatch_sync(self, envelope) -> dict:
        """
        Dispatches a task with Early TRP and Blacklist Enforcement.
        """
        node_id = envelope.source_node
        
        # 1. Blacklist Check
        is_blocked, msg = self._check_blacklist(node_id)
        if is_blocked:
            return {"status": "BLACKLISTED", "task_id": envelope.task_id, "reason": msg}

        # 2. TRP: Early Gatekeeper Check
        bridge_id = envelope.metadata.get("via", "ZBUS_BRIDGE")
        success, slot_id, msg = TimelineManager.request_slot(envelope.model_dump(), via=bridge_id)
        
        if not success:
            self._handle_misbehavior(node_id, msg)
            return {
                "status": "DENIED_BY_ATC",
                "task_id": envelope.task_id,
                "reason": f"Temporal Routing Denied: {msg}"
            }
        
        # Reset score on success
        self.MISBEHAVIOR_SCORES[node_id] = 0
        
        envelope.slot_id = slot_id
        task_id = envelope.task_id
        future = asyncio.Future()
        self.pending_tasks[task_id] = future
        
        # Publish to the Z-Bus
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
                "reason": "Z-Bus Execution Timeout (ATC Slot was active)"
            }
        finally:
            self.pending_tasks.pop(task_id, None)

    async def dispatch_async(self, envelope) -> dict:
        """
        Dispatches a task asynchronously with Early TRP and Blacklist Enforcement.
        """
        node_id = envelope.source_node
        
        # 1. Blacklist Check
        is_blocked, msg = self._check_blacklist(node_id)
        if is_blocked:
            return {"status": "BLACKLISTED", "task_id": envelope.task_id, "reason": msg}

        # 2. TRP: Early Gatekeeper Check
        bridge_id = envelope.metadata.get("via", "ZBUS_BRIDGE")
        success, slot_id, msg = TimelineManager.request_slot(envelope.model_dump(), via=bridge_id)
        
        if not success:
            self._handle_misbehavior(node_id, msg)
            return {
                "status": "DENIED_BY_ATC",
                "task_id": envelope.task_id,
                "reason": f"Temporal Routing Denied: {msg}"
            }
            
        self.MISBEHAVIOR_SCORES[node_id] = 0
        envelope.slot_id = slot_id
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
            "slot_id": slot_id,
            "message": f"Dispatched via ATC Slot {slot_id}"
        }

# Global singleton will be initialized when needed by the API
nexus_router_instance = None

def get_router(zbus_instance):
    global nexus_router_instance
    if nexus_router_instance is None:
        nexus_router_instance = NexusRouter(zbus_instance)
    return nexus_router_instance
