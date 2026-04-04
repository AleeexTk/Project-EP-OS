import sys
import asyncio
from pathlib import Path
import json
from unittest.mock import MagicMock, AsyncMock

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Handle number-prefixed dir for Z16
_z16 = str(PROJECT_ROOT / "alpha_pyramid_core" / "SPINE" / "_16_NEXUS_ROUTER")
if _z16 not in sys.path:
    sys.path.insert(0, _z16)

from beta_pyramid_functional.B1_Kernel.timeline import TimelineManager
from index import NexusRouter
from beta_pyramid_functional.B1_Kernel.contracts import TaskEnvelope

async def test_gatekeeper_rejection():
    print("--- Starting Nexus Gatekeeper Test ---")
    
    # Setup mock Z-Bus
    zbus = MagicMock()
    zbus.publish = AsyncMock()
    zbus.subscribe = MagicMock()
    
    router = NexusRouter(zbus)
    
    envelope = TaskEnvelope(
        task_id="GATEKEEPER-TEST-001",
        source_node="test-agent",
        target_node="execution_z1",
        action="test",
        origin_z=17,
        metadata={"via": "ZBUS_BRIDGE"}
    )
    
    # 1. Manually LOCK the bridge in state
    TimelineManager._lock_bridge("ZBUS_BRIDGE", "LOCK-SLOT-001", "TEST-TASK")
    print("Bridge ZBUS_BRIDGE locked manually.")
    
    # 2. Try to dispatch via NexusRouter (Should be DENIED)
    result = await router.dispatch_sync(envelope)
    print(f"Sync Dispatch Result: {result.get('status')} - {result.get('reason')}")
    assert result["status"] == "DENIED_BY_ATC"
    zbus.publish.assert_not_called()
    
    # 3. Unlock bridge
    TimelineManager.release_slot("LOCK-SLOT-001", "ZBUS_BRIDGE")
    print("Bridge released.")
    
    # 4. Try again (Should be GRANTED)
    # We use dispatch_async to avoid waiting for Z-Bus result future
    result2 = await router.dispatch_async(envelope)
    print(f"Async Dispatch Result: {result2.get('status')} - {result2.get('slot_id')}")
    assert result2["status"] == "ACCEPTED_ASYNC"
    assert "slot_id" in result2
    zbus.publish.assert_called_once()
    
    print("--- Nexus Gatekeeper Test Passed ---")

if __name__ == "__main__":
    # Clean state before test
    locks_path = PROJECT_ROOT / "state" / "bridge_locks.ndjson"
    if locks_path.exists():
        locks_path.unlink()
        
    asyncio.run(test_gatekeeper_rejection())
