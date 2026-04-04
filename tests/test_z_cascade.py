import sys
import os
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(str(PROJECT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from beta_pyramid_functional.B1_Kernel.policy_manager import SystemPolicyManager
from beta_pyramid_functional.B1_Kernel.contracts import TaskEnvelope, CascadeStatus, TaskStatus
from alpha_pyramid_core.SPINE._12_SEC_GUARDIAN.sec_guardian import SignatureVerifier

class TestZCascadeProtocol(unittest.TestCase):
    def setUp(self):
        self.pm = SystemPolicyManager()
        
    def test_successful_cascade(self):
        print("\n[TEST] Z-Cascade: Testing Full Semantic Crystallization (Z15 -> Z5)")
        
        envelope = TaskEnvelope(
            task_id="t_success",
            source_node="architect_z15",
            target_node="system",
            action="manifest_node",
            origin_z=15,
            signature=SignatureVerifier.generate_signature("architect_z15", "t_success"),
            slot_id="slot_z15_success",
            payload={"z_level": 5}
        )
        
        is_valid = self.pm.validate_action(envelope)
        
        self.assertTrue(is_valid, "Cascade should pass without simulated failures.")
        self.assertEqual(envelope.cascade_status, CascadeStatus.PASSED)
        print("[TEST] SUCCESS: Meaning descended and crystallized without distortion.")

    def test_failed_cascade_semantic_loss(self):
        print("\n[TEST] Z-Cascade: Testing Semantic Integrity Loss (Z15 -> Z5)")
        print("[TEST] (V6: Distorted task should be intercepted and REPAIRED by Z14 Auto-Corrector)")

        envelope = TaskEnvelope(
            source_node="architect_z15",
            target_node="system",
            action="manifest_node",
            origin_z=15,
            signature=SignatureVerifier.generate_signature("architect_z15", "t_fail"),
            slot_id="slot_z15_fail",
            task_id="t_fail",
            intent="Original architect intent.",
            payload={
                "z_level": 5,
                "simulate_semantic_loss": True
            }
        )

        is_valid = self.pm.validate_action(envelope)

        # V6 behaviour: Z14 Auto-Corrector intercepts the block and repairs the task.
        # Valid result is now True (repaired), not False (blocked).
        self.assertTrue(is_valid, "V6: Z14 should intercept Monument block and repair the task.")
        self.assertEqual(envelope.cascade_status, CascadeStatus.CRYSTALLIZED,
                         "After repair, task should be CRYSTALLIZED — not BLOCKED.")
        print("[TEST] SUCCESS: Monument blocked, Z14 intercepted, task was CRYSTALLIZED.")

if __name__ == "__main__":
    unittest.main()
