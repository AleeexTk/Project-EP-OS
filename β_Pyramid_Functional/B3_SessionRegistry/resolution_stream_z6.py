"""
Resolution Stream Z6 (β_Pyramid_Functional)
Streams resolved state and events up from the Exec layer or Orchestrator 
out to subscribers (e.g. Observer Z4, UI). Subscribes to Z8.
"""

import logging
from typing import Dict, Any

from β_Pyramid_Functional.agent_bus_z8 import get_bus

logger = logging.getLogger(__name__)

class ResolutionStream:
    def __init__(self):
        self.bus = get_bus()
        self.target_name = "resolution_stream"
        logger.info(f"[Z6] Resolution Stream initialized on target: '{self.target_name}'")

    def start(self):
        self.bus.subscribe(self.target_name, self._on_resolution_pulse)
        logger.info("[Z6] Stream Online. Routing resolutions...")

    def _on_resolution_pulse(self, pulse: Dict[str, Any]):
        """Forward executed actions/resolutions into the Reflective (Gamma) layer."""
        source = pulse.get("source", "unknown")
        payload = pulse.get("payload", {})
        
        logger.info(f"[Z6] Streaming resolution from {source}. Payload: {payload}")
        
        # Route logic: If it's an action success, relay to Z4 Observer
        self.bus.transmit(
            source_agent="ResolutionStream_Z6",
            target="observer_relay",
            data={
                "streamed_event": "action_completed",
                "origin_source": source,
                "data": payload
            }
        )

def initialize():
    stream = ResolutionStream()
    stream.start()
    return stream

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    initialize()
