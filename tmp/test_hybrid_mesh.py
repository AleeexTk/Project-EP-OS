import asyncio
import sys
import os
from pathlib import Path

# Add project root to sys.path
root_dir = Path(r"c:\Users\Alex Bear\Desktop\EvoPyramid OS")
sys.path.insert(0, str(root_dir))
sys.path.insert(0, str(root_dir / "beta_pyramid_functional"))
sys.path.insert(0, str(root_dir / "beta_pyramid_functional" / "B1_Kernel"))
sys.path.insert(0, str(root_dir / "beta_pyramid_functional" / "B2_Orchestrator"))
sys.path.insert(0, str(root_dir / "beta_pyramid_functional" / "B3_SessionRegistry"))

async def test_supervised_mesh():
    from llm_orchestrator import AgentOrchestrator
    from session_models import Provider, AgentSession, Message
    
    # Mock a session
    session = AgentSession(
        id="test-val-1",
        node_id="chaos_engine",
        node_z=7,
        provider=Provider.GEMINI,
        task_title="Verify Local Mesh",
        task_context="Checking if the supervisor can evaluate a response.",
        messages=[Message(role="user", content="Hello, tell me about Z7.")]
    )
    
    # Force Gemini quota block to test fallback
    import llm_orchestrator
    llm_orchestrator._GEMINI_QUOTA_BLOCK_UNTIL = sys.maxsize # Forever in the future
    
    print("--- Starting Supervised Hybrid Call (Simulating Gemini Block) ---")
    try:
        response = await AgentOrchestrator.get_response(session)
        print("\n[FINAL RESPONSE]")
        print(response)
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_supervised_mesh())
