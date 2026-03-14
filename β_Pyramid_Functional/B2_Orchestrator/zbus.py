import asyncio
import logging
from typing import Dict, Any

class ZBus:
    """
    Message Broker (Z-Bus) for routing LLM prompts to the Nexus Browser Extension.
    """
    def __init__(self):
        self.queue = asyncio.Queue()
        self.running = False
        
    async def dispatch_llm_task(self, node_id: str, target_url: str, prompt: str):
        task = {
            "type": "LLM_INJECT_PROMPT",
            "node_id": node_id,
            "url": target_url,
            "prompt": prompt
        }
        await self.queue.put(task)
        logging.info(f"[Z-Bus] Task enqueued for node {node_id} (Target: {target_url})")

    async def run_worker(self, websocket_manager, current_state):
        self.running = True
        logging.info("[Z-Bus] Async worker initialized. Listening for tasks...")
        while self.running:
            try:
                task = await self.queue.get()
                node_id = task["node_id"]
                
                # 1. Update node state to WAITING
                if node_id in current_state.nodes:
                    # We use the string representation directly so the IDE static analyzer doesn't complain about unresolvable imports.
                    # Pydantic natively parses this onto the correct OrchestratorState Enum.
                    current_state.nodes[node_id].orchestrator_state = "waiting_for_llm"
                    
                    # Ensure node_update fires
                    await websocket_manager.broadcast({
                        "type": "node_update", 
                        "data": current_state.nodes[node_id].model_dump()
                    })

                # 2. Transmit command to Chrome Extension WSS Client
                logging.info(f"[Z-Bus] Routing task to extension for Node {node_id}")
                await websocket_manager.broadcast(task)
                
                self.queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"[Z-Bus] Worker error: {e}")

zbus = ZBus()
