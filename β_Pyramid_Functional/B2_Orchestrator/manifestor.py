import json
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# We assume this is running within the EvoPyramid environment where sys.path is already set up
# or we can set it up here if needed.
import sys
from pathlib import Path
import logging

# Discovery of pyramid layers
ROOT_DIR = Path(__file__).resolve().parents[2]
core_layer = None
for d in ROOT_DIR.iterdir():
    if not d.is_dir(): continue
    if "pyramid_core" in d.name.lower():
        core_layer = d
        break

if core_layer is None:
    core_layer = ROOT_DIR / "α_Pyramid_Core"
    if not core_layer.exists():
        core_layer = ROOT_DIR / "\u03b1_Pyramid_Core"

# Inject critical paths
if core_layer and core_layer.exists():
    path_str = str(core_layer / "B_Structure")
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
else:
    raise RuntimeError(f"Core layer missing or invalid: {core_layer}. ROOT={ROOT_DIR}")

try:
    from models import Node, NodeState, NodeKind, LayerType, PyramidState
except ImportError as e:
    # Re-attempt core_layer discovery if it was not found or path was wrong
    core_layer_fallback = next(iter(ROOT_DIR.glob("*_Pyramid_Core")), None)
    if core_layer_fallback:
        if str(core_layer_fallback / "B_Structure") not in sys.path:
            sys.path.insert(0, str(core_layer_fallback / "B_Structure"))
    
    try:
        from models import Node, NodeState, NodeKind, LayerType, PyramidState
    except ImportError as e_inner:
        raise RuntimeError(f"Manifestor failed to import models: {e_inner}. ROOT_DIR={ROOT_DIR}") from e

class PhysicalManifestor:
    """
    Project Generator: Transforms visual nodes into a real folder structure.
    Architecture: projects/[PROJECT_NAME]/[LAYER]/[SECTOR]/[NODE_ID]
    """
    ROOT_DIR = Path(__file__).resolve().parents[2]
    
    @classmethod
    def _get_layers(cls):
        core = None
        func = None
        refl = None
        for d in cls.ROOT_DIR.iterdir():
            if not d.is_dir(): continue
            name = d.name.lower()
            if "pyramid_core" in name: core = d
            elif "pyramid_functional" in name: func = d
            elif "pyramid_reflective" in name: refl = d
        
        # Fallback
        if core is None: core = cls.ROOT_DIR / "α_Pyramid_Core"
        if func is None: func = cls.ROOT_DIR / "β_Pyramid_Functional"
        if refl is None: refl = cls.ROOT_DIR / "γ_Pyramid_Reflective"
        
        return core, func, refl

    @classmethod
    def manifest_node(cls, node: Node) -> str:
        try:
            # Discovery of layer folders
            core_layer, functional_layer, reflective_layer = cls._get_layers()

            if node.z_level >= 11:
                layer_folder = core_layer.name
            elif node.z_level >= 5:
                layer_folder = functional_layer.name
            else:
                layer_folder = reflective_layer.name
                
            sector = str(node.sector or "SPINE").upper()
            
            # Create path in the REAL project structure
            clean_label = "".join(x for x in node.title if x.isalnum() or x in " -_").strip().replace(" ", "_")
            node_dir = cls.ROOT_DIR / layer_folder / sector / f"{node.z_level}_{clean_label}"
            
            # Ensure folder and __init__.py exist to make it a package
            node_dir.mkdir(parents=True, exist_ok=True)
            (node_dir / "__init__.py").touch(exist_ok=True)
            
            # Create a small manifest file in the node
            manifest_path = node_dir / ".node_manifest.json"
            with open(manifest_path, "w", encoding="utf-8") as f:
                node_data = node.dict()
                node_data["layer_folder"] = layer_folder
                json.dump(node_data, f, indent=2)
                
            # Specialized Logic Injection based on EvoGenesis Architecture
            entry_point = node_dir / "index.py"
            if entry_point.exists():
                try:
                    existing_text = entry_point.read_text(encoding="utf-8", errors="ignore")
                    legacy_markers = (
                        'print(f"Core Node {node.title} active.")',
                        'print(f"Genesis Node {node.title} active.")',
                    )
                    if any(marker in existing_text for marker in legacy_markers):
                        entry_point.unlink()
                except Exception:
                    pass

            if not entry_point.exists():
                is_genesis = (node.id or "").startswith("gen-")
                content = f'"""\nEvoPyramid Node: {node.title}\nLayer: {layer_folder} | Sector: {sector}\nZ-Level: {node.z_level}\n"""\n\n'
                
                if is_genesis:
                    if "nexus" in node.id or "bridge" in node.id:
                        content += (
                            "import asyncio\n\n"
                            "class NexusBridge:\n"
                            "    \"\"\"Command gateway for external AI adapters (GCP/Replicate)\"\"\"\n"
                            "    async def execute(self, task: str):\n"
                            "        print(f'[NEXUS] Routing task: {task}')\n"
                            "        return '[OK] Action Manifested'\n\n"
                            "async def main():\n"
                            "    bridge = NexusBridge()\n"
                            "    await bridge.execute('Sync State')\n\n"
                            "if __name__ == '__main__':\n"
                            "    asyncio.run(main())\n"
                        )
                    elif "pear" in node.id:
                        content += (
                            "def pear_cycle(observation):\n"
                            "    \"\"\"PEAR: Perception, Evolution, Action, Reflection\"\"\"\n"
                            "    print(f'[PEAR] {observation} -> Analyzing Coherence...')\n"
                            "    return {'status': 'coherent', 'entropy': 0.12}\n\n"
                            "if __name__ == '__main__':\n"
                            "    result = pear_cycle('Initial state pulse')\n"
                            "    print(f'System Status: {result}')\n"
                            )
                    else:
                        content += f'def main():\n    print("Genesis Node {node.title} active.")\n\nif __name__ == "__main__":\n    main()\n'
                else:
                    content += f'def main():\n    print("Core Node {node.title} active.")\n\nif __name__ == "__main__":\n    main()\n'
                
                with open(entry_point, "w", encoding="utf-8") as f:
                    f.write(content)
                    
            return str(node_dir)
        except Exception as e:
            logging.error(f"Manifestation error: {e}")
            raise e

    @classmethod
    def _manifest_matches(cls, manifest_path: Path, node_id: str) -> bool:
        try:
            with open(manifest_path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
            return str(data.get("id", "")) == node_id
        except Exception:
            return False

    @classmethod
    def resolve_node_dir(cls, node_id: str):
        base_path = cls.ROOT_DIR

        for manifest_path in base_path.glob("**/.node_manifest.json"):
            if cls._manifest_matches(manifest_path, node_id):
                return manifest_path.parent

        legacy_dirs = list(base_path.glob(f"**/*_{node_id}"))
        if legacy_dirs:
            return legacy_dirs[0]

        if "peer" in node_id:
            alias_id = node_id.replace("peer", "pear")
            for manifest_path in base_path.glob("**/.node_manifest.json"):
                if cls._manifest_matches(manifest_path, alias_id):
                    return manifest_path.parent
            alias_dirs = list(base_path.glob(f"**/*_{alias_id}"))
            if alias_dirs:
                return alias_dirs[0]

        return None

    @staticmethod
    def autorun_node(node_id: str, current_state: PyramidState):
        """Executes the index.py for a manifested node."""
        try:
            node_dir = PhysicalManifestor.resolve_node_dir(node_id)

            if node_dir is None and node_id in current_state.nodes:
                node_dir = Path(PhysicalManifestor.manifest_node(current_state.nodes[node_id]))

            if node_dir is None and "peer" in node_id:
                alias_id = node_id.replace("peer", "pear")
                node_dir = PhysicalManifestor.resolve_node_dir(alias_id)
                if node_dir is None and alias_id in current_state.nodes:
                    node_dir = Path(PhysicalManifestor.manifest_node(current_state.nodes[alias_id]))

            if node_dir is None:
                if node_id not in current_state.nodes:
                    synthetic_node = Node(
                        id=node_id,
                        title=node_id,
                        z_level=9,
                        sector="SPINE",
                        coords={"x": 9, "y": 9, "z": 9},
                        layer_type="beta",
                        kind="service",
                        summary="Autogenerated placeholder node for autorun compatibility",
                        state=NodeState.ACTIVE,
                    )
                    current_state.nodes[node_id] = synthetic_node
                    # The caller should handle saving state if needed
                    # but we'll return the fact that it was created

                node_dir = Path(PhysicalManifestor.manifest_node(current_state.nodes[node_id]))

            index_py = node_dir / "index.py"

            if index_py.exists():
                try:
                    current_text = index_py.read_text(encoding="utf-8", errors="ignore")
                    legacy_markers = (
                        'print(f"Core Node {node.title} active.")',
                        'print(f"Genesis Node {node.title} active.")',
                    )
                    if any(marker in current_text for marker in legacy_markers) and node_id in current_state.nodes:
                        node_dir = Path(PhysicalManifestor.manifest_node(current_state.nodes[node_id]))
                        index_py = node_dir / "index.py"
                except Exception:
                    pass

            if not index_py.exists() and node_id in current_state.nodes:
                node_dir = Path(PhysicalManifestor.manifest_node(current_state.nodes[node_id]))
                index_py = node_dir / "index.py"

            if not index_py.exists():
                return {"status": "error", "message": "index.py not found"}

            result = subprocess.run(
                [sys.executable, str(index_py)],
                capture_output=True,
                text=True,
                timeout=10,
                encoding="utf-8",
            )

            output = result.stdout + result.stderr
            return {
                "status": "success" if result.returncode == 0 else "failed",
                "exit_code": result.returncode,
                "output": output,
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

class RealityAnchor:
    """
    Stabilization Engine: Monitors project entropy and coherence.
    Calculates health score based on manifestation status and file integrity.
    """
    @staticmethod
    def calculate_node_health(node_id: str) -> float:
        """Returns coherence score (1.0 = Stable, 0.0 = High Entropy)"""
        try:
            node_dir = PhysicalManifestor.resolve_node_dir(node_id)
            if node_dir is None: return 0.0 # Not manifested
            
            score = 0.5 # Default starting point for manifested
            
            # Check for core files
            if (node_dir / "index.py").exists(): score += 0.2
            if (node_dir / ".node_manifest.json").exists(): score += 0.1
            
            # Syntax validation of code
            index_path = node_dir / "index.py"
            if index_path.exists():
                with open(index_path, "r", encoding="utf-8", errors="ignore") as f:
                    try:
                        compile(f.read(), index_path, 'exec')
                        score += 0.2 # Syntactically correct
                    except SyntaxError:
                        score -= 0.3 # High entropy: broken code
            
            return min(1.0, max(0.0, score))
        except:
            return 0.0
