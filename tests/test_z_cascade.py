import sys
import os
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(str(PROJECT_ROOT))
sys.path.append(str(Path("beta_pyramid_functional/B1_Kernel")))

from policy_manager import SystemPolicyManager
from contracts import TaskEnvelope, CascadeStatus, TaskStatus

class TestZCascadeProtocol(unittest.TestCase):
    def setUp(self):
        self.pm = SystemPolicyManager()
        
    def test_successful_cascade(self):
        print("\n[TEST] Z-Cascade: Testing Full Semantic Crystallization (Z15 -> Z5)")
        
        envelope = TaskEnvelope(
            source_node="architect_z15",
            target_node="system",
            action="manifest_node",
            origin_z=15,
            payload={"z_level": 5}
        )
        
        is_valid = self.pm.validate_action(envelope)
        
        self.assertTrue(is_valid, "Cascade should pass without simulated failures.")
        self.assertEqual(envelope.cascade_status, CascadeStatus.PASSED)
        print("[TEST] SUCCESS: Meaning descended and crystallized without distortion.")

    def test_failed_cascade_semantic_loss(self):
        print("\n[TEST] Z-Cascade: Testing Semantic Integrity Loss (Z15 -> Z5)")
        
        envelope = TaskEnvelope(
            source_node="architect_z15",
            target_node="system",
            action="manifest_node",
            origin_z=15,
            payload={
                "z_level": 5, 
                "simulate_semantic_loss": True
            }
        )
        
        is_valid = self.pm.validate_action(envelope)
        
        self.assertFalse(is_valid, "Cascade should fail if semantic integrity is lost.")
        self.assertEqual(envelope.cascade_status, CascadeStatus.BLOCKED)
        self.assertEqual(envelope.status, TaskStatus.FAILED)
        self.assertIn("Semantic Integrity Lost", envelope.metadata.get("cascade_error", ""))
        print("[TEST] SUCCESS: Monument blocked the distorted transition.")

if __name__ == "__main__":
    unittest.main()
