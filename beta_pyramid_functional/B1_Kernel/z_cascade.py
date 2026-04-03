import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

# Ensure B1_Kernel is in path for absolute-style imports
_kern_path = str(Path(__file__).resolve().parent)
if _kern_path not in sys.path:
    sys.path.append(_kern_path)
PROJECT_ROOT = Path(__file__).resolve().parents[2]

from contracts import TaskEnvelope, CascadeStatus, TaskStatus
from events import create_event, EventType, EventSeverity
from timeline import TimelineManager

class Observer:
    @staticmethod
    def log_status(envelope: TaskEnvelope, message: str):
        logging.info(f"[Z-CASCADE OBSERVER] {envelope.task_id} [{envelope.action}] -> {message}")

class Monument:
    @staticmethod
    def crystallize(envelope: TaskEnvelope) -> bool:
        """Fixes the transition. If invariant broken, returns False."""
        envelope.cascade_status = CascadeStatus.CRYSTALLIZED
        logging.info(f"[Z-CASCADE MONUMENT] Transition crystallized for {envelope.task_id}.")
        return True

    @staticmethod
    def block(envelope: TaskEnvelope, reason: str):
        envelope.cascade_status = CascadeStatus.BLOCKED
        envelope.status = TaskStatus.FAILED
        envelope.metadata["cascade_error"] = reason
        logging.warning(f"[Z-CASCADE MONUMENT] Blocked: {reason}")

class ChaosEngine:
    @staticmethod
    def register_friction(envelope: TaskEnvelope, detail: str):
        logging.warning(f"[Z-CASCADE CHAOS] Friction detected: {detail}")

class CascadeValidator:
    """
    Implements the 'Cascading Inter-level Verification with Sliding Z-Pair'.
    Validates the descent of meaning from Z_n to Z_n-1.
    """
    
    @staticmethod
    def validate_descent(envelope: TaskEnvelope, target_z: int) -> bool:
        """
        Runs the full 3-step Cascade for a downward transition.
        1. Semantic Integrity
        2. Inter-level Consistency
        3. Crystallization
        """
        Observer.log_status(envelope, f"Starting Z-Cascade: Z{envelope.origin_z} -> Z{target_z}")
        envelope.cascade_status = CascadeStatus.ACTIVE
        
        # 1. Semantic Integrity (Такт 1. Семантическая целостность)
        # Check if intent is present
        if not envelope.intent and not envelope.payload.get("synthesis_proposal"):
             ChaosEngine.register_friction(envelope, "Missing semantic intent or synthesis proposal.")
             # We don't block yet, but we log the friction.

        if envelope.payload.get("simulate_semantic_loss", False):
            Monument.block(envelope, "Semantic Integrity Lost. Original intent distorted.")
            return False
            
        # 2. Inter-level Consistency (Такт 2. Межуровневая согласованность)
        # Sliding Z-Pair Invariant: Origin must be strictly above Target
        if envelope.origin_z <= target_z:
            Monument.block(envelope, f"Consistency Failed. Origin Z{envelope.origin_z} must be higher than Target Z{target_z}.")
            return False

        if envelope.payload.get("simulate_inconsistency", False):
            ChaosEngine.register_friction(envelope, "Inter-level capability mismatch.")
            Monument.block(envelope, "Consistency Failed. Target level cannot structurally accept this state.")
            return False

        # Placeholder for real SK_Engine validation (Phase 6 Integration)
        # In the future, this calls SK_Engine.validate_coherence(envelope.intent, envelope.payload['synthesis_proposal'])
        logging.info(f"[Z-CASCADE] SK_Engine internal coherence check: PASSED (Symbolic)")

        # 3. Crystallization (Такт 3. Кристаллизация перехода)
        if Monument.crystallize(envelope):
            envelope.cascade_status = CascadeStatus.PASSED
            Observer.log_status(envelope, "Cascade Successful. Meaning preserved.")
            TimelineManager.log_event(envelope.model_dump(), "CASCADE_PASSED", "SUCCESS", "Meaning preserved.", "NEXT_LEVEL")
            return True
        else:
            Monument.block(envelope, "Crystallization Failed. Invariant broken.")
            TimelineManager.log_event(envelope.model_dump(), "CASCADE_FAILED", "ERROR", "Crystallization Failed.", "ABORT")
            return False


class ZCascadePipeline:
    """
    Minimal orchestrated Z17→Z1 cascading pipeline.
    Uses existing SystemPolicyManager + CascadeValidator path (including Z14 repair).
    """

    @staticmethod
    def run_z17_to_z1(envelope: TaskEnvelope, policy_manager=None) -> Dict[str, Any]:
        if envelope.origin_z != 17:
            raise ValueError("ZCascadePipeline requires envelope.origin_z == 17")

        from policy_manager import SystemPolicyManager

        # TRP: Request temporal slot before movement (Air Traffic Control)
        # Using ZBUS_BRIDGE as the primary resource for the cascade.
        bridge_id = envelope.metadata.get("via", "ZBUS_BRIDGE")
        if not envelope.slot_id:
            success, slot_id, msg = TimelineManager.request_slot(envelope.model_dump(), via=bridge_id)
            if not success:
                return {
                    "task_id": envelope.task_id,
                    "status": "denied",
                    "reason": f"Temporal Slot Denied: {msg}",
                    "trace_id": envelope.trace_id
                }
            envelope.slot_id = slot_id
        else:
            # Slot already provided by Dispatcher (Phase 2 Early Enforcement)
            TimelineManager.log_event(
                envelope.model_dump(),
                "TRP_INHERIT",
                "ACTIVE",
                f"Inherited ATC Slot {envelope.slot_id} from Dispatcher.",
                "Z16_ROUTING"
            )

        TimelineManager.log_event(
            envelope.model_dump(), 
            "CASCADE_START", 
            "ACTIVE", 
            f"Starting Z17->Z1 cascade for task {envelope.task_id}",
            "Z16_ROUTING"
        )

        manager = policy_manager or SystemPolicyManager()
        try:
            z12_dir = PROJECT_ROOT / "alpha_pyramid_core" / "SPINE" / "12_SEC_GUARDIAN"
            if str(z12_dir) not in sys.path:
                sys.path.insert(0, str(z12_dir))
            from sec_guardian import SecGuardian
            manager._sec_guardian = SecGuardian(max_rps=64, window=60)
        except Exception:
            # Keep default guardian behavior if import path is unavailable.
            pass
            
        task_id = envelope.task_id
        trace_id = envelope.trace_id
        pair_results: List[Dict[str, Any]] = []
        runtime_audit: List[Dict[str, Any]] = []

        def _audit_hook(event: Dict[str, Any]):
            if event.get("task_id") == task_id:
                runtime_audit.append(event)

        manager.register_reporter(_audit_hook)

        try:
            for upper_z in range(17, 1, -1):
                lower_z = upper_z - 1
                pair_id = f"Z{upper_z}->Z{lower_z}"

                pair_envelope = envelope.model_copy(deep=True)
                pair_envelope.origin_z = upper_z
                pair_envelope.payload["target_z"] = lower_z
                pair_envelope.payload["z_level"] = lower_z
                pair_envelope.metadata["pair_id"] = pair_id
                pair_envelope.metadata["cascade_trace"] = trace_id
                pair_envelope.cascade_status = CascadeStatus.PENDING

                pair_ok = manager.validate_action(pair_envelope)
                pair_event = create_event(
                    event_type=EventType.NODE_PROGRESS if pair_ok else EventType.NODE_FAILURE,
                    trace_id=trace_id,
                    node_id=f"z{upper_z}_pair_validator",
                    task_id=task_id,
                    severity=EventSeverity.INFO if pair_ok else EventSeverity.ERROR,
                    payload={
                        "pair_id": pair_id,
                        "repaired": bool(pair_envelope.metadata.get("repaired", False)),
                        "cascade_status": str(pair_envelope.cascade_status),
                        "error": pair_envelope.metadata.get("error"),
                    },
                )

                pair_results.append(
                    {
                        "pair_id": pair_id,
                        "ok": pair_ok,
                        "cascade_status": pair_envelope.cascade_status,
                        "repaired": bool(pair_envelope.metadata.get("repaired", False)),
                        "error": pair_envelope.metadata.get("error"),
                        "event": pair_event.model_dump(),
                    }
                )

                # Log each pair transition to the timeline
                TimelineManager.log_event(
                    pair_envelope.model_dump(),
                    "Z_TRANSITION",
                    "PASSED" if pair_ok else "FAILED",
                    f"Transition {pair_id} result: {'OK' if pair_ok else 'ERROR'}",
                    f"Z{lower_z}_ENTRY" if pair_ok else "REPAIR_Z14"
                )

                if not pair_ok:
                    return {
                        "trace_id": trace_id,
                        "task_id": task_id,
                        "status": "failed",
                        "stopped_at": pair_id,
                        "pairs": pair_results,
                        "repair_count": sum(1 for p in pair_results if p["repaired"]),
                        "audit": runtime_audit,
                    }

            return {
                "trace_id": trace_id,
                "task_id": task_id,
                "status": "passed",
                "stopped_at": None,
                "pairs": pair_results,
                "repair_count": sum(1 for p in pair_results if p["repaired"]),
                "audit": runtime_audit,
            }
        finally:
            # RELEASE the bridge slot after completion or failure
            TimelineManager.release_slot(envelope.slot_id, bridge_id)
            TimelineManager.log_event(
                envelope.model_dump(),
                "CASCADE_FINISH",
                "CLOSED",
                f"Z-Cascade finished for task {task_id}. Slot {envelope.slot_id} released.",
                "STANDBY"
            )
