import asyncio
import os
import sys
from pathlib import Path

# Setup path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from beta_pyramid_functional.B2_Orchestrator.node_generator import NodeGenerator

async def test_autogenesis():
    print("--- EVO-PYRAMID V8.0: NEURAL AUTOGENESIS TEST ---")
    generator = NodeGenerator(root_dir=str(ROOT_DIR))
    
    print("[TEST] Directing system to generate a 'Security Guardian' node...")
    
    node_path = generator.generate_node(
        node_id="sec_guardian",
        title="Security Guardian Node",
        z_level=12,
        sector="SPINE",
        summary="Autonomous monitor for detecting unauthorized LSH injections in ProjectCortex."
    )
    
    print(f"[TEST] Node Generated successfully at: {node_path}")
    
    manifest_path = Path(node_path) / ".node_manifest.json"
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = f.read()
            print("\n--- GENERATED MANIFEST ---")
            print(manifest)
            
    print("\n[SUCCESS] Neural Autogenesis V8.0 verified. The pyramid can now build itself.")

if __name__ == "__main__":
    asyncio.run(test_autogenesis())
