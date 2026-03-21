import sys
import asyncio
import json
import logging
from pathlib import Path

# ─────────────────────────────────────────
#  Environment Setup
# ─────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

# Ensure sub-modules are discoverable
from alpha_pyramid_core.B_Structure.models import PyramidState, Node
from beta_pyramid_functional.B1_Kernel.SK_Engine import CortexMemory, QuantumBlock, MemoryColor, write_atomic

STATE_FILE = ROOT_DIR / "state" / "pyramid_state.json"

async def run_semantic_linker():
    print("Starting Semantic Linker (SK Engine)...")
    
    # 1. Load State
    if not STATE_FILE.exists():
        print(f"State file not found at {STATE_FILE}")
        return
    
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            state = PyramidState(**data)
        print(f"Loaded {len(state.nodes)} nodes from state.")
    except Exception as e:
        print(f"Failed to load state: {e}")
        return

    # 2. Initialize SK Memory
    sk = CortexMemory()
    
    sector_colors = {
        "SPINE": MemoryColor.BLUE,
        "GOLD": MemoryColor.YELLOW,
        "RED": MemoryColor.RED,
        "GREEN": MemoryColor.GREEN,
        "PURPLE": MemoryColor.VIOLET
    }

    # 3. Index all nodes
    print("Indexing nodes into Associative Memory...")
    for node_id, node in state.nodes.items():
        m_color = sector_colors.get(node.sector.upper(), MemoryColor.WHITE)
        block = QuantumBlock(
            id=node_id,
            content=f"{node.title} {node.summary} {node.sector} {node.layer_type}",
            color=m_color
        )
        await sk.add_block(block, persist=False)

    # 4. Semantic Linking Phase
    print("Discovering semantic relationships...")
    link_count = 0
    for node_id, node in state.nodes.items():
        # Search for similar nodes
        query_text = f"{node.title} {node.summary}"
        
        # Lower threshold for architectural mapping
        similar_blocks = await sk.find_similar(query_text, threshold=0.1)
        
        # Filter: exclude self and already linked
        existing_links = set(node.links or [])
        semantic_targets = [b.id for b in similar_blocks if b.id != node_id and b.id not in existing_links]
        
        # Pick top 2 semantic links to avoid clutter
        top_semantic = semantic_targets[:2]
        
        if top_semantic:
            node.links.extend(top_semantic)
            link_count += len(top_semantic)

    # 5. Save State
    print(f"Created {link_count} new semantic links.")
    try:
        write_atomic(STATE_FILE, state.model_dump())
        print("State updated atomically.")
        print("\n[SUCCESS] Semantic Resonance achieved.")
    except Exception as e:
        print(f"Failed to save state: {e}")

if __name__ == "__main__":
    asyncio.run(run_semantic_linker())
