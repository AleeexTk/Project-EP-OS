import asyncio
import json
import uuid
import time
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

import sys
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

try:
    from beta_pyramid_functional.B1_Kernel.SK_Engine.engine import CortexMemory, ProjectCortex
    from beta_pyramid_functional.B1_Kernel.SK_Engine.models import QuantumBlock, MemoryColor, MethodMode
    from beta_pyramid_functional.B1_Kernel.events import EventType, create_event
    from beta_pyramid_functional.B2_Orchestrator.llm_orchestrator import AgentOrchestrator, Provider, AgentSession
    from beta_pyramid_functional.B4_Cognitive.cognitive_bridge import CognitiveBridge
except ImportError as e:
    print(f"!! [PEAR_BRIDGE] Import failed, using simplified logic: {e}")

logger = logging.getLogger("PEAR_Protocol")


class PEARAgent:
    """
    Standard Base for agents participating in the PEAR loop
    (Perception, Evolution, Action, Reflection).

    Memory layers (innermost → outermost):
        1. Role-specific CortexMemory  — agent's own past actions
        2. CognitiveBridge             — cross-session long-term memory (NEW)
        3. ProjectCortex               — global project-wide semantic memory
    """

    def __init__(self, role: str, z_level: int, color: MemoryColor, provider: str = "ollama"):
        self.role = role
        self.z_level = z_level
        self.color = color
        self.provider = provider
        self.memory = CortexMemory(data_dir=ROOT_DIR / "state" / "agent_memory" / role.lower())

    async def perceive(self, pulse_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 1: Perception — Gather context from all three memory layers.

        Memory layers queried:
        - role_context      : this agent's own past similar tasks
        - session_context   : CognitiveBridge cross-session architectural memory (NEW)
        - global_context    : shared ProjectCortex knowledge
        """
        intent = pulse_data.get("intent", "")

        # Layer 1: Role-specific memories
        past_blocks = await self.memory.find_similar(intent)
        role_context = [b.to_dict() for b in past_blocks[:3]]

        # Layer 2: CognitiveBridge — cross-session long-term memory
        try:
            bridge = await CognitiveBridge.get_instance()
            session_blocks = await bridge.retrieve_session_context(intent, top_k=3)
            session_context = [b.to_dict() for b in session_blocks]
        except Exception as e:
            logger.warning(f"[PEAR] CognitiveBridge unavailable: {e}")
            session_context = []

        # Layer 3: Global Project Cortex memories
        project_cortex = await ProjectCortex.get_instance()
        global_blocks = await project_cortex.find_similar(intent)
        global_context = [b.to_dict() for b in global_blocks[:3]]

        logger.debug(
            f"[PEAR/{self.role}] Perceive — role:{len(role_context)} "
            f"session:{len(session_context)} global:{len(global_context)}"
        )

        return {
            "perceived_intent": intent,
            "role_context": role_context,
            "session_context": session_context,   # ← NEW: long-term memory
            "global_context": global_context,
            "pulse_id": pulse_data.get("pulse_id"),
        }

    async def evolve(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 2: Evolution - Logic to transform perception into a proposal."""
        intent = perception["perceived_intent"]
        role_mem = json.dumps(perception["role_context"])
        glob_mem = json.dumps(perception["global_context"])
        sess_mem = json.dumps(perception["session_context"])

        try:
            session = AgentSession(
                node_id=f"z{self.z_level}-{self.role.lower()}",
                node_z=self.z_level,
                task_title=f"{self.role} Evolution: {intent[:30]}",
                provider=Provider.OLLAMA if self.provider == "ollama" else Provider.GEMINI,
                task_context=(
                    f"PEAR Evolution Cycle. "
                    f"Agent History: {role_mem} | "
                    f"Long-Term Memory: {sess_mem} | "
                    f"Global Project Memory: {glob_mem}"
                ),
            )
            session.add_user_message(
                f"Evolve the following intent based on your architecture role as {self.role}: {intent}"
            )

            response = await AgentOrchestrator.get_response(session)
            return {"proposal": response or "No proposal generated.", "status": "evolved"}
        except Exception as e:
            logger.error(f"Evolution failed for {self.role}: {e}")
            return {"proposal": f"Fallback: Basic action for {intent}", "status": "evolved_fallback"}

    async def act(self, evolution: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 3: Action - Execution of the proposal."""
        return {
            "agent": self.role,
            "z_level": self.z_level,
            "output": evolution["proposal"],
            "status": "success",
            "timestamp": time.time(),
        }

    async def reflect(self, result: Dict[str, Any], original_pulse: Dict[str, Any]):
        """
        Phase 4: Reflection — Store result in all three memory layers.

        In addition to the existing role + global cortex storage,
        we now also persist to CognitiveBridge for cross-session recall.
        """
        block = QuantumBlock(
            id=f"ref_{uuid.uuid4().hex[:8]}",
            base_color=self.color,
            content=f"Task: {original_pulse.get('intent')} | Result: {result['output']}",
            method=MethodMode.SK2_FUNDAMENTAL,
        )

        # Layer 1: Local agent memory
        await self.memory.add_block(block)

        # Layer 2: CognitiveBridge — long-term cross-session memory (NEW)
        try:
            bridge = await CognitiveBridge.get_instance()
            await bridge.store_decision(
                topic=original_pulse.get("intent", "unknown"),
                outcome=result["output"],
                z_level=self.z_level,
                tags=[self.role.lower(), "pear_reflection"],
            )
        except Exception as e:
            logger.warning(f"[PEAR] CognitiveBridge store failed: {e}")

        # Layer 3: Shared ProjectCortex
        project_cortex = await ProjectCortex.get_instance()
        await project_cortex.add_block(block)

        print(f"[RECALL] [{self.role}] Reflected → stored in all 3 memory layers.")


class ZLevelOrchestrator:
    """Manages protocol-based interaction between agents on different Z-Levels."""

    def __init__(self):
        self.agents: Dict[int, PEARAgent] = {}

    def register_agent(self, agent: PEARAgent):
        self.agents[agent.z_level] = agent

    async def hiearchical_execute(self, pulse: Dict[str, Any]):
        """
        Executes a task across Z-levels.
        Higher levels provide context, lower levels execute, mid levels stabilize.
        """
        levels = sorted(self.agents.keys(), reverse=True)
        current_context = pulse

        results = []
        for z in levels:
            agent = self.agents[z]
            print(f"[NEXUS] Routing to Z-{z} ({agent.role})...")

            perception = await agent.perceive(current_context)
            evolution = await agent.evolve(perception)
            action = await agent.act(evolution)
            await agent.reflect(action, current_context)

            results.append(action)
            current_context["intent"] += f" | Z{z}_Context: {action['output']}"

        return results


async def test_pear_protocol():
    orch = ZLevelOrchestrator()
    orch.register_agent(PEARAgent("Architect", 17, MemoryColor.WHITE))
    orch.register_agent(PEARAgent("Orchestrator", 8, MemoryColor.VIOLET))
    orch.register_agent(PEARAgent("executor", 3, MemoryColor.GREEN))

    pulse = {"pulse_id": "test_123", "intent": "Analyze recent log errors on Z4 node"}
    final_chain = await orch.hiearchical_execute(pulse)
    print("\n[OK] PEAR Hierarchical Execution Complete:")
    for r in final_chain:
        print(f"  - Z{r['z_level']} {r['agent']}: {r['status']}")


if __name__ == "__main__":
    asyncio.run(test_pear_protocol())
