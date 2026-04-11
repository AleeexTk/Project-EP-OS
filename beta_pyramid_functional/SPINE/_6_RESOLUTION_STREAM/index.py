"""
EvoPyramid Node: RESOLUTION STREAM
Z-Level: 6 | Sector: SPINE

Role: Beta-layer Observability Stream.
Collects task resolution events from B2_Orchestrator (LLM, Synthesis, ZBus)
and emits standardized telemetry packets upward to Z2 Audit Bridge.

Interaction Protocol:
  - Subscribes to: TASK_RESULT, SYNTHESIS_COMPLETE, RESPONSE_COMPLETE, EXECUTE_TASK
  - Emits to ZBus topic: AUDIT_STREAM (consumed by Z2 AUDIT_BRIDGE)
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

logger = logging.getLogger("Z6.ResolutionStream")


class ResolutionStreamNode:
    """
    Z6 SPINE node. Collects resolution events from the Beta execution layer
    and forwards canonical telemetry packets to Z2 via the AUDIT_STREAM topic.
    """

    SUBSCRIBED_TOPICS = [
        "TASK_RESULT",
        "SYNTHESIS_COMPLETE",
        "RESPONSE_COMPLETE",
    ]

    def __init__(self):
        self._zbus = None
        self._active = False
        logger.info("[Z6] ResolutionStream node initialized (ACTIVE).")

    def _wrap_telemetry(self, topic: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Wraps a raw ZBus event into a canonical telemetry packet for Z2."""
        return {
            "topic": "AUDIT_STREAM",
            "payload": {
                "source_topic": topic,
                "source_z": 6,
                "layer": "beta",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": payload,
            },
        }

    async def _handle_event(self, event_dict: Dict[str, Any]):
        topic = event_dict.get("topic", "UNKNOWN")
        payload = event_dict.get("payload", {})

        logger.info(f"[Z6] Intercepted: {topic} | task_id={payload.get('task_id', 'n/a')}")

        telemetry = self._wrap_telemetry(topic, payload)
        if self._zbus:
            try:
                await self._zbus.publish(telemetry)
                logger.debug(f"[Z6] Telemetry forwarded to AUDIT_STREAM for topic={topic}.")
            except Exception as e:
                logger.error(f"[Z6] Failed to publish AUDIT_STREAM: {e}")

    def register(self):
        """Wire this node into the canonical ZBus (Z14 Policy Bus)."""
        try:
            from beta_pyramid_functional.B2_Orchestrator.zbus import zbus
            if zbus:
                self._zbus = zbus
                for topic in self.SUBSCRIBED_TOPICS:
                    zbus.subscribe(topic, self._handle_event)
                    logger.info(f"[Z6] Subscribed to ZBus topic: {topic}")
                self._active = True
            else:
                logger.warning("[Z6] ZBus not available. ResolutionStream is passive.")
        except ImportError as e:
            logger.error(f"[Z6] ZBus import failed: {e}")

    @property
    def is_active(self) -> bool:
        return self._active


# Singleton instance — imported by evo_api lifespan or test harness
resolution_stream = ResolutionStreamNode()


def main():
    """Stand-alone activation entry-point."""
    logger.info("[Z6] ResolutionStream activating stand-alone...")
    resolution_stream.register()
    if resolution_stream.is_active:
        logger.info("[Z6] ResolutionStream ONLINE — subscribed to Beta execution bus.")
    else:
        logger.warning("[Z6] ResolutionStream DEGRADED — ZBus unavailable.")


if __name__ == "__main__":
    main()
