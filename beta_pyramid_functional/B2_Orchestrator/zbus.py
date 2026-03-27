import sys
import logging
from pathlib import Path

# Resolve paths to reach Z14 Canon Model
THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parents[1]

# Make sure the entire core is importable
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

z14_path = str(PROJECT_ROOT / "alpha_pyramid_core" / "SPINE" / "14_POLICY_BUS")
if z14_path not in sys.path:
    sys.path.insert(0, z14_path)

try:
    from index import zbus_instance as zbus, ZBus
    logging.info("[B2_Orchestrator Bridge] Successfully hooked into Z14 Policy Bus.")
except ImportError as e:
    logging.error(f"[B2_Orchestrator Bridge] Failed to bridge Z-Bus to Z14 Canon: {e}")
    zbus = None
    ZBus = None

