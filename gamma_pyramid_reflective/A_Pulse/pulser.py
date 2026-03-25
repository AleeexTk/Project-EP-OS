import logging
import asyncio
import json
from typing import Callable, Awaitable
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

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
        self.violation_count = 0
        self.total_attempts = 0 # This would ideally come from the manager

    async def anchor_pulse(self):
        """Background task to sync physical reality with visual state."""
        from beta_pyramid_functional.B2_Orchestrator.manifestor import RealityAnchor
        while self.is_running:
            try:
                changed = False
                for node_id, node in self.state.nodes.items():
                    health = RealityAnchor.calculate_node_health(node_id)
                    from alpha_pyramid_core.B_Structure.models import NodeState
                    # Transition logic
                    new_state = NodeState.ACTIVE if health > 0.7 else NodeState.IDLE if health > 0.3 else NodeState.ERROR

                    if node.state != new_state:
                        node.state = new_state
                        changed = True
                
                if changed:
                    # Inject compliance metrics into the broadcast
                    compliance = self._calculate_compliance()
                    await self.manager.broadcast({
                        "type": "STATE_UPDATE", 
                        "state": self.state.model_dump(),
                        "metrics": {
                            "compliance_score": compliance,
                            "resilience_index": max(0.0, 1.0 - (self.violation_count * 0.1))
                        }
                    })
                    self.save_state(self.state)
                    
            except Exception as e:
                logging.error(f"[PULSER] Anchor Pulse Error: {e}")
            
            await asyncio.sleep(10)

    def _calculate_compliance(self) -> float:
        """Reads the violation log, counts per-node infractions, and enforces quarantine."""
        from pathlib import Path
        # Resolve path relative to project root (App root is /app in container)
        # ROOT_DIR here should be the project root
        project_root = Path(__file__).resolve().parents[3]
        log_path = project_root / "gamma_pyramid_reflective" / "B_Evo_Log" / "violations.json"
        try:
            if log_path.exists():
                with open(log_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.violation_count = len(data)
                    
                    # Automated Discipline Logic
                    node_violations = {}
                    for v in data:
                        src = v.get("source")
                        if src:
                            node_violations[src] = node_violations.get(src, 0) + 1
                    
                    for node_id, count in node_violations.items():
                        if count >= 3:
                            self._enforce_quarantine(node_id)
            
            # Simple scoring: Starts at 1.0, drops 0.05 per violation
            score = max(0.0, 1.0 - (self.violation_count * 0.05))
            return round(score, 2)
        except Exception as e:
            logging.error(f"[PULSER] Compliance Calc Error: {e}")
            return 1.0

    def _enforce_quarantine(self, node_id: str):
        """Places a node into quarantine lock if not already locked."""
        node = self.state.nodes.get(node_id)
        if node and getattr(node, "state", None) != "locked":
            node.state = "locked"
            if not getattr(node, "metadata", None):
                node.metadata = {}
            node.metadata["quarantined"] = True
            logging.warning(f"[PULSER] [DISCIPLINE] Node '{node_id}' placed in QUARANTINE due to excessive violations (>=3).")

    async def self_heal_pulse(self):
        """Background task for structural self-healing and Garbage Collection."""
        import shutil
        while self.is_running:
            try:
                from gamma_pyramid_reflective.A_Pulse.reality_monitor_z3 import RealityMonitor
                monitor = RealityMonitor()
                report = monitor.check_integrity()
                if report["status"] != "HEALTHY":
                    logging.warning(f"[PULSER] [HEALER] Integrity issues found: {len(report['issues'])}")
                    
                # V4.3 Garbage Collector (Executioner) Logic
                nodes_to_purge = []
                for node_id, node in list(self.state.nodes.items()):
                    is_locked = getattr(node, "state", None) == "locked"
                    is_renegade = "renegade" in node_id.lower() or "rogue" in node_id.lower()
                    
                    if is_locked or is_renegade:
                        nodes_to_purge.append(node_id)
                
                if nodes_to_purge:
                    from beta_pyramid_functional.B2_Orchestrator.manifestor import PhysicalManifestor
                    for node_id in nodes_to_purge:
                        try:
                            # 1. Resolve physical path
                            node_dir = PhysicalManifestor.resolve_node_dir(node_id)
                            # 2. Delete physical folder
                            if node_dir and node_dir.exists():
                                shutil.rmtree(node_dir)
                                logging.warning(f"[PULSER] [EXECUTIONER] Physically annihilated folder for '{node_id}'.")
                            else:
                                logging.warning(f"[PULSER] [EXECUTIONER] Folder for '{node_id}' not found. Removing from matrix only.")
                            
                            # 3. Erase from state matrix
                            del self.state.nodes[node_id]
                            logging.warning(f"[PULSER] [EXECUTIONER] Erased '{node_id}' from state matrix.")
                        except Exception as purge_err:
                            logging.error(f"[PULSER] [EXECUTIONER] Failed to purge '{node_id}': {purge_err}")
                            
                    # Trigger broadcast and save state
                    self.save_state(self.state)
                    await self.manager.broadcast({
                        "type": "STATE_UPDATE", 
                        "state": self.state.model_dump(),
                        "metrics": {
                            "compliance_score": self._calculate_compliance(),
                            "resilience_index": max(0.0, 1.0 - (self.violation_count * 0.1))
                        }
                    })
                    
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
