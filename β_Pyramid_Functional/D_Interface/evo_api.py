import json
import logging
import os
import sys
import re
import asyncio
from typing import Any, List, Dict, Optional, Tuple, cast
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ─────────────────────────────────────────
#  Environment Setup
# ─────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

# Discovery of pyramid layers
core_layer = None
functional_layer = None
reflective_layer = None

try:
    for d in ROOT_DIR.iterdir():
        if not d.is_dir(): continue
        name = d.name.lower()
        if "pyramid_core" in name: core_layer = d
        elif "pyramid_functional" in name: functional_layer = d
        elif "pyramid_reflective" in name: reflective_layer = d
except Exception as e:
    logging.warning(f"Iterdir failed, falling back to positional: {e}")

# Fallback to hardcoded names if iterdir fails to find by substring
if core_layer is None: core_layer = ROOT_DIR / "α_Pyramid_Core"
if functional_layer is None: functional_layer = ROOT_DIR / "β_Pyramid_Functional"
if reflective_layer is None: reflective_layer = ROOT_DIR / "γ_Pyramid_Reflective"

# Absolute validation
if not core_layer.exists() or not functional_layer.exists() or not reflective_layer.exists():
    # Final attempt: direct strings
    core_layer = ROOT_DIR / "\u03b1_Pyramid_Core"
    functional_layer = ROOT_DIR / "\u03b2_Pyramid_Functional"
    reflective_layer = ROOT_DIR / "\u03b3_Pyramid_Reflective"

if not core_layer.exists():
    raise RuntimeError(f"Critical error: Core layer NOT found at {core_layer}")

# Inject critical paths into sys.path
sys.path.insert(0, str(core_layer / "B_Structure"))
sys.path.insert(0, str(functional_layer / "D_Interface"))
sys.path.insert(0, str(functional_layer / "B2_Orchestrator"))
sys.path.insert(0, str(reflective_layer / "A_Pulse"))

try:
    from models import Node, Link, PyramidState, NodeState, NodeKind, LayerType, OrchestratorState
    from manifestor import PhysicalManifestor
    from pulser import PulserEngine
except ImportError as e:
    # Diagnostic print
    print(f"DEBUG: sys.path = {sys.path}")
    raise RuntimeError(f"Critical dependency import failed: {e}")

# ─────────────────────────────────────────
#  Logging & State
# ─────────────────────────────────────────
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_DIR / "core_engine.log"), logging.StreamHandler()]
)

STATE_DIR = ROOT_DIR / "state"
STATE_FILE = STATE_DIR / "pyramid_state.json"

def load_state() -> PyramidState:
    try:
        if STATE_FILE.exists():
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return PyramidState(**data)
    except Exception as e:
        logging.error(f"State load error: {e}")
    return PyramidState()

def save_state(state: PyramidState):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w", encoding='utf-8') as f:
        f.write(state.model_dump_json())

current_state = load_state()

# ─────────────────────────────────────────
#  Communication Manager
# ─────────────────────────────────────────
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        dead = []
        for c in self.active_connections:
            try:
                await c.send_json(message)
            except Exception:
                dead.append(c)
        for c in dead:
            self.disconnect(c)

manager = ConnectionManager()

# ─────────────────────────────────────────
#  Lifespan & Background Tasks
# ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize background engine
    pulser = PulserEngine(current_state, manager, save_state)
    await pulser.start()
    
    # Initialize Z-Bus
    zbus_task = None
    try:
        from zbus import zbus
        zbus_task = asyncio.create_task(zbus.run_worker(manager, current_state))
    except ImportError:
        logging.warning("Z-Bus module not found. Orchestrator communication offline.")

    yield
    
    # Shutdown
    await pulser.stop()
    if zbus_task:
        zbus_task.cancel()
        try:
            await zbus_task
        except asyncio.CancelledError:
            pass

app = FastAPI(title="EvoPyramid OS Core Engine", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────
#  Discovery Utilities
# ─────────────────────────────────────────
SCAN_SECTORS = {"SPINE", "PURPLE", "RED", "GOLD", "GREEN"}
VALID_LAYER_TYPES = {"alpha", "beta", "gamma"}

def _safe_slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", str(value or "").strip()).strip("_")
    return slug.lower()

def _safe_int(value: Any, default: int) -> int:
    try: return int(value)
    except: return default

def _load_manifest(manifest_path: Path) -> Dict[str, Any]:
    try:
        if manifest_path.exists():
            with open(manifest_path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
    except: pass
    return {}

def _node_from_structure_dir(layer_dir: Path, sector_dir: Path, node_dir: Path) -> Optional[Node]:
    if not node_dir.is_dir() or node_dir.name.startswith("__"): return None
    sector = sector_dir.name.upper()
    if sector not in SCAN_SECTORS: return None

    manifest = _load_manifest(node_dir / ".node_manifest.json")
    parsed = re.match(r"^(?P<z>\d+)_([A-Za-z0-9_-]+)$", node_dir.name)
    parsed_z = _safe_int(parsed.group("z"), 9) if parsed else 9
    parsed_name = parsed.group(2) if parsed else node_dir.name

    node_id = _safe_slug(manifest.get("id") or parsed_name)
    if not node_id: return None

    z_level = _safe_int(manifest.get("z_level") or manifest.get("coords", {}).get("z"), parsed_z)
    
    return Node(
        id=node_id,
        title=str(manifest.get("title") or parsed_name.replace("_", " ")).strip() or node_id,
        z_level=z_level,
        sector=sector,
        coords={
            "x": _safe_int(manifest.get("coords", {}).get("x"), 9),
            "y": _safe_int(manifest.get("coords", {}).get("y"), 9),
            "z": _safe_int(manifest.get("coords", {}).get("z"), z_level),
        },
        layer_type=str(manifest.get("layer_type") or "beta").lower(),
        kind=str(manifest.get("kind") or "module").lower(),
        summary=str(manifest.get("summary") or f"Discovered: {sector}/{node_dir.name}"),
        state=str(manifest.get("state") or NodeState.ACTIVE.value),
        links=[str(l) for l in manifest.get("links", []) if str(l).strip()],
        metadata={
            "source": "filesystem-discovery",
            "path": str(node_dir.relative_to(ROOT_DIR)).replace("\\", "/"),
            "layer_folder": layer_dir.name,
        }
    )

def discover_structure_nodes() -> Tuple[List[Node], Dict[str, int]]:
    layers = [d for d in ROOT_DIR.glob("*_Pyramid_*") if d.is_dir()]
    discovered: Dict[str, Node] = {}
    scanned_dirs: int = 0

    for layer in layers:
        for sector_dir in layer.iterdir():
            if not sector_dir.is_dir() or sector_dir.name.upper() not in SCAN_SECTORS: continue
            for node_dir in sector_dir.iterdir():
                if not node_dir.is_dir(): continue
                scanned_dirs += 1
                node = _node_from_structure_dir(layer, sector_dir, node_dir)
                if node and (node.id not in discovered or node.z_level > discovered[node.id].z_level):
                    discovered[node.id] = node

    return list(discovered.values()), {"layers": len(layers), "scanned_dirs": scanned_dirs, "discovered": len(discovered)}

# ─────────────────────────────────────────
#  API Routes
# ─────────────────────────────────────────
@app.get("/state")
async def get_state():
    return current_state

@app.get("/health/audit")
async def health_audit():
    try:
        from reality_monitor_z3 import RealityMonitor
        return RealityMonitor().check_integrity()
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@app.post("/sync/discover-modules")
async def sync_modules(update_existing: bool = False):
    nodes, stats = discover_structure_nodes()
    added: int = 0
    updated: int = 0
    for node in nodes:
        if node.id not in current_state.nodes:
            current_state.nodes[node.id] = node
            added += 1
        elif update_existing:
            current_state.nodes[node.id] = node
            updated += 1
    
    if added or updated:
        save_state(current_state)
        await manager.broadcast({"type": "full_state", "data": current_state.model_dump()})
    
    return {"status": "ok", "added": added, "updated": updated, **stats}

@app.post("/canon/guard/apply")
async def guard_apply(update_existing: bool = True, prune_missing: bool = False):
    sync_result = await sync_modules(update_existing=update_existing)
    removed_count: int = 0
    if prune_missing:
        # Pruning logic: if node is in state but not on disk
        discovered_nodes, _ = discover_structure_nodes()
        discovered_ids = {n.id for n in discovered_nodes}
        for node_id in list(current_state.nodes.keys()):
            if node_id not in discovered_ids:
                del current_state.nodes[node_id]
                removed_count += 1
        if removed_count:
            save_state(current_state)
            await manager.broadcast({"type": "full_state", "data": current_state.model_dump()})
            
    return {"status": "ok", "sync": sync_result, "removed": removed_count}

@app.post("/node/{node_id}/run")
async def run_node(node_id: str):
    return PhysicalManifestor.autorun_node(node_id, current_state)

@app.post("/node")
async def add_update_node(node: Node):
    current_state.nodes[node.id] = node
    save_state(current_state)
    try:
        path = PhysicalManifestor.manifest_node(node)
        await manager.broadcast({"type": "node_update", "data": node.model_dump(), "manifest_path": path})
        return {"status": "ok", "path": path}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.post("/link")
async def add_link(link: Link):
    current_state.links.append(link)
    save_state(current_state)
    await manager.broadcast({"type": "link_added", "data": link.model_dump()})
    return {"status": "ok"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    await websocket.send_json({"type": "full_state", "data": current_state.model_dump()})
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "LLM_RESPONSE":
                    node_id = msg.get("node_id")
                    if node_id in current_state.nodes:
                        current_state.nodes[node_id].orchestrator_state = "ready"
                        await manager.broadcast({"type": "node_update", "data": current_state.nodes[node_id].model_dump()})
            except: pass
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



















