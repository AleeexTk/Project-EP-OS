import sys
import asyncio
from pathlib import Path
import json
import time
from unittest.mock import MagicMock, AsyncMock

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "alpha_pyramid_core" / "SPINE" / "16_NEXUS_ROUTER"))
sys.path.append(str(PROJECT_ROOT / "beta_pyramid_functional" / "B1_Kernel"))

from timeline import TimelineManager
from index import NexusRouter
from contracts import TaskEnvelope

import pytest

@pytest.mark.asyncio
async def test_active_spine_enforcement():
    print("--- Starting Phase 3: Active Spine Test ---")
    
    # 1. Reset State
    TimelineManager._ACTIVE_SLOTS = {}
    locks_path = PROJECT_ROOT / "state" / "bridge_locks.ndjson"
    if locks_path.exists(): locks_path.unlink()
    
    zbus = MagicMock()
    zbus.publish = AsyncMock()
    zbus.subscribe = MagicMock()
    router = NexusRouter(zbus)
    
    envelope = TaskEnvelope(
        task_id="SPINE-TEST-001",
        source_node="rogue-agent",
        target_node="execution_z1",
        action="attack",
        origin_z=17,
        metadata={"via": "ZBUS_BRIDGE"}
    )

    # 2. Test RAM Locking
    print("Pre-locking bridge ZBUS_BRIDGE...")
    TimelineManager._lock_bridge("ZBUS_BRIDGE", "LOCK-1", "HACKER")
    assert "ZBUS_BRIDGE" in TimelineManager._ACTIVE_SLOTS
    print("RAM Lock confirmed.")

    # 3. Trigger 3 failures for 'rogue-agent'
    for i in range(1, 4):
        print(f"Attempt {i} for rogue-agent...")
        result = await router.dispatch_async(envelope)
        if i < 3:
            assert result["status"] == "DENIED_BY_ATC"
            assert "rogue-agent" in router.MISBEHAVIOR_SCORES
            assert router.MISBEHAVIOR_SCORES["rogue-agent"] == i
        else:
            # 3rd failure should trigger blacklist
            assert result["status"] == "DENIED_BY_ATC"
            assert "rogue-agent" in router.BLACKLIST
            print("Blacklist triggered successfully after 3 attempts.")

    # 4. Verify Blacklist persistence
    print("Attempt 4 (Blacklisted)...")
    result_blocked = await router.dispatch_async(envelope)
    assert result_blocked["status"] == "BLACKLISTED"
    assert "is blacklisted" in result_blocked["reason"]
    print(f"Blacklist Enforcement confirmed: {result_blocked['reason']}")

    # 5. Verify Evolution Journal entry
    journal_path = PROJECT_ROOT / "gamma_pyramid_reflective" / "B_Evo_Log" / "evolution_journal.md"
    if journal_path.exists():
        with open(journal_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "Temporal Blacklist Active" in content
            assert "rogue-agent" in content
        print("Evolution Journal audit entry confirmed.")

    # 6. Test Recovery after release
    print("Releasing bridge...")
    TimelineManager.release_slot("LOCK-1", "ZBUS_BRIDGE")
    assert "ZBUS_BRIDGE" not in TimelineManager._ACTIVE_SLOTS
    
    # Still blacklisted!
    result_still_blocked = await router.dispatch_async(envelope)
    assert result_still_blocked["status"] == "BLACKLISTED"
    print("Node remains blacklisted even if bridge is released (Temporal Penalty applied).")

    print("--- Phase 3: Active Spine Test Passed ---")

if __name__ == "__main__":
    asyncio.run(test_active_spine_enforcement())
