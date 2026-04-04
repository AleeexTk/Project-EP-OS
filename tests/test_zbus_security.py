import sys
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
_z12 = str(PROJECT_ROOT / "alpha_pyramid_core" / "SPINE" / "12_SEC_GUARDIAN")
if _z12 not in sys.path:
    sys.path.insert(0, _z12)

from beta_pyramid_functional.B1_Kernel.contracts import TaskEnvelope, TaskStatus
from sec_guardian import SecGuardian

@pytest.mark.asyncio
async def test_zbus_zero_trust_enforcement():
    guardian = SecGuardian()
    
    # 1. High-Z Node (Z17) WITHOUT signature -> Should be BLOCKED
    envelope_blocked = TaskEnvelope(
        task_id="ZT-TEST-001",
        source_node="architect_z17",
        target_node="nexus",
        action="manifest_node",
        origin_z=17
    )
    
    assert guardian.audit(envelope_blocked) is False
    assert envelope_blocked.status == TaskStatus.FAILED
    assert "SignatureMissing" in envelope_blocked.metadata["error"]
    print("Test 1: Unsigned Z17 blocked successfully.")

    # 2. High-Z Node (Z17) with INVALID signature format -> Should be BLOCKED
    envelope_invalid = TaskEnvelope(
        task_id="ZT-TEST-002",
        source_node="architect_z17",
        target_node="nexus",
        action="manifest_node",
        origin_z=17,
        signature="INVALID-SIG"
    )
    
    assert guardian.audit(envelope_invalid) is False
    assert "SignatureInvalid" in envelope_invalid.metadata["error"]
    print("Test 2: Invalid signature Z17 blocked successfully.")

    # 3. High-Z Node (Z7) with VALID signature -> Should be ACCEPTED
    envelope_valid = TaskEnvelope(
        task_id="ZT-TEST-003",
        source_node="bridge_z7",
        target_node="nexus",
        action="sync_structure",
        origin_z=7,
        signature="TSIG:bridge_z7:AUTHORIZED-ZT-TEST-003"
    )
    
    assert guardian.audit(envelope_valid) is True
    assert envelope_valid.status == TaskStatus.PENDING # Default from TaskEnvelope
    print("Test 3: Signed Z7 accepted successfully.")

    # 4. Low-Z Node (Z1) WITHOUT signature -> Should be ACCEPTED (no mandatory sig for Z < 7)
    envelope_low = TaskEnvelope(
        task_id="ZT-TEST-004",
        source_node="worker_z1",
        target_node="storage",
        action="read_log",
        origin_z=1
    )
    
    assert guardian.audit(envelope_low) is True
    print("Test 4: Unsigned Z1 accepted successfully.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_zbus_zero_trust_enforcement())
