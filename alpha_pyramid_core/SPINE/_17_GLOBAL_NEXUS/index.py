"""
EvoPyramid Node: GLOBAL NEXUS
Layer: α_Pyramid_Core | Sector: SPINE
Z-Level: 17

Z17 — apex orchestration gateway.
Loads ApexCore registry, fires PEAR pulse, reports full system status.
"""

import json
import sys
from pathlib import Path
import asyncio

# ── Root resolution ───────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parents[3]  # alpha_pyramid_core/SPINE/_17_GLOBAL_NEXUS/index.py
sys.path.insert(0, str(ROOT_DIR / "alpha_pyramid_core"))
sys.path.insert(0, str(ROOT_DIR))


class NexusBridge:
    """Command gateway for external AI adapters (GCP / Replicate)."""

    async def execute(self, task: str) -> str:
        print(f"[NEXUS] Routing task: {task}")
        return "[OK] Action Manifested"


def main():
    # Import ApexCore lazily to keep node self-contained
    try:
        from apex_core import ApexCore  # type: ignore
        apex = ApexCore()
        apex.print_report()
        pulse = apex.initiate_pear_pulse("Z17 NEXUS startup")
        print(f"[NEXUS] Pulse → {pulse['pulse_id']}")
    except Exception as exc:
        print(f"[NEXUS] ApexCore unavailable ({exc}). Standalone mode.")

    print("[NEXUS] Global Nexus active at Z17.")


async def _async_main():
    bridge = NexusBridge()
    result = await bridge.execute("Sync State")
    print(result)


if __name__ == "__main__":
    main()
    asyncio.run(_async_main())
