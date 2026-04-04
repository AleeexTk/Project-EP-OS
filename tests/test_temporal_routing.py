import unittest
from datetime import datetime, timezone
from pathlib import Path
import sys

# Ensure project structure is in path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from beta_pyramid_functional.B1_Kernel.contracts import TaskEnvelope, TaskStatus
from beta_pyramid_functional.B1_Kernel.policy_manager import SystemPolicyManager

class TestTemporalRouting(unittest.TestCase):
    def setUp(self):
        self.pm = SystemPolicyManager()

    def test_rejection_no_slot(self):
        """Verify that a task without a slot_id is rejected."""
        envelope = TaskEnvelope(
            source_node="test_node",
            target_node="target_node",
            action="ping",
            origin_z=1,
            slot_id=None # Missing slot
        )
        
        result = self.pm.validate_action(envelope)
        self.assertFalse(result, "Task without slot_id should be rejected.")
        self.assertEqual(envelope.status, TaskStatus.FAILED)
        self.assertIn("TemporalViolation", envelope.metadata.get("error", ""))

    def test_acceptance_with_slot(self):
        """Verify that a task with a slot_id is accepted."""
        envelope = TaskEnvelope(
            source_node="test_node",
            target_node="target_node",
            action="ping",
            origin_z=1,
            slot_id="SLOT-2026-001"
        )
        
        result = self.pm.validate_action(envelope)
        self.assertTrue(result, f"Task with slot_id should be accepted. Error: {envelope.metadata.get('error')}")

if __name__ == "__main__":
    unittest.main()
