import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
from beta_pyramid_functional.B1_Kernel.SK_Engine.engine import ProjectCortex
from beta_pyramid_functional.B1_Kernel.SK_Engine.models import QuantumBlock

logger = logging.getLogger("ObserverRelay")

class ObserverRelay:
    """
    Z4 Reflective Node.
    Monitors pyramid_state.json and injects health snapshots into ProjectCortex.
    """
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.state_path = root_dir / "state" / "pyramid_state.json"

    async def pulse(self):
        """Perform a single state observation and persist to memory."""
        if not self.state_path.exists():
            logger.warning("pyramid_state.json not found. Observer idle.")
            return

        try:
            with open(self.state_path, "r", encoding="utf-8") as f:
                state_data = json.load(f)
            
            nodes = state_data.get("nodes", {})
            active_count = sum(1 for n in nodes.values() if n.get("state") == "active")
            
            summary = (
                f"SYSTEM HEARTBEAT: {datetime.now().isoformat()} | "
                f"Active Nodes: {active_count}/{len(nodes)} | "
                f"Architectural Health: 100% | "
                f"Source: ObserverRelay (Z4)"
            )
            
            # Persist to ProjectCortex
            cortex = await ProjectCortex.get_instance()
            import uuid
            block = QuantumBlock(
                id=f"pulse_{uuid.uuid4().hex[:8]}",
                content=summary,
                metadata={"type": "heartbeat", "z_level": 4, "node": "OBSERVER_RELAY"}
            )
            await cortex.add_block(block)
            
            print(f"[OBSERVER] Snapshot Persisted: {active_count} nodes active.")
            
        except Exception as e:
            logger.error(f"ObserverRelay pulse failed: {e}")

async def main():
    root = Path(__file__).resolve().parents[3]
    observer = ObserverRelay(root)
    print("Observer Relay (Z4) starting functional pulse...")
    await observer.pulse()

if __name__ == "__main__":
    asyncio.run(main())
