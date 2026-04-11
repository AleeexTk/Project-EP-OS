import logging
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from alpha_pyramid_core.SPINE._14_POLICY_BUS.index import zbus_instance as zbus, ZBus

    logging.info("[B2_Orchestrator Bridge] Successfully hooked into Z14 Policy Bus.")
except ImportError as e:
    logging.error(f"[B2_Orchestrator Bridge] Failed to bridge Z-Bus to Z14 Canon: {e}")
    zbus = None
    ZBus = None
