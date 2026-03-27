import sys
import os
import json
import unittest
from pathlib import Path
from datetime import datetime, timezone

# Add paths to sys.path for imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(str(PROJECT_ROOT))
sys.path.append(str(Path("beta_pyramid_functional/B1_Kernel")))
sys.path.append(str(Path("gamma_pyramid_reflective/SPINE/2_INTEGRITY_OBSERVER")))
sys.path.append(str(Path("gamma_pyramid_reflective/A_Pulse")))

from policy_manager import SystemPolicyManager, SystemPolicy
from contracts import TaskEnvelope, TaskStatus
from integrity_observer import IntegrityObserver
from pulser import PulserEngine

class TestIntegrityBridge(unittest.TestCase):
    def setUp(self):
        self.log_dir = PROJECT_ROOT / "gamma_pyramid_reflective" / "B_Evo_Log"
        self.violation_file = self.log_dir / "violations.json"
        
        # Clear previous logs if they exist for clean test
        if self.violation_file.exists():
            with open(self.violation_file, "w", encoding="utf-8") as f:
                json.dump([], f)
                
        # Also clear the class-level audit log from SystemPolicyManager
        SystemPolicyManager.audit_log = []
        SystemPolicyManager._initialized = False

    def test_end_to_end_violation(self):
        print("\n[TEST] Running End-to-End Integrity Bridge Test...")
        
        # 1. Setup Kernel and Observer
        pm = SystemPolicyManager()
        # Verify observer is instantiated, but DO NOT register it as a reporter
        # because SystemPolicyManager._log_violation already writes to the same violations.json file.
        obs = IntegrityObserver(str(self.log_dir))
        
        # 2. Trigger a Z-Level Violation (Z5 node trying to manifest Z15)
        envelope = TaskEnvelope(
            source_node="test_node_z5",
            target_node="system",
            action="manifest_node",
            origin_z=5,
            payload={"z_level": 15}
        )
        
        print("[TEST] Triggering Z-Level Violation (Z5 -> Z15)...")
        is_valid = pm.validate_action(envelope)
        
        # 3. Verify Kernel Blocked It
        self.assertFalse(is_valid, "Kernel should have blocked Z5 -> Z15 manifestation")
        self.assertEqual(envelope.status, TaskStatus.FAILED)
        
        # 4. Verify Observer Archived It
        with open(self.violation_file, "r", encoding="utf-8") as f:
            violations = json.load(f)
            
        self.assertTrue(len(violations) > 0, "Violation should be archived in violations.json")
        self.assertEqual(violations[-1]["action"], "manifest_node")
        self.assertEqual(violations[-1]["origin_z"], 5)
        print("[TEST] Violation accurately archived in Gamma layer.")

        # 5. Verify Pulser Metrics
        # Mocking the state and manager for pulser
        class MockState:
            def model_dump(self): return {}
            nodes = {}
        
        class MockManager:
            async def broadcast(self, msg): pass

        pulser = PulserEngine(MockState(), MockManager(), lambda x: None)
        score = pulser._calculate_compliance()
        
        # With 1 violation, score should be 1.0 - 0.05 = 0.95
        self.assertEqual(score, 0.95, f"Compliance score should be 0.95, got {score}")
        print(f"[TEST] Pulser Compliance Score verified: {score}")

if __name__ == "__main__":
    unittest.main()
