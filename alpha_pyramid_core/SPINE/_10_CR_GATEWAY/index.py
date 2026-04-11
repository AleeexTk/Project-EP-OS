"""
EvoPyramid Node: CLOUD RUN GATEWAY (CR GATEWAY)
Z-Level: 10 | Sector: SPINE

Role: Alpha/Beta Boundary Cross-Talk Gateway.
Z10 sits precisely on the border between the Canon Layer (Alpha, Z11-Z17)
and the Execution Layer (Beta, Z5-Z10). It acts as a formal handover point
ensuring that cross-layer commands comply with Z-Bus contracts and Policy hierarchy.

Law of Z-Parity: Z10 is EVEN → Responsibility Bridge (Colored).
Geometric Expansion: available block 8x8 at (9,9).

Interaction Protocol:
  - Listens: EXECUTE_TASK (validates origin Z — rejects if origin_z < 10)
  - Listens: CANON_GATE_REQUEST (from Alpha SPINE to Beta execution)
  - Emits: CANON_GATE_APPROVED / CANON_GATE_REJECTED
  - Cross-validates with SystemPolicyManager before forwarding downward.
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger("Z10.CRGateway")

_REQUIRED_ORIGIN_Z_MIN = 10  # Tasks from Z < 10 must arrive via Z-Bus protocol only


class CRGatewayNode:
    """
    Z10 SPINE boundary node.
    Governs the handover of canonical policy definitions from Alpha layer
    into actionable execution packets for the Beta layer runtime.

    Hard rules enforced:
      - Z5 cannot command Z14 (RULE 5). Any envelope with origin_z < 10
        is rejected and logged.
      - All cross-Z tasks must pass SystemPolicyManager.validate_action().
    """

    def __init__(self):
        self._zbus = None
        self._active = False
        self._gate_stats = {"approved": 0, "rejected": 0}
        logger.info("[Z10] CRGateway node initialized (ACTIVE).")

    async def _handle_canon_gate_request(self, event_dict: Dict[str, Any]):
        """
        Handles formal Alpha→Beta handover requests.
        Validates origin Z-level and policy before forwarding into execution.
        """
        payload = event_dict.get("payload", {})
        envelope_data = payload.get("envelope", {})
        origin_z = int(envelope_data.get("origin_z", 0))
        task_id = envelope_data.get("task_id", "unknown")

        logger.info(f"[Z10] CANON_GATE_REQUEST received | task_id={task_id}, origin_z={origin_z}")

        # Z-parity check: only tasks from Z≥10 (Alpha) may request cross-gate passage
        if origin_z < _REQUIRED_ORIGIN_Z_MIN:
            reason = f"Z-level violation: origin_z={origin_z} is below threshold ({_REQUIRED_ORIGIN_Z_MIN})"
            logger.warning(f"[Z10] GATE REJECTED — {reason}")
            self._gate_stats["rejected"] += 1
            if self._zbus:
                await self._zbus.publish({
                    "topic": "CANON_GATE_REJECTED",
                    "payload": {
                        "task_id": task_id,
                        "reason": reason,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                })
            return

        # Policy validation
        try:
            from beta_pyramid_functional.B1_Kernel.contracts import TaskEnvelope
            from beta_pyramid_functional.B1_Kernel.policy_manager import SystemPolicyManager
            envelope = TaskEnvelope(**envelope_data)
            policy_mgr = SystemPolicyManager()
            if not policy_mgr.validate_action(envelope):
                reason = envelope.metadata.get("error", "Policy violation at Z10 gateway")
                logger.warning(f"[Z10] GATE REJECTED — policy: {reason}")
                self._gate_stats["rejected"] += 1
                if self._zbus:
                    await self._zbus.publish({
                        "topic": "CANON_GATE_REJECTED",
                        "payload": {
                            "task_id": task_id,
                            "reason": reason,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    })
                return

            # Approved — forward into execution via EXECUTE_TASK
            logger.info(f"[Z10] GATE APPROVED — forwarding task_id={task_id} to EXECUTE_TASK.")
            self._gate_stats["approved"] += 1
            if self._zbus:
                await self._zbus.publish({
                    "topic": "CANON_GATE_APPROVED",
                    "payload": {
                        "task_id": task_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                })
                await self._zbus.publish({
                    "topic": "EXECUTE_TASK",
                    "payload": {
                        "task_id": task_id,
                        "envelope": envelope_data,
                    }
                })

        except Exception as e:
            logger.error(f"[Z10] Exception during gate processing: {e}")
            self._gate_stats["rejected"] += 1

    async def _handle_execute_task_guard(self, event_dict: Dict[str, Any]):
        """
        Passive guard: observes all EXECUTE_TASK events and logs Z-level violations.
        Does not block (the primary execution handler in evo_api does the blocking);
        this node is for observability and metrics at the Z10 boundary.
        """
        payload = event_dict.get("payload", {})
        envelope_data = payload.get("envelope", {})
        origin_z = int(envelope_data.get("origin_z", 0))
        task_id = envelope_data.get("task_id", "unknown")

        if origin_z < _REQUIRED_ORIGIN_Z_MIN:
            logger.warning(
                f"[Z10] Observing EXECUTE_TASK bypass: task_id={task_id}, origin_z={origin_z} "
                f"(expected ≥{_REQUIRED_ORIGIN_Z_MIN}). Flagged for Z2 audit."
            )
            # Emit audit event for Z2 tracking
            if self._zbus:
                await self._zbus.publish({
                    "topic": "AUDIT_STREAM",
                    "payload": {
                        "source_topic": "EXECUTE_TASK_GUARD",
                        "source_z": 10,
                        "layer": "alpha_beta_boundary",
                        "data": {
                            "task_id": task_id,
                            "origin_z": origin_z,
                            "status": "Z_LEVEL_BYPASS_DETECTED",
                        },
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                })

    def register(self):
        """Wire this node into the canonical ZBus."""
        try:
            from beta_pyramid_functional.B2_Orchestrator.zbus import zbus
            if zbus:
                self._zbus = zbus
                zbus.subscribe("CANON_GATE_REQUEST", self._handle_canon_gate_request)
                zbus.subscribe("EXECUTE_TASK", self._handle_execute_task_guard)
                self._active = True
                logger.info(
                    "[Z10] CRGateway ONLINE — Alpha/Beta boundary enforced. "
                    "Subscribed to CANON_GATE_REQUEST + EXECUTE_TASK."
                )
            else:
                logger.warning("[Z10] ZBus not available. CRGateway is passive.")
        except ImportError as e:
            logger.error(f"[Z10] ZBus import failed: {e}")

    @property
    def is_active(self) -> bool:
        return self._active

    @property
    def gate_stats(self) -> Dict[str, int]:
        return dict(self._gate_stats)


# Singleton instance
cr_gateway = CRGatewayNode()


def main():
    """Stand-alone activation entry-point."""
    logger.info("[Z10] CRGateway activating stand-alone...")
    cr_gateway.register()
    if cr_gateway.is_active:
        logger.info("[Z10] CRGateway ONLINE — Alpha/Beta boundary cross-talk active.")
    else:
        logger.warning("[Z10] CRGateway DEGRADED — ZBus unavailable.")


if __name__ == "__main__":
    main()
