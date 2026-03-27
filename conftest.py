"""
Root conftest.py — Path bootstrap for pytest.
Adds all required project paths to sys.path so that all 7 test files
can import their dependencies without per-file path manipulation.
"""
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

# Core paths needed by most tests
_REQUIRED_PATHS = [
    PROJECT_ROOT,
    PROJECT_ROOT / "beta_pyramid_functional" / "B1_Kernel",
    PROJECT_ROOT / "beta_pyramid_functional" / "B2_ProviderMatrix",
    PROJECT_ROOT / "beta_pyramid_functional" / "B3_SessionRegistry",
    PROJECT_ROOT / "alpha_pyramid_core" / "SPINE" / "12_SEC_GUARDIAN",
    PROJECT_ROOT / "alpha_pyramid_core" / "SPINE" / "14_AUTO_CORRECTOR",
    PROJECT_ROOT / "gamma_pyramid_reflective" / "SPINE" / "2_INTEGRITY_OBSERVER",
    PROJECT_ROOT / "gamma_pyramid_reflective" / "A_Pulse",
]

for _p in _REQUIRED_PATHS:
    _s = str(_p)
    if _s not in sys.path:
        sys.path.insert(0, _s)

# Ensure tests run from project root so relative file paths in test setUp work
os.chdir(str(PROJECT_ROOT))


import pytest

@pytest.fixture(autouse=True)
def _reset_policy_manager_state():
    """
    Auto-fixture: resets SystemPolicyManager class-level singletons between tests.
    Without this, class variables (audit_log, quarantine_list, _initialized) bleed
    across tests, causing phantom violations and stale quarantine state.
    """
    # Defer import so conftest can still be loaded before sys.path is fully set
    try:
        from policy_manager import SystemPolicyManager
        SystemPolicyManager.audit_log = []
        SystemPolicyManager.quarantine_list = set()
        SystemPolicyManager.amnesty_journal = []
        SystemPolicyManager._initialized = False
    except ImportError:
        pass  # Not yet on path — tests that don't need it will still work
    yield
    # Re-reset after the test too, for clean-up
    try:
        from policy_manager import SystemPolicyManager
        SystemPolicyManager.audit_log = []
        SystemPolicyManager.quarantine_list = set()
        SystemPolicyManager.amnesty_journal = []
        SystemPolicyManager._initialized = False
    except ImportError:
        pass
