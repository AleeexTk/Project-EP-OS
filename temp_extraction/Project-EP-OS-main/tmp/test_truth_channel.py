import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from beta_pyramid_functional.B2_Orchestrator.llm_orchestrator import AgentOrchestrator
from beta_pyramid_functional.B3_SessionRegistry.session_models import AgentSession, Provider

async def main():
    session = AgentSession(
        node_id="alexcreator_navigator",
        node_z=17,
        task_title="Navigator smoke test",
        provider=Provider.OLLAMA,
        task_context="Optimize Z-Bus dispatcher for ultra-low latency."
    )
    
    ctx = await AgentOrchestrator._system_context(session)
    print("=== SYSTEM CONTEXT DUMP ===")
    print(ctx)
    print("===========================")

if __name__ == "__main__":
    asyncio.run(main())
