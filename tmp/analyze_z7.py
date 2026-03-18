import asyncio
import sys
import os
from pathlib import Path

# Add the project root and orchestrator path to sys.path
project_root = Path(r"c:\Users\Alex Bear\Desktop\EvoPyramid OS")
orchestrator_path = project_root / "beta_pyramid_functional" / "B2_Orchestrator"
sys.path.append(str(project_root))
sys.path.append(str(orchestrator_path))

try:
    from llm_orchestrator import OllamaSupervisor, Provider
    
    async def main():
        # Mocking an AgentSession
        class MockSession:
            def __init__(self, title, context):
                self.task_title = title
                self.task_context = context
                self.node_id = "chaos_engine"
                self.node_z = 7
                self.provider = Provider.OLLAMA
        
        session = MockSession(
            "Analyze Z7 Anomaly",
            "An architectural anomaly has been detected in Z-Level 7. Specifically, the 'chaos_engine' and 'gen-webmcp' nodes are reporting active status but triggering UI alerts."
        )
        
        supervisor = OllamaSupervisor()
        print(f"--- Initiating Supervisor Analysis ---")
        analysis = await supervisor.analyze_task(session)
        print("\n[ANALYSIS RESULT]")
        print(analysis)
    
    asyncio.run(main())
    
except Exception as e:
    print(f"Error during supervisor analysis: {e}")
