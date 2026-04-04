import sys
import json
from pathlib import Path
from datetime import datetime, timezone
import logging

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT / "beta_pyramid_functional" / "B1_Kernel") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "beta_pyramid_functional" / "B1_Kernel"))

from beta_pyramid_functional.B1_Kernel.contracts import TaskEnvelope
from beta_pyramid_functional.B1_Kernel.z_cascade import ZCascadePipeline

# Trinity Resonance Imports
try:
    if str(PROJECT_ROOT / "alpha_pyramid_core" / "SPINE" / "17_GLOBAL_NEXUS") not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT / "alpha_pyramid_core" / "SPINE" / "17_GLOBAL_NEXUS"))
    from trinity_resonance.engine import FormalResonanceEngine
    from trinity_resonance.models import TriangleColor
except ImportError:
    FormalResonanceEngine = None
    TriangleColor = None

try:
    from alpha_pyramid_core.SPINE.12_SEC_GUARDIAN.sec_guardian import SignatureVerifier
except ImportError:
    SignatureVerifier = None

logger = logging.getLogger("GLOBAL_NEXUS")

class Z17GlobalNexus:
    """
    The absolute peak of the Z-Architecture.
    Reads global intent and translates it into a Z-Cascade TaskEnvelope.
    Now utilizes TRINITY RESONANCE v3.0 to validate intent coherence.
    """
    
    RESONANCE = FormalResonanceEngine(admin_name="Админ Алекс") if FormalResonanceEngine else None
    PROPOSALS_PATH = PROJECT_ROOT / "gamma_pyramid_reflective" / "D_Audit" / "evolution_proposals.md"
    STATE_FILE = PROJECT_ROOT / "state" / "pyramid_state.json"

    # ── Registry (merged from apex_core.py) ───────────────────────────────────

    @classmethod
    def load_registry(cls) -> dict:
        """Load pyramid_state.json node registry."""
        try:
            with open(cls.STATE_FILE, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
            return raw.get("nodes", {})
        except FileNotFoundError:
            logger.warning("[Z17] State file not found. Starting empty.")
            return {}
        except json.JSONDecodeError as exc:
            logger.error(f"[Z17] Failed to parse state file: {exc}")
            return {}

    @classmethod
    def status_report(cls) -> dict:
        """Structured health summary of the full node registry."""
        nodes = cls.load_registry()
        counts: dict = {}
        for node in nodes.values():
            s = str(node.get("state", "unknown"))
            counts[s] = counts.get(s, 0) + 1
        return {
            "z_level": 17,
            "sector": "SPINE",
            "total_nodes": len(nodes),
            "state_counts": counts,
            "alpha_nodes": sum(1 for n in nodes.values() if n.get("layer_type") == "alpha"),
            "beta_nodes": sum(1 for n in nodes.values() if n.get("layer_type") == "beta"),
            "gamma_nodes": sum(1 for n in nodes.values() if n.get("layer_type") == "gamma"),
        }

    @classmethod
    def initiate_pear_pulse(cls, intent: str = "System coherence check") -> dict:
        """Fire the primary PEAR pulse from Z17 apex."""
        import time
        nodes = cls.load_registry()
        pulse = {
            "pulse_id": f"z17_apex_{int(time.time())}",
            "origin": "Z17_GLOBAL_NEXUS",
            "intent": intent,
            "fired_at": time.time(),
            "node_snapshot": {
                "total": len(nodes),
                "active": sum(1 for n in nodes.values() if n.get("state") == "active"),
                "error": sum(1 for n in nodes.values() if n.get("state") == "error"),
            },
        }
        logger.info(f"[Z17] PEAR pulse fired → intent='{intent}' | nodes={pulse['node_snapshot']}")
        return pulse


    @classmethod
    def perform_structural_audit(cls) -> bool:
        """Validates that all nodes in architecture_map.json respect the (18-Z) block rule."""
        map_path = PROJECT_ROOT / "architecture" / "architecture_map.json"
        if not map_path.exists():
            logger.error("[Z17_AUDIT] architecture_map.json missing!")
            return False
            
        with open(map_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        modules = data.get("modules", {})
        errors = []
        CENTER = 9
        
        for name, meta in modules.items():
            z = meta.get("z", 1)
            x, y = meta.get("x", 9), meta.get("y", 9)
            size = 18 - z
            start = CENTER - (size // 2)
            end = start + size - 1
            
            if not (start <= x <= end and start <= y <= end):
                errors.append(f"Node {name} at Z{z} is out of bounds (x:{x}, y:{y}). Expected range [{start}-{end}].")
        
        if errors:
            for err in errors:
                logger.warning(f"[Z17_AUDIT] {err}")
            return False
            
        logger.info(f"[Z17_AUDIT] Structural integrity verified for {len(modules)} nodes.")
        return True

    @classmethod
    def read_latest_intent(cls) -> str:
        if not cls.PROPOSALS_PATH.exists():
            return "No master intent found."
        with open(cls.PROPOSALS_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
            
        import re
        matches = re.findall(r"## \[(.*?)\](.*?)(?=\n## |$)", content, re.DOTALL)
        if matches:
            latest = matches[-1]
            return f"[{latest[0]}] {latest[1].strip()}"
        return "Synchronize base components."

    @classmethod
    def initialize_evolution_cascade(cls):
        # 1. Mandatory Structural Audit from Z17
        if not cls.perform_structural_audit():
            logger.error("[Z17_GLOBAL_NEXUS] Structural Audit Failed. Cascade aborted.")
            return {"status": "aborted", "reason": "Structural Integrity Breach"}

        intent = cls.read_latest_intent()
        
        # 2. Trinity Resonance Core v3.0 Check (BLACK CORE)
        resonance_result = {"coherence": 1.0, "state": "DORMANT"}
        if cls.RESONANCE:
            import asyncio
            # Use sync wrapper for the async process if needed, or assume loop is running
            # In a real environment, we'd use 'await', but nexus_core is currently a script.
            # We'll use a simplified version:
            try:
                loop = asyncio.get_event_loop()
                res = loop.run_until_complete(cls.RESONANCE.process(intent, "BLACK"))
                resonance_result = res
                if res.get("status") == "blocked":
                    logger.error(f"[Z17_RESONANCE] Intent Coherence Critical! Blocked: {res.get('violations')}")
                    return {"status": "blocked", "reason": "Low Coherence", "violations": res.get("violations")}
                
                logger.info(f"[Z17_RESONANCE] Coherence Verified: {res.get('coherence')}")
            except Exception as e:
                logger.warning(f"[Z17_RESONANCE] Check failed: {e}")

        logger.info(f"[Z17_GLOBAL_NEXUS] Firing Genesis Cascade. Intent: {intent}")
        
        task_id = f"genesis_cascade_{int(datetime.now().timestamp())}"
        sig = SignatureVerifier.generate_signature("Z17_GLOBAL_NEXUS", task_id) if SignatureVerifier else f"TSIG:Z17_GLOBAL_NEXUS:{task_id}"

        envelope = TaskEnvelope(
            task_id=task_id,
            source_node="Z17_GLOBAL_NEXUS",
            target_node="system",
            action="manifest_node",
            origin_z=17,
            signature=sig,
            intent=f"Z17 Master Intent: {intent[:100]}...",
            coherence_score=resonance_result.get("coherence", 1.0),
            trinity_state=resonance_result.get("state", "EMITTING"),
            payload={
                "z_level": 1,
                "synthesis_proposal": "Full project structural synchronization.",
                "target_z": 1
            }
        )
        
        # 3. Dispatch through the Z-Cascade Pipeline
        report = ZCascadePipeline.run_z17_to_z1(envelope)
        
        status = report.get("status")
        logger.info(f"[Z17_GLOBAL_NEXUS] Cascade Finished. Status: {status}")
        return report

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    report = Z17GlobalNexus.initialize_evolution_cascade()
    print(json.dumps(report, indent=2))
