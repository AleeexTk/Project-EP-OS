import sys
import os
import unittest
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(str(PROJECT_ROOT))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Handle number-prefixed dir for Z12
_z12 = str(PROJECT_ROOT / "alpha_pyramid_core" / "SPINE" / "_12_SEC_GUARDIAN")
if _z12 not in sys.path:
    sys.path.insert(0, _z12)

from beta_pyramid_functional.B1_Kernel.contracts import TaskEnvelope, TaskStatus
from sec_guardian import SecGuardian, SignatureVerifier


def _make_envelope(source="gen-bridge", origin_z=13, task_id="t001"):
    return TaskEnvelope(
        task_id=task_id,
        source_node=source,
        target_node="gen-pear",
        action="manifest_node",
        origin_z=origin_z,
        signature=SignatureVerifier.generate_signature(source, task_id),
        slot_id="slot_sec_test_01",
        payload={"z_level": 11},
        timestamp=datetime.now(timezone.utc),
    )


class TestSecGuardian(unittest.TestCase):

    def test_trusted_node_passes(self):
        print("\n[TEST] SEC_GUARDIAN: trusted Alpha node should pass")
        guardian = SecGuardian()
        env = _make_envelope(source="gen-bridge", origin_z=13)
        result = guardian.audit(env)
        self.assertTrue(result)
        print("[TEST] PASS [OK]")

    def test_spoof_blocked(self):
        print("\n[TEST] SEC_GUARDIAN: unknown node claiming Z13 origin should be blocked (anti-spoof)")
        guardian = SecGuardian()
        env = _make_envelope(source="rogue_agent_z5", origin_z=13)
        result = guardian.audit(env)
        self.assertFalse(result)
        self.assertEqual(env.status, TaskStatus.FAILED)
        self.assertIn("SpoofingAttempt", env.metadata["error"])
        print(f"[TEST] Blocked with: {env.metadata['error']}")
        print("[TEST] PASS [OK]")

    def test_rate_limit_triggers(self):
        print("\n[TEST] SEC_GUARDIAN: node exceeding rate limit should be blocked")
        guardian = SecGuardian(max_rps=3, window=60)
        env_template = _make_envelope(source="gen-meta", origin_z=15)

        for i in range(3):
            env = env_template.model_copy()
            ok = guardian.audit(env)
            self.assertTrue(ok, f"Request {i+1} should pass")

        # 4th request must be blocked
        env = env_template.model_copy()
        result = guardian.audit(env)
        self.assertFalse(result)
        self.assertEqual(env.status, TaskStatus.FAILED)
        self.assertIn("RateLimitViolation", env.metadata["error"])
        print(f"[TEST] Blocked with: {env.metadata['error']}")
        print("[TEST] PASS [OK]")


if __name__ == "__main__":
    unittest.main()
