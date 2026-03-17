import logging
import asyncio
from typing import Callable, Awaitable
from pathlib import Path

class PulserEngine:
    """
    Background worker engine for EvoPyramid.
    Handles periodic tasks like health checks and reality anchoring.
    """
    def __init__(self, state, manager, save_state_func: Callable):
        self.state = state
        self.manager = manager
        self.save_state = save_state_func
        self.is_running = False
        self.tasks = []

    async def anchor_pulse(self):
        """Background task to sync physical reality with visual state."""
        from manifestor import RealityAnchor
        while self.is_running:
            try:
                changed = False
                for node_id, node in self.state.nodes.items():
                    health = RealityAnchor.calculate_node_health(node_id)
                    from models import NodeState
                    # Transition logic
                    new_state = NodeState.ACTIVE if health > 0.7 else NodeState.IDLE if health > 0.3 else NodeState.ERROR

                    if node.state != new_state:
                        node.state = new_state
                        changed = True
                
                if changed:
                    await self.manager.broadcast({"type": "STATE_UPDATE", "state": self.state.model_dump()})
                    self.save_state(self.state)
                    
            except Exception as e:
                logging.error(f"[PULSER] Anchor Pulse Error: {e}")
            
            await asyncio.sleep(10)

    async def self_heal_pulse(self):
        """Background task for structural self-healing."""
        while self.is_running:
            try:
                from reality_monitor_z3 import RealityMonitor
                monitor = RealityMonitor()
                report = monitor.check_integrity()
                if report["status"] != "HEALTHY":
                    logging.warning(f"[PULSER] [HEALER] Integrity issues found: {len(report['issues'])}")
                    # Potential for auto-triggering repair here if configured
            except Exception as e:
                logging.error(f"[PULSER] Self-Heal Pulse Error: {e}")
            await asyncio.sleep(300)

    async def start(self):
        self.is_running = True
        self.tasks.append(asyncio.create_task(self.anchor_pulse()))
        self.tasks.append(asyncio.create_task(self.self_heal_pulse()))
        logging.info("[PULSER] Engine started.")

    async def stop(self):
        self.is_running = False
        for task in self.tasks:
            task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        self.tasks = []
        logging.info("[PULSER] Engine stopped.")
