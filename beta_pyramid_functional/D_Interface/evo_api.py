# ─────────────────────────────────────────
#  Kernel Spine Discovery
# ─────────────────────────────────────────
import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parents[2]

# Bootstrap kernel path
kernel_path = str(ROOT_DIR / "beta_pyramid_functional" / "B1_Kernel")
if kernel_path not in sys.path:
    sys.path.insert(0, kernel_path)

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from path_discovery import initialize_kernel_paths
    initialize_kernel_paths()
except ImportError as e:
    import logging
    logging.error(f"Kernel path discovery failed: {e}")
    sys.exit(1)

# Now it is safe to import from layers
import json
import logging
import os
import re
import asyncio
import uuid
from datetime import datetime, timezone
from typing import Any, List, Dict, Optional, Tuple, cast
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from alpha_pyramid_core.B_Structure.models import PyramidState, Node, Link, NodeState, NodeKind, LayerType, OrchestratorState
from beta_pyramid_functional.B1_Kernel.ws_manager import ConnectionManager
from beta_pyramid_functional.B1_Kernel.contracts import TaskEnvelope, TaskStatus
from beta_pyramid_functional.B1_Kernel.SK_Engine import CortexMemory, QuantumBlock, write_atomic, MemoryColor
from beta_pyramid_functional.B1_Kernel.contracts import TaskEnvelope, TaskStatus
from beta_pyramid_functional.B1_Kernel.policy_manager import SystemPolicyManager

try:
    from beta_pyramid_functional.B2_Orchestrator.manifestor import PhysicalManifestor
    from gamma_pyramid_reflective.A_Pulse.pulser import PulserEngine
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
    handlers=[logging.FileHandler(LOG_DIR / "core_engine.log", encoding="utf-8"), logging.StreamHandler()]
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

EVOLUTION_JOURNAL_PATH = Path(__file__).parent / "evolution_journal.json"

def _log_to_journal(envelope: TaskEnvelope, status: str, result: Any):
    try:
        if not EVOLUTION_JOURNAL_PATH.exists():
            data = {"protocol": "Trinity-Soft-Lang", "version": "1.0", "journal": []}
        else:
            data = json.loads(EVOLUTION_JOURNAL_PATH.read_text(encoding="utf-8"))
        
        entry = {
            "task_id": envelope.task_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": envelope.source_node,
            "origin_z": envelope.origin_z,
            "action": envelope.action,
            "result_summary": str(result)[:500], # Keep it brief
            "status": status
        }
        data["journal"].append(entry)
        EVOLUTION_JOURNAL_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception as e:
        logging.error(f"Journal logging failed: {e}")

def save_state(state: PyramidState):
    """Atomic state persistence using SK Engine utility."""
    try:
        write_atomic(STATE_FILE, state.model_dump())
    except Exception as e:
        logging.error(f"CRITICAL: Failed to save state: {e}")

current_state = load_state()

# ─────────────────────────────────────────
#  Communication Manager
# ─────────────────────────────────────────
manager = ConnectionManager()
sk_memory = CortexMemory()

# ─────────────────────────────────────────
#  Lifespan & Background Tasks
# ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SK Memory from current state for associative search
    logging.info("Initializing SK Memory from current state...")
    for node_id, node in current_state.nodes.items():
        # Sector-to-Color Logic Mapping
        sector_colors = {
            "SPINE": MemoryColor.BLUE,
            "GOLD": MemoryColor.YELLOW,
            "RED": MemoryColor.RED,
            "GREEN": MemoryColor.GREEN,
            "PURPLE": MemoryColor.VIOLET
        }
        m_color = sector_colors.get(node.sector, MemoryColor.WHITE)
        
        block = QuantumBlock(
            id=node_id,
            content=f"{node.title} {node.summary}",
            base_color=m_color,
            metadata={"path": node.metadata.get("path")}
        )
        await sk_memory.add_block(block, persist=False)
        
        # Sync back to current_state for UI
        node.memory_color = m_color.value
        node.gravity = block.gravity

    logging.info(f"SK Memory initialized with {len(sk_memory.blocks)} nodes.")

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

    # System Metrics Background Poller
    async def metrics_poller():
        try:
            from beta_pyramid_functional.B4_Cognitive.cognitive_bridge import CognitiveBridge
            bridge = await CognitiveBridge.get_instance()
        except ImportError:
            bridge = None
            logging.warning("CognitiveBridge not found. Memory metrics offline.")

        pulse_path = ROOT_DIR / "state" / "project_cortex" / "pulse.json"

        while True:
            try:
                metrics = {}
                # Health from ObserverRelay pulse
                if pulse_path.exists():
                    try:
                        with open(pulse_path, "r", encoding="utf-8") as f:
                            pulse_data = json.load(f)
                            metrics["health_pct"] = pulse_data.get("health_pct", 0.0)
                            metrics["health_status"] = pulse_data.get("status", "unknown")
                    except Exception:
                        pass
                else:
                    metrics["health_pct"] = 0.0
                    metrics["health_status"] = "offline"

                # Memory from CognitiveBridge
                if bridge:
                     try:
                         mem_stats = await bridge.health_summary()
                         metrics["memory_total"] = mem_stats.get("total_blocks", 0)
                         metrics["memory_session"] = mem_stats.get("session_memory_blocks", 0)
                     except Exception:
                         pass

                if metrics:
                    current_state.system_metrics = metrics
                    # Full state broadcast is handled by other events (like pulser) periodically, 
                    # but we could also broadcast a lightweight metrics update if needed.
            except Exception as e:
                logging.error(f"Metrics poller error: {e}")
            
            await asyncio.sleep(5)  # Poll every 5 seconds

    metrics_task = asyncio.create_task(metrics_poller())

    yield
    
    # Shutdown
    metrics_task.cancel()
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
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173", 
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────
#  Mount Session Registry Router
# ─────────────────────────────────────────
try:
    from beta_pyramid_functional.B3_SessionRegistry.session_api import router as session_router
    app.include_router(session_router)
    logging.info("Mounted Evo API v1 Session Router (/v1/sessions, /v1/providers)")
except ImportError as e:
    logging.warning(f"Could not load session router: {e}")



# ─────────────────────────────────────────
#  Discovery Utilities
# ─────────────────────────────────────────
SCAN_SECTORS = {"SPINE", "PURPLE", "RED", "GOLD", "GREEN", "SANDBOX"}
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
    layers = [d for d in ROOT_DIR.glob("*pyramid*") if d.is_dir()]
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
@app.get("/search/similarity")
async def search_similarity(q: str, threshold: float = 0.1):
    """Associative search for related nodes in the pyramid."""
    results = await sk_memory.find_similar(q, threshold)
    return [
        {
            "id": b.id,
            "title": current_state.nodes[b.id].title if b.id in current_state.nodes else b.id,
            "similarity": sk_memory._jaccard_similarity(sk_memory.minhash.create_signature(q), b.minhash)
        } 
        for b in results
    ]

@app.get("/state", response_model=PyramidState)
async def get_state():
    return current_state

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "layer": "alpha",
        "z_level": 17,
        "sector": "SPINE",
        "module": "core_engine",
        "nodes_total": len(current_state.nodes)
    }

@app.get("/health/audit")
async def health_audit():
    try:
        from reality_monitor_z3 import RealityMonitor
        return RealityMonitor().check_integrity()
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@app.get("/health/seven")
async def health_seven():
    try:
        from reality_monitor_z3 import RealityMonitor
        return RealityMonitor.perform_seven_audit()
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

@app.get("/health/kernel")
async def health_kernel():
    """
    Returns the status of the Spine-Kernel and active security policies.
    """
    try:
        from policy_manager import SystemPolicyManager
        policy_mgr = SystemPolicyManager()
        return {
            "status": "ONLINE",
            "spine_version": "2.0.0-crystallization",
            "policy": policy_mgr.policy.model_dump(),
            "audit_violations": len(policy_mgr.audit_log),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        return {"status": "ERROR", "message": f"Kernel link failed: {e}"}

@app.post("/kernel/dispatch")
async def kernel_dispatch(envelope: TaskEnvelope):
    """
    Mandatory dispatch gate for all autonomous tasks.
    Enforces security policies defined in the Kernel.
    """
    try:
        from policy_manager import SystemPolicyManager
        policy_mgr = SystemPolicyManager()
        
        if not policy_mgr.validate_action(envelope):
            return {
                "status": "REJECTED",
                "task_id": envelope.task_id,
                "reason": envelope.metadata.get("error", "Policy violation")
            }
            
        # Action Execution Logic
        result = {}
        if envelope.action == "manifest_node":
            from models import Node
            node_data = envelope.payload
            node = Node(**node_data)
            current_state.nodes[node.id] = node
            save_state(current_state)
            path = PhysicalManifestor.manifest_node(node)
            await manager.broadcast({"type": "node_update", "data": node.model_dump(), "manifest_path": path})
            result = {"path": path}
            
        elif envelope.action == "sync_structure":
            update_existing = envelope.payload.get("update_existing", False)
            sync_res = await sync_modules(update_existing=update_existing)
            result = sync_res
            
        elif envelope.action == "apply_canon_guard":
            update_existing = envelope.payload.get("update_existing", True)
            prune_missing = envelope.payload.get("prune_missing", False)
            guard_res = await guard_apply(update_existing=update_existing, prune_missing=prune_missing)
            result = guard_res
        
        # Log to Evolution Journal
        _log_to_journal(envelope, status="ACCEPTED", result=result)

        return {
            "status": "ACCEPTED",
            "task_id": envelope.task_id,
            "orchestrator": "Spine-V2-Hardened",
            "result": result
        }
    except Exception as e:
        return {"status": "ERROR", "message": f"Dispatch failure: {e}"}

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

class NodeStatusPatch(BaseModel):
    status: str  # NodeState value: active | idle | degraded | quarantined | failed
    runtime_canon_flag: Optional[str] = None  # canon | runtime | None (no change)

@app.patch("/nodes/{node_id}/status")
async def patch_node_status(node_id: str, patch: NodeStatusPatch):
    """
    Update node state and optionally runtime_canon_flag.
    Used by Observer Banner: Confirm Route / Quarantine Z7 actions.
    Broadcasts node_update over WebSocket to all connected clients.
    """
    if node_id not in current_state.nodes:
        return {"status": "error", "detail": f"Node '{node_id}' not found"}
    
    node = current_state.nodes[node_id]
    
    # Validate status value
    valid_states = {s.value for s in NodeState}
    if patch.status not in valid_states:
        return {"status": "error", "detail": f"Invalid status '{patch.status}'. Valid: {sorted(valid_states)}"}
    
    node.state = patch.status
    if patch.runtime_canon_flag is not None:
        node.runtime_canon_flag = patch.runtime_canon_flag
    
    current_state.nodes[node_id] = node
    save_state(current_state)
    await manager.broadcast({"type": "node_update", "data": node.model_dump()})
    
    return {
        "status": "ok",
        "node_id": node_id,
        "new_state": node.state,
        "runtime_canon_flag": node.runtime_canon_flag
    }


@app.post("/link")
async def add_link(link: Link):
    current_state.links.append(link)
    save_state(current_state)
    await manager.broadcast({"type": "link_added", "data": link.model_dump()})
    return {"status": "ok"}

@app.post("/zbus/publish")
async def zbus_publish(event: dict):
    """
    HTTP Bridge for standalone nodes to publish events to the UI.
    Calls the internal zbus broadcast mechanism.
    """
    try:
        from zbus import zbus
        await zbus.broadcast_event(event)
        return {"status": "event_broadcasted"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

class PromptRequest(BaseModel):
    prompt: str
    session_ids: List[str]
    routing: str = "single"
    context_pack_id: Optional[str] = None

@app.post("/v1/prompt")
async def trigger_prompt(req: PromptRequest):
    """Evo API v1: Unified prompt routing dispatch."""
    import uuid
    try:
        from zbus import zbus
    except ImportError:
        return {"status": "error", "message": "Z-Bus not available"}
        
    task_id = str(uuid.uuid4())
    
    # Broadcast to requested sessions
    for sid in req.session_ids:
        try:
            from beta_pyramid_functional.B3_SessionRegistry.session_api import SessionRegistry
            session = SessionRegistry.get(sid)
            provider = session.provider if session else "unknown"
            url = session.external_url if session and hasattr(session, "external_url") else ""
            
            await zbus.dispatch_llm_task(
                task_id=task_id,
                session_id=sid,
                provider=provider,
                prompt=req.prompt,
                target_url=url or ""
            )
        except Exception as e:
            logging.error(f"Failed to dispatch prompt for session {sid}: {e}")
            
    return {
        "status": "dispatched",
        "task_id": task_id,
        "routing": req.routing,
        "sessions": req.session_ids
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Enhanced Z-Bus WebSocket Gateway."""
    await manager.connect(websocket)
    await websocket.send_json({"type": "full_state", "data": current_state.model_dump()})
    try:
        from zbus import zbus
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                
                # 1. Z-Bus Event ingestion from clients (Extension/UI)
                if "topic" in msg:
                    await zbus.publish(msg)
                    
                # 2. Legacy LLM Response handling
                elif msg.get("type") == "LLM_RESPONSE":
                    node_id = msg.get("node_id")
                    if node_id and node_id in current_state.nodes:
                        current_state.nodes[node_id].orchestrator_state = "ready"
                        await manager.broadcast({"type": "node_update", "data": current_state.nodes[node_id].model_dump()})
            except Exception as e:
                logging.error(f"WS Parse error: {e}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)



















