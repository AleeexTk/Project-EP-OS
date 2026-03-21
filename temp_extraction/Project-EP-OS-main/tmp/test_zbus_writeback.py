
import asyncio
import json
import logging
import sys
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path("c:/Users/Alex Bear/Desktop/EvoPyramid OS")
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "beta_pyramid_functional" / "B3_SessionRegistry"))
sys.path.insert(0, str(PROJECT_ROOT / "beta_pyramid_functional" / "B2_Orchestrator"))

async def test_writeback():
    logging.basicConfig(level=logging.INFO)
    from zbus import zbus
    from session_models import SessionRegistry, SessionCreateRequest, MessageCreateRequest
    
    # 1. Create a dummy session
    session = SessionRegistry.create(SessionCreateRequest(
        node_id="test_node",
        node_z=10,
        provider="gpt",
        task_title="Z-Bus Smoke Test"
    ))
    session_id = session.id
    print(f"Created Test Session: {session_id}")

    # 2. Setup the same handler as in evo_api.py
    async def memory_writeback_handler(event_dict):
        try:
            if event_dict.get("topic") == "RESPONSE_COMPLETE":
                sid = event_dict.get("session_id")
                content = event_dict.get("payload", {}).get("content", "")
                if sid == session_id and content:
                    SessionRegistry.add_message(sid, MessageCreateRequest(role="assistant", content=content))
                    print(f"SUCCESS: Captured and saved back to {sid}")
        except Exception as e:
            print(f"ERROR in handler: {e}")

    zbus.subscribe("RESPONSE_COMPLETE", memory_writeback_handler)
    
    # Start worker
    worker = asyncio.create_task(zbus.run_worker(None))
    await asyncio.sleep(0.5)

    # 3. Publish mock event
    print("Publishing mock RESPONSE_COMPLETE...")
    await zbus.publish({
        "topic": "RESPONSE_COMPLETE",
        "session_id": session_id,
        "payload": {"content": "Hello from Z-Bus Smoke Test!"}
    })

    await asyncio.sleep(1)
    
    # 4. Verify result
    updated_session = SessionRegistry.get(session_id)
    msg_count = len(updated_session.messages)
    print(f"Final message count: {msg_count}")
    
    if msg_count > 0 and updated_session.messages[-1].content == "Hello from Z-Bus Smoke Test!":
        print("VERIFICATION PASSED")
    else:
        print("VERIFICATION FAILED")

    worker.cancel()

if __name__ == "__main__":
    asyncio.run(test_writeback())
