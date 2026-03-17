import asyncio
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any

# --- Kernel Path Initialization ---
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR / "beta_pyramid_functional" / "B1_Kernel") not in sys.path:
    sys.path.append(str(ROOT_DIR / "beta_pyramid_functional" / "B1_Kernel"))

from base_node import BaseServiceNode, node_entry
from events import (
    EventType, EventSeverity, ProviderPayload, FallbackPayload, FailurePayload
)

try:
    from session_models import Provider
except ImportError:
    from enum import Enum
    class Provider(str, Enum):
        GEMINI = "gemini"
        OLLAMA = "ollama"

# ─────────────────────────────────────────
#  Spine Health Observer Task
# ─────────────────────────────────────────

@node_entry
class SpineHealthObserver(BaseServiceNode):
    """
    Exemplary autonomous service node.
    Inherits from BaseServiceNode for unified lifecyle, events, and paths.
    """
    
    def __init__(self, trace_id: Optional[str] = None, simulation: bool = False):
        super().__init__(node_id="spine_health_observer", trace_id=trace_id, simulation=simulation)
        self.primary_provider = Provider.GEMINI
        self.fallback_provider = Provider.OLLAMA

    def scan_for_manifests(self) -> int:
        """Scan project for .node_manifest.json and return count."""
        count = 0
        for root, dirs, files in os.walk(ROOT_DIR):
            if ".node_manifest.json" in files:
                count += 1
        return count

    async def simulate_provider_call(self, provider: Provider, task: str, should_fail: bool) -> dict:
        """Simulate an LLM call which might timeout."""
        await asyncio.sleep(1.0) 
        if should_fail:
            raise TimeoutError(f"Provider {provider.value} failed on Z7 SLA.")
        return {"result": "ok", "message": f"Verified with {provider.value}"}

    async def run(self, task_id: str, session_id: Optional[str] = None):
        """Main execution logic for the node using the canonical lifecycle."""
        
        # 1. NODE_START
        await self.publish(
            event_type=EventType.NODE_START,
            task_id=task_id, 
            session_id=session_id,
            payload={"action": "manifest_integrity_scan"}
        )

        # 2. PROVIDER_SELECTED
        await self.publish(
            event_type=EventType.PROVIDER_SELECTED,
            task_id=task_id,
            payload=ProviderPayload(
                provider_name=self.primary_provider.value,
                model="gemini-1.5-pro"
            ).model_dump()
        )

        manifest_count = self.scan_for_manifests()
        self.logger.info(f"Targets: {manifest_count} manifests.")

        # 3. Execution Phase
        try:
            await self.simulate_provider_call(self.primary_provider, "verify_manifests", self.simulation)
            
            # SUCCESS
            await self.publish(
                event_type=EventType.NODE_COMPLETE,
                task_id=task_id,
                payload={"manifests_checked": manifest_count, "integrity": "nominal"}
            )

        except TimeoutError as e:
            # 4. PROVIDER_TIMEOUT
            await self.publish(
                event_type=EventType.PROVIDER_TIMEOUT,
                task_id=task_id,
                severity=EventSeverity.WARNING,
                payload=FailurePayload(error_code="TIMEOUT_Z7", message=str(e)).model_dump()
            )
            
            # 5. NODE_FALLBACK_INIT
            await self.publish(
                event_type=EventType.NODE_FALLBACK_INIT,
                task_id=task_id,
                severity=EventSeverity.WARNING,
                payload=FallbackPayload(
                    from_provider=self.primary_provider.value,
                    to_provider=self.fallback_provider.value,
                    reason="Target provider unresponsive",
                    trigger_node=self.node_id
                ).model_dump()
            )
            
            try:
                # 6. Fallback Execution
                self.logger.info("Executing Fallback Recovery...")
                await self.simulate_provider_call(self.fallback_provider, "verify_manifests", False)
                
                # 7. NODE_RECOVERY_SUCCESS
                await self.publish(
                    event_type=EventType.NODE_RECOVERY_SUCCESS,
                    task_id=task_id,
                    payload={"recovered_via": self.fallback_provider.value, "manifests_checked": manifest_count}
                )
            except Exception as fe:
                # 8. NODE_FAILURE (CRITICAL)
                await self.publish(
                    event_type=EventType.NODE_FAILURE,
                    task_id=task_id,
                    severity=EventSeverity.CRITICAL,
                    payload=FailurePayload(error_code="RECOVERY_FAILED", message=str(fe)).model_dump()
                )

async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Spine Health Observer (BaseNode Implementation).")
    parser.add_argument("--chaos-mode", action="store_true", help="Trigger fallback simulation.")
    args = parser.parse_args()

    # Initializing standardized logger
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    
    task_id = f"task-{int(time.time())}"
    observer = SpineHealthObserver(simulation=args.chaos_mode)
    await observer.run(task_id)

if __name__ == "__main__":
    asyncio.run(main())
