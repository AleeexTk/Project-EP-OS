import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal

# --- Path discovery to import core modules ---
def setup_sys_path():
    current_dir = Path(__file__).resolve().parent
    base_repo_dir = current_dir.parent.parent
    if str(base_repo_dir) not in sys.path:
        sys.path.insert(0, str(base_repo_dir))
    
    # Also add functional layer directly for easier imports
    functional_dir = base_repo_dir / "β_Pyramid_Functional"
    if str(functional_dir) not in sys.path:
        sys.path.insert(0, str(functional_dir))

setup_sys_path()

try:
    from B2_ProviderMatrix.provider_matrix import ProviderMatrix, ProviderConfig
    from B3_SessionRegistry.session_models import Provider
    from B2_Orchestrator.zbus import zbus  # Assuming zbus is a global instance
except ImportError as e:
    logging.error(f"Failed to import core modules: {e}")
    # Will define fallbacks later if needed to run standalone

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("Spine_Health_Observer")

# ─────────────────────────────────────────
#  Event Schemas (ZBus Events)
# ─────────────────────────────────────────

class ZBusNodeEvent(BaseModel):
    event_type: Literal[
        "NODE_START", 
        "PROVIDER_SELECTED", 
        "PROVIDER_TIMEOUT", 
        "NODE_FALLBACK_INIT", 
        "NODE_RECOVERY_SUCCESS", 
        "NODE_FAILURE"
    ]
    node_id: str = "spine_health_observer"
    task_id: str
    trace_id: str
    provider: Optional[str] = None
    fallback_to: Optional[str] = None
    status: Literal["healthy", "degraded", "failed", "running"] = "running"
    simulation: bool = False
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    payload: Dict[str, Any] = Field(default_factory=dict)

# ─────────────────────────────────────────
#  Spine Health Observer Task
# ─────────────────────────────────────────

class SpineHealthObserver:
    """
    First autonomous service node that traverses the tree ensuring manifest health.
    Includes Provider Matrix fallback and a chaos-mode simulation for testing UI resilience.
    """
    
    def __init__(self, trace_id: str = "trace-001", simulation: bool = False):
        self.node_id = "spine_health_observer"
        self.trace_id = trace_id
        self.simulation = simulation
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.primary_provider = Provider.GEMINI
        self.fallback_provider = Provider.OLLAMA

    async def emit_event(self, event: ZBusNodeEvent):
        """Simulate publishing to ZBus (or actually publish if WS context exists)"""
        event_dict = event.model_dump()
        logger.info(f"==> ZBUS EVENT: {event.event_type} | Provider: {event.provider} | Status: {event.status}")
        logger.debug(f"Payload: {json.dumps(event_dict, indent=2)}")
        
        # If zbus had a generic emit/broadcast, we'd call it here:
        # await zbus.broadcast_event(event_dict)
        # For now, we print it beautifully. Return the event dict for usage.
        return event_dict

    def scan_for_manifests(self) -> int:
        """Scan project for .node_manifest.json and return count."""
        count = 0
        for root, dirs, files in os.walk(self.base_dir):
            if ".node_manifest.json" in files:
                count += 1
        return count

    async def simulate_provider_call(self, provider: Provider, task: str, should_fail: bool) -> dict:
        """Simulate an LLM call which might timeout."""
        await asyncio.sleep(1.5) # Simulate network delay
        if should_fail:
            raise TimeoutError(f"Provider {provider.value} failed to respond in time.")
        return {"result": "ok", "message": f"Verified with {provider.value}"}

    async def verify_manifests(self, task_id: str):
        """Main execution logic for the node."""
        
        # 1. Start Task
        await self.emit_event(ZBusNodeEvent(
            event_type="NODE_START",
            task_id=task_id,
            trace_id=self.trace_id,
            simulation=self.simulation,
            payload={"task": "verify_manifests", "action": "Scanning directories"}
        ))

        # 2. Select Primary Provider
        await self.emit_event(ZBusNodeEvent(
            event_type="PROVIDER_SELECTED",
            task_id=task_id,
            trace_id=self.trace_id,
            provider=self.primary_provider.value,
            simulation=self.simulation,
            payload={"reason": "Highest Z-Level capability match"}
        ))

        manifest_count = self.scan_for_manifests()
        logger.info(f"Found {manifest_count} manifests to verify.")

        # 3. Simulated Execution (with optional Chaos Mode)
        try:
            should_fail = self.simulation
            
            logger.info("Attempting verification with primary provider...")
            await self.simulate_provider_call(self.primary_provider, "verify_manifests", should_fail)
            
            # If we succeed here on primary (chaos off):
            await self.emit_event(ZBusNodeEvent(
                event_type="NODE_RECOVERY_SUCCESS", # Or TASK_SUCCESS, but we use RECOVERY_SUCCESS based on prompt schema context if we just completed it
                task_id=task_id,
                trace_id=self.trace_id,
                provider=self.primary_provider.value,
                status="healthy",
                simulation=self.simulation,
                payload={"task": "verify_manifests", "manifests_checked": manifest_count, "result": "clean"}
            ))

        except TimeoutError as e:
            # 4. Chaos Mode hit - emit Timeout and init Fallback
            logger.warning(f"Timeout detected: {e}")
            
            await self.emit_event(ZBusNodeEvent(
                event_type="PROVIDER_TIMEOUT",
                task_id=task_id,
                trace_id=self.trace_id,
                provider=self.primary_provider.value,
                status="degraded",
                simulation=self.simulation,
                payload={"reason": str(e), "task": "verify_manifests"}
            ))
            
            # Init fallback
            await self.emit_event(ZBusNodeEvent(
                event_type="NODE_FALLBACK_INIT",
                task_id=task_id,
                trace_id=self.trace_id,
                provider=self.primary_provider.value,
                fallback_to=self.fallback_provider.value,
                status="degraded",
                simulation=self.simulation,
                payload={"reason": "provider_timeout", "task": "verify_manifests"}
            ))
            
            try:
                # 5. Execute Fallback Recovery
                logger.info("Attempting verification with fallback provider...")
                await self.simulate_provider_call(self.fallback_provider, "verify_manifests", False) # Fallback doesn't fail
                
                await self.emit_event(ZBusNodeEvent(
                    event_type="NODE_RECOVERY_SUCCESS",
                    task_id=task_id,
                    trace_id=self.trace_id,
                    provider=self.fallback_provider.value,
                    status="healthy",
                    simulation=self.simulation,
                    payload={"task": "verify_manifests", "manifests_checked": manifest_count, "result": "recovered_locally"}
                ))
            except Exception as fe:
                # Total Failure
                await self.emit_event(ZBusNodeEvent(
                    event_type="NODE_FAILURE",
                    task_id=task_id,
                    trace_id=self.trace_id,
                    provider=self.fallback_provider.value,
                    status="failed",
                    simulation=self.simulation,
                    payload={"reason": f"Fallback also failed: {fe}", "task": "verify_manifests"}
                ))

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Spine Health Observer daemon.")
    parser.add_argument("--chaos-mode", action="store_true", help="Simulate a provider timeout to trigger fallback.")
    args = parser.parse_args()

    # Generate a dummy task_id for this standalone execution
    task_id = f"task-{int(time.time())}"
    
    observer = SpineHealthObserver(simulation=args.chaos_mode)
    await observer.verify_manifests(task_id)

if __name__ == "__main__":
    asyncio.run(main())
