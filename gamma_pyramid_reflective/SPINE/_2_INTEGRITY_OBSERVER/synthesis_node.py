import json
import os
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Set
from datetime import datetime

# Canonical imports
from beta_pyramid_functional.B1_Kernel.SK_Engine.engine import ProjectCortex, HyperNode, QuantumBlock, MemoryColor
from gamma_pyramid_reflective.A_Pulse.timeline_manager import TimelineManager

class SynthesisNode:
    """
    Z2-Level Reflective Agent.
    Synthesizes failures and repairs into Architectural Proposals.
    """
    _PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
    _PROPOSALS_FILE = _PROJECT_ROOT / "gamma_pyramid_reflective" / "D_Audit" / "evolution_proposals.md"
    _REPAIRS_FILE = _PROJECT_ROOT / "gamma_pyramid_reflective" / "B_Evo_Log" / "repairs.json"

    def __init__(self, cortex: ProjectCortex):
        self.cortex = cortex

    async def run_synthesis(self):
        """Main synthesis loop: Analyze -> Cluster -> Propose."""
        print("[SYNTHESIS_NODE] Starting evolutionary synthesis cycle...")
        
        # 1. Gather raw data from Radar (Timeline) and Surgery (Repairs)
        timeline_events = TimelineManager.get_recent_history(limit=500)
        repairs = self._load_repairs()
        
        if not timeline_events and not repairs:
            print("[SYNTHESIS_NODE] No data to synthesize. Skipping cycle.")
            return

        # 2. Index logs in ProjectCortex for semantic analysis
        await self._index_logs(timeline_events, repairs)
        
        # 3. Find Semantic Clusters of failures
        clusters = await self.cortex.hypergraph.get_clusters(min_similarity=0.4)
        
        # 4. Generate Proposals for significant clusters
        for cluster in clusters:
            if len(cluster) >= 3:  # Pattern threshold
                await self._generate_proposal(cluster)

    async def _index_logs(self, events: List[Dict], repairs: List[Dict]):
        """Converts logs into Quantum Blocks for clustering."""
        for i, event in enumerate(events):
            content = f"Event: {event.get('act')} at {event.get('loc')} for {event.get('mod')}. Status: {event.get('st')}"
            block = QuantumBlock(id=f"TL_{i}_{datetime.now().timestamp()}", hyper_id=None, base_color=MemoryColor.BLUE, content=content)
            node = HyperNode(id=block.id, block_id=block.id, color=MemoryColor.BLUE)
            await self.cortex.hypergraph.add_node(node, block)
            
        for i, repair in enumerate(repairs):
            content = f"Repair: {repair.get('module')} fixed error '{repair.get('error')}'. Method: {repair.get('strategy')}"
            block = QuantumBlock(id=f"RP_{i}_{datetime.now().timestamp()}", hyper_id=None, base_color=MemoryColor.GREEN, content=content)
            node = HyperNode(id=block.id, block_id=block.id, color=MemoryColor.GREEN)
            await self.cortex.hypergraph.add_node(node, block)

    async def _generate_proposal(self, cluster_ids: Set[str]):
        """Creates a formal Evolutionary Proposal in markdown."""
        cluster_nodes = [await self.cortex.hypergraph.get_node(nid, load_content=True) for nid in cluster_ids]
        cluster_contents = [n.metadata.get('content_preview', '') for n in cluster_nodes if n]
        
        proposal_id = f"EP-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        proposal_md = f"""
### [NEW] Proposal {proposal_id}
**Cluster Size**: {len(cluster_ids)}
**Detected Pattern**: 
- {cluster_contents[0]}
- {cluster_contents[1]} (and {len(cluster_contents)-2} more similar events)

**Architectural Insight**:
The system has detected a recurring failure/repair cycle. This indicates a structural bottleneck or a policy mismatch.

**Suggested Amendment**:
> [!TIP]
> Synthesized Suggestion: Review the Z-Cascade constraints for the affected sector. Consider creating a dedicated Solution for this recurring task pattern.

---
"""
        try:
            os.makedirs(self._PROPOSALS_FILE.parent, exist_ok=True)
            with open(self._PROPOSALS_FILE, "a", encoding="utf-8") as f:
                f.write(proposal_md)
            print(f"[SYNTHESIS_NODE] Generated new Evolutionary Proposal: {proposal_id}")
        except Exception as e:
            print(f"[SYNTHESIS_NODE] Failed to write proposal: {e}")

    def _load_repairs(self) -> List[Dict]:
        if not self._REPAIRS_FILE.exists():
            return []
        try:
            with open(self._REPAIRS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
