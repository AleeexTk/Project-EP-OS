"""
conftest.py — Sprint 9 Harmonization
Provides a single, canonical PROJECT_ROOT injection for all tests.
This replaces per-file sys.path hacks in every test module.
"""
import sys
from pathlib import Path

# Single canonical injection point for the entire test suite
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
