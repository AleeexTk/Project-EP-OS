"""
EvoPyramid Node: AUDIT BRIDGE
Z-Level: 2 | Sector: SPINE

Role: Gamma-layer Audit Relay.
Receives telemetry packets from Z6 ResolutionStream (and directly from
Z14 Policy Bus for policy violations) and persists them to the audit ledger.

Interaction Protocol:
  - Subscribes to: AUDIT_STREAM, TASK_RESULT (fallback)
  - Persists entries to: evo_data/audit_ledger.jsonl (append-only)
  - Broadcasts AUDIT_VIOLATION on critical severity events.

PEAR-CHAOS-OBSERVER: This node is the OBSERVER terminator of the cycle.
"""
import json
import logging
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger("Z2.AuditBridge")

# Resolve paths relative to this file (RULE 3 — no absolute paths)
_THIS_FILE = Path(__file__).resolve()
_PROJECT_ROOT = _THIS_FILE.parents[4]
_AUDIT_LEDGER_PATH = _PROJECT_ROOT / "evo_data" / "audit_ledger.jsonl"


class AuditBridgeNode:
    """
    Z2 SPINE node acting as the canonical Observer terminus of the PEAR-CHAOS-OBSERVER cycle.
    It receives telemetry from Z6 and writes to an immutable append-only audit ledger.
    """

    SUBSCRIBED_TOPICS = ["AUDIT_STREAM", "TASK_RESULT"]

    def __init__(self, ledger_path: Optional[Path] = None):
        self._ledger = ledger_path or _AUDIT_LEDGER_PATH
        self._ledger.parent.mkdir(parents=True, exist_ok=True)
        self._zbus = None
        self._active = False
        self._violations = 0
        logger.info(f"[Z2] AuditBridge initialized. Ledger → {self._ledger}")

    def _append_to_ledger(self, entry: Dict[str, Any]):
        """Append a single audit entry to the JSONL ledger (thread-safe append)."""
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "z_source": entry.get("source_z", 0),
            "source_topic": entry.get("source_topic", "UNKNOWN"),
            "layer": entry.get("layer", "unknown"),
            "data": entry.get("data", {}),
        }
        try:
            with open(self._ledger, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            logger.error(f"[Z2] Ledger write failed: {e}")

    async def _handle_audit_stream(self, event_dict: Dict[str, Any]):
        """Primary handler: receives canonical telemetry packets from Z6."""
        payload = event_dict.get("payload", {})
        source_topic = payload.get("source_topic", "?")
        data = payload.get("data", {})
        layer = payload.get("layer", "?")
        z_src = payload.get("source_z", 0)

        logger.info(f"[Z2] Audit entry: [{source_topic}] from Z{z_src}/{layer} | status={data.get('status', 'n/a')}")
        self._append_to_ledger(payload)

        # Detect policy violations (REJECTED or ERROR task results)
        status = str(data.get("status", "")).upper()
        if status in ("REJECTED", "ERROR"):
            self._violations += 1
            logger.warning(f"[Z2] Policy violation detected! Total violations: {self._violations}")
            if self._zbus:
                try:
                    await self._zbus.publish({
                        "topic": "AUDIT_VIOLATION",
                        "payload": {
                            "task_id": data.get("task_id"),
                            "reason": data.get("reason") or data.get("message", "Unknown"),
                            "status": status,
                            "violation_count": self._violations,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    })
                except Exception as e:
                    logger.error(f"[Z2] Failed to broadcast AUDIT_VIOLATION: {e}")

    async def _handle_task_result_fallback(self, event_dict: Dict[str, Any]):
        """
        Fallback handler: directly catches TASK_RESULT in case Z6 is not wired.
        Wraps into canonical telemetry format and reuses audit logic.
        """
        payload = event_dict.get("payload", {})
        wrapped = {
            "source_topic": "TASK_RESULT",
            "source_z": 5,  # Fallback — assume came from lowest Beta level
            "layer": "beta_fallback",
            "data": payload,
        }
        await self._handle_audit_stream({"payload": wrapped})

    def register(self):
        """Wire this node into the canonical ZBus (Z14 Policy Bus)."""
        try:
            from beta_pyramid_functional.B2_Orchestrator.zbus import zbus
            if zbus:
                self._zbus = zbus
                zbus.subscribe("AUDIT_STREAM", self._handle_audit_stream)
                zbus.subscribe("TASK_RESULT", self._handle_task_result_fallback)
                self._active = True
                logger.info("[Z2] AuditBridge ONLINE — subscribed to AUDIT_STREAM + TASK_RESULT.")
            else:
                logger.warning("[Z2] ZBus not available. AuditBridge is passive.")
        except ImportError as e:
            logger.error(f"[Z2] ZBus import failed: {e}")

    @property
    def is_active(self) -> bool:
        return self._active

    @property
    def violation_count(self) -> int:
        return self._violations

    def tail_ledger(self, n: int = 20) -> list:
        """Read the last N entries from the audit ledger."""
        if not self._ledger.exists():
            return []
        try:
            lines = self._ledger.read_text(encoding="utf-8").strip().split("\n")
            return [json.loads(l) for l in lines[-n:] if l.strip()]
        except Exception as e:
            logger.error(f"[Z2] Could not read ledger: {e}")
            return []


# Singleton instance
audit_bridge = AuditBridgeNode()


def main():
    """Stand-alone activation entry-point."""
    logger.info("[Z2] AuditBridge activating stand-alone...")
    audit_bridge.register()
    if audit_bridge.is_active:
        logger.info("[Z2] AuditBridge ONLINE — OBSERVER cycle terminus is active.")
    else:
        logger.warning("[Z2] AuditBridge DEGRADED — ZBus unavailable.")


if __name__ == "__main__":
    main()
