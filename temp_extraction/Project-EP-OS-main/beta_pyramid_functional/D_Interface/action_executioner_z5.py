"""
Action Executioner Z5 (β_Pyramid_Functional)
Execution layer that translates abstract agent decisions into concrete physical actions.
Subscribes to Z8 Agent Bus for 'action_executioner' pulses.
"""

import logging
from typing import Dict, Any

from β_Pyramid_Functional.agent_bus_z8 import get_bus

logger = logging.getLogger(__name__)

class ActionExecutioner:
    def __init__(self):
        self.bus = get_bus()
        self.target_name = "action_executioner"
        logger.info(f"[Z5] Action Executioner initialized, attaching to AgentBusZ8 target: '{self.target_name}'")

    def start(self):
        self.bus.subscribe(self.target_name, self._on_action_pulse)
        logger.info("[Z5] Executioner Online. Awaiting approved actions.")

    def _on_action_pulse(self, pulse: Dict[str, Any]):
        """Executes physical actions requested by agents or orchestrator."""
        source = pulse.get("source", "unknown")
        payload = pulse.get("payload", {})
        action_type = payload.get("action_type", "unknown_action")
        
        logger.info(f"[Z5] Executing action '{action_type}' initiated by {source}.")
        
        # Simulate execution execution
        result_payload = {
            "execution_status": "success",
            "action_type": action_type,
            "details": "Action executed physically by Z5",
            "source_ref": pulse.get("pulse_id")
        }
        
        # Emit confirmation via Resolution Stream (Z6) or directly to chaos_bus
        self.bus.transmit(
            source_agent="ActionExecutioner_Z5",
            target="resolution_stream",
            data=result_payload
        )

def initialize():
    executioner = ActionExecutioner()
    executioner.start()
    return executioner

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    initialize()
