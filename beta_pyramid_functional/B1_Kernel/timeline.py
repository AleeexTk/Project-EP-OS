import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, List
import uuid

# Canonical paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
GLOBAL_TIMELINE_PATH = PROJECT_ROOT / "timeline" / "project_timeline.ndjson"
BRIDGE_LOCKS_PATH = PROJECT_ROOT / "state" / "bridge_locks.ndjson"

# Node to path mapping for local timelines
NODE_MAP = {
    "Z17_GLOBAL_NEXUS": "alpha_pyramid_core/SPINE/17_GLOBAL_NEXUS",
    "gen-nexus": "alpha_pyramid_core/SPINE/17_GLOBAL_NEXUS",
    "Z16_NEXUS_ROUTER": "alpha_pyramid_core/SPINE/16_NEXUS_ROUTER",
    "Z14_POLICY_BUS": "alpha_pyramid_core/SPINE/14_POLICY_BUS",
    "Z13_AUTO_CORRECTOR": "alpha_pyramid_core/SPINE/13_AUTO_CORRECTOR",
    "B1_PROJECT_CORTEX": "beta_pyramid_functional/B1_Kernel",
    "B2_SYNTHESIS_AGENT": "beta_pyramid_functional/B2_Orchestrator",
    "B2_LLM_ORCHESTRATOR": "beta_pyramid_functional/B2_Orchestrator",
    "B4_COGNITIVE_BRIDGE": "beta_pyramid_functional/B4_Cognitive",
    "D_INTERFACE_API": "beta_pyramid_functional/D_Interface",
}

class TimelineManager:
    """
    Manages the 4th dimension (Time) of the EvoPyramid OS.
    Implements NDJSON logging and hardened Temporal Routing Protocol (TRP).
    """

    @staticmethod
    def log_event(envelope_data: Dict[str, Any], action: str, status: str, summary: Optional[str] = None, next_intent: str = "WAIT"):
        """
        Logs a structured event to both global and local timelines.
        Format: UNIFIED 6-FIELD PROTOCOL (time, id, location, action, status, next)
        """
        # Ensure global directory exists
        GLOBAL_TIMELINE_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Unified 6-field event structure
        event = {
            "time": datetime.now(timezone.utc).isoformat(),
            "id": envelope_data.get("source_node", "UNKNOWN"),
            "location": envelope_data.get("metadata", {}).get("pair_id", envelope_data.get("origin_z", "STAY")),
            "action": action,
            "status": status,
            "next": next_intent,
            # Extended traceability
            "task_id": envelope_data.get("task_id"),
            "slot_id": envelope_data.get("slot_id"),
            "summary": summary or envelope_data.get("intent", "")
        }

        # Write to Global Timeline
        with open(GLOBAL_TIMELINE_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

        # Write to Local Timeline
        TimelineManager._log_to_local(event["id"], event)

    @staticmethod
    def _log_to_local(node_id: str, event: Dict[str, Any]):
        """Writes the event to the node-specific local timeline.ndjson."""
        rel_path = NODE_MAP.get(node_id)
        if not rel_path:
            return

        local_path = PROJECT_ROOT / rel_path / "timeline.ndjson"
        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            with open(local_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        except Exception:
            # Silent fail for local logging to avoid blocking core execution
            pass

    _ACTIVE_SLOTS = {} # bridge_id -> slot_data

    @staticmethod
    def _sync_from_disk():
        """Syncs the RAM cache from the bridge_locks.ndjson persistent store."""
        if not BRIDGE_LOCKS_PATH.exists():
            return
        try:
            with open(BRIDGE_LOCKS_PATH, "r", encoding="utf-8") as f:
                lines = f.readlines()
                # We only care about the latest state of each bridge
                temp_status = {}
                for line in lines:
                    if not line.strip(): continue
                    lock = json.loads(line)
                    temp_status[lock["bridge_id"]] = lock
                
                # Filter only active locks
                TimelineManager._ACTIVE_SLOTS = {
                    b_id: data for b_id, data in temp_status.items() 
                    if data["status"] == "active"
                }
        except Exception:
            pass

    @staticmethod
    def request_slot(envelope_data: Dict[str, Any], via: Optional[str] = None) -> Tuple[bool, str, str]:
        """
        Requests a temporal slot for a cross-layer or cross-module movement.
        Phase 3: Uses RAM-based ACTIVE_SLOTS for sub-millisecond verification.
        """
        via = via or envelope_data.get("metadata", {}).get("via", "GENERAL_ROUTE")
        
        # Cold start sync if RAM is empty but disk has data
        if not TimelineManager._ACTIVE_SLOTS and BRIDGE_LOCKS_PATH.exists():
            TimelineManager._sync_from_disk()

        # Check RAM bridge availability
        if via in TimelineManager._ACTIVE_SLOTS:
            msg = f"Bridge {via} is currently saturated or locked by another process (RAM-Verified)."
            TimelineManager.log_event(envelope_data, "REQUEST_SLOT", "DENIED", msg, "RETRY_LATER")
            return False, "", msg

        slot_id = f"SLOT-{uuid.uuid4().hex[:8].upper()}"
        
        # Lock the bridge (RAM + DISK)
        TimelineManager._lock_bridge(via, slot_id, envelope_data.get("task_id", "GLOBAL"))

        msg = f"Temporal slot {slot_id} granted via {via} (RAM-Lock)."
        TimelineManager.log_event(
            envelope_data=envelope_data,
            action="REQUEST_SLOT",
            status="GRANTED",
            summary=msg,
            next_intent="EXECUTE"
        )
        
        return True, slot_id, msg

    @staticmethod
    def _lock_bridge(bridge_id: str, slot_id: str, task_id: str):
        """Records a new active lock for a bridge (RAM + DISK)."""
        lock_entry = {
            "time": datetime.now(timezone.utc).isoformat(),
            "bridge_id": bridge_id,
            "slot_id": slot_id,
            "task_id": task_id,
            "status": "active"
        }
        
        # Update RAM
        TimelineManager._ACTIVE_SLOTS[bridge_id] = lock_entry
        
        # Update DISK
        BRIDGE_LOCKS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(BRIDGE_LOCKS_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(lock_entry, ensure_ascii=False) + "\n")

    @staticmethod
    def release_slot(slot_id: str, bridge_id: str):
        """Releases the lock on a bridge (RAM + DISK)."""
        # Update RAM
        if bridge_id in TimelineManager._ACTIVE_SLOTS:
            if TimelineManager._ACTIVE_SLOTS[bridge_id].get("slot_id") == slot_id:
                del TimelineManager._ACTIVE_SLOTS[bridge_id]

        # Update DISK
        release_entry = {
            "time": datetime.now(timezone.utc).isoformat(),
            "bridge_id": bridge_id,
            "slot_id": slot_id,
            "status": "released"
        }
        with open(BRIDGE_LOCKS_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(release_entry, ensure_ascii=False) + "\n")

    @staticmethod
    def get_context(limit: int = 10):
        """Retrieves the last N events from the global timeline."""
        if not GLOBAL_TIMELINE_PATH.exists():
            return []
        
        events = []
        with open(GLOBAL_TIMELINE_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[-limit:]:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return events
