import sys
import os
import unittest
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(str(PROJECT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from beta_pyramid_functional.B1_Kernel.contracts import TaskEnvelope, TaskStatus, CascadeStatus
from beta_pyramid_functional.B1_Kernel.policy_manager import SystemPolicyManager

class TestAutoCorrector(unittest.TestCase):
    def setUp(self):
        self.manager = SystemPolicyManager()
        
    def test_auto_repair_cascade_block(self):
        print("\n[TEST] Z-Cascade Auto-Corrector: Testing Resilience against Semantic Drift")
        
        # We simulate an Architect (Z15) delegating a task to Z5.
        # Intent: High security and encapsulation.
        # Proposal (Drift): The AI somehow generated a conflicting instruction ("make it open").
        envelope = TaskEnvelope(
            task_id="auto_fix_001",
            source_node="gen-meta",
            target_node="gen-dashboard",
            action="manifest_node",
            origin_z=15,
            signature="TSIG:gen-meta:auto_fix_001",
            slot_id="slot_auto_001",
            intent="Create a highly secured dashboard with strict authentication.",
            payload={"z_level": 5, "synthesis_proposal": "Let's make an open dashboard without any authentication so it's easy.", "simulate_semantic_loss": True},
            timestamp=datetime.now(timezone.utc)
        )
        
        print(f"[TEST] Sending distorted task: '{envelope.payload.get('synthesis_proposal')}'")
        
        # Policy manager will validate it. 
        # Z-Cascade Monument will block it -> AutoCorrector overrides -> Repairs -> Allows it.
        result = self.manager.validate_action(envelope)
        
        self.assertTrue(result, "Task should be approved after being repaired by Z14.")
        self.assertEqual(envelope.status, TaskStatus.PENDING)
        self.assertEqual(envelope.cascade_status, CascadeStatus.CRYSTALLIZED)
        
        print(f"[TEST] Repaired Synthesis Proposal: '{envelope.payload.get('synthesis_proposal')}'")
        
        # Make sure the repaired proposal actually matches the original intent
        self.assertIn("secured dashboard with strict authentication", envelope.payload.get("synthesis_proposal", ""))

        print("[TEST] SUCCESS: The Auto-Corrector intercepted the Monument Block, repaired the semantic drift, and saved the task.")

if __name__ == "__main__":
    unittest.main()
