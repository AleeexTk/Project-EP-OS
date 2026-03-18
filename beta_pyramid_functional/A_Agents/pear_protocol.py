import asyncio
import uuid
import time
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# Absolute paths for imports
import sys
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

try:
    from beta_pyramid_functional.B1_Kernel.SK_Engine.engine import CortexMemory
    from beta_pyramid_functional.B1_Kernel.SK_Engine.models import QuantumBlock, MemoryColor, MethodMode
    from beta_pyramid_functional.B1_Kernel.events import EventType, create_event
    from beta_pyramid_functional.B2_Orchestrator.llm_orchestrator import AgentOrchestrator, Provider, AgentSession
except ImportError as e:
    print(f"!! [PEAR_BRIDGE] Import failed, using simplified logic: {e}")

logger = logging.getLogger("PEAR_Protocol")

class PEARAgent:
    """
    Standard Base for agents participating in the PEAR loop 
    (Perception, Evolution, Action, Reflection).
    """
    def __init__(self, role: str, z_level: int, color: MemoryColor, provider: str = "ollama"):
        self.role = role
        self.z_level = z_level
        self.color = color
        self.provider = provider
        self.memory = CortexMemory(data_dir=ROOT_DIR / "state" / "agent_memory" / role.lower())
        
    async def perceive(self, pulse_data: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 1: Perception - Gather context and similar past experiences."""
        intent = pulse_data.get("intent", "")
        past_blocks = await self.memory.find_similar(intent)
        context = [b.to_dict() for b in past_blocks[:3]]
        
        return {
            "perceived_intent": intent,
            "relevant_past": context,
            "pulse_id": pulse_data.get("pulse_id")
        }

    async def evolve(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 2: Evolution - Logic to transform perception into a proposal."""
        intent = perception["perceived_intent"]
        mem_context = json.dumps(perception["relevant_past"])
        
        try:
            # Create a session to talk through the orchestrator
            session = AgentSession(
                node_id=f"z{self.z_level}-{self.role.lower()}",
                node_z=self.z_level,
                provider=Provider.OLLAMA if self.provider == "ollama" else Provider.GEMINI,
                task_context=f"PEAR Evolution Cycle. History: {mem_context}"
            )
            session.add_user_message(f"Evolve the following intent based on your architecture role as {self.role}: {intent}")
            
            response = await AgentOrchestrator.get_response(session)
            return {"proposal": response or "No proposal generated.", "status": "evolved"}
        except Exception as e:
            logger.error(f"Evolution failed for {self.role}: {e}")
            return {"proposal": f"Fallback: Basic action for {intent}", "status": "evolved_fallback"}

    async def act(self, evolution: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 3: Action - Execution of the proposal."""
        action_result = {
            "agent": self.role,
            "z_level": self.z_level,
            "output": evolution["proposal"],
            "status": "success",
            "timestamp": time.time()
        }
        return action_result

    async def reflect(self, result: Dict[str, Any], original_pulse: Dict[str, Any]):
        """Phase 4: Reflection - Store result in SK_Engine for future Perception."""
        block = QuantumBlock(
            id=f"ref_{uuid.uuid4().hex[:8]}",
            base_color=self.color,
            content=f"Task: {original_pulse.get('intent')} | Result: {result['output']}",
            method=MethodMode.SK2_FUNDAMENTAL
        )
        await self.memory.add_block(block)
        print(f"[RECALL] [{self.role}] Reflected and stored experience.")

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
        # Sort levels descending (Z17 -> Z0)
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
            # Carry over results to next level as context
            current_context["intent"] += f" | Z{z}_Context: {action['output']}"
            
        return results

async def test_pear_protocol():
    orch = ZLevelOrchestrator()
    # Mock agents for demo
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
