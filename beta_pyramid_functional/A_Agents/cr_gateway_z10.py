"""
CR Gateway Z10 (β_Pyramid_Functional)
Cognitive Response Gateway. Routes and processes complex reasoning 
tasks by interfacing with LLMs and the Z8 Agent Bus.
"""

import logging
import asyncio
from typing import Dict, Any

# Ensure we can import from B1_Kernel and B2_Orchestrator
from β_Pyramid_Functional.agent_bus_z8 import get_bus
from β_Pyramid_Functional.B2_Orchestrator.llm_orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)

class CRGateway:
    def __init__(self):
        self.bus = get_bus()
        self.target_name = "cr_gateway"
        logger.info(f"[Z10] CR Gateway initialized, attaching to AgentBusZ8 target: '{self.target_name}'")

    def start(self):
        """Attaches to the Z8 event bus."""
        self.bus.subscribe(self.target_name, self._on_pulse_received)
        logger.info("[Z10] Gateway Online. Listening on Z8.")

    def _on_pulse_received(self, pulse: Dict[str, Any]):
        """Callback triggered when Z8 bus routes a pulse to 'cr_gateway'."""
        source = pulse.get("source", "unknown")
        payload = pulse.get("payload", {})
        logger.info(f"[Z10] Received pulse from {source}. Payload: {payload}")
        
        # In the future, this is where we invoke LLMs via AgentOrchestrator.
        # For now, we reflect a summary response back to chaos_bus or source.
        response_payload = {
            "status": "processed_by_z10",
            "original_query": payload,
            "cognitive_result": f"Z10 acknowledged cognition request from {source}"
        }
        
        # Send resolution out back to the bus
        self.bus.transmit(
            source_agent="CRGateway_Z10",
            target="chaos_bus",
            data=response_payload
        )

def initialize():
    gateway = CRGateway()
    gateway.start()
    return gateway

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    initialize()
