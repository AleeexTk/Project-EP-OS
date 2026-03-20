import asyncio
import os
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from beta_pyramid_functional.B2_Orchestrator.auto_corrector import AutoCorrector
from beta_pyramid_functional.B4_Cognitive.cognitive_bridge import CognitiveBridge

async def mock_get_response(session, **kwargs):
    print("   [LLM MOCK] Generating fake patch...")
    return "def broken():\n    return 42\n"

async def main():
    corrector = AutoCorrector()
    # Mock the LLM to skip 60s waits
    corrector.orchestrator.get_response = mock_get_response
    
    with open("tmp/broken_file.py", "w", encoding="utf-8") as f:
        f.write("def broken():\n    return 1 / 0\n")
        
    error_traceback = '''Traceback (most recent call last):
  File "tmp/broken_file.py", line 2, in broken
ZeroDivisionError: division by zero
'''
    print("-" * 50)
    print("[1] FIRST CALL - EXPECT LLM SYNTHESIS")
    print("-" * 50)
    p1 = await corrector.propose_fix(error_traceback)
    if p1:
        print("\nProposal 1 rationale:\n", p1.rationale)
        
    # Give it a moment to ensure disk flush if any
    await asyncio.sleep(1)
    
    print("\n" + "-" * 50)
    print("[2] SECOND CALL - EXPECT MEMORY RECALL (BYPASS)")
    print("-" * 50)
    p2 = await corrector.propose_fix(error_traceback)
    if p2:
        print("\nProposal 2 rationale:\n", p2.rationale)
    
    if p2 and "MEMORY BYPASS" in p2.rationale:
        print("\n>>> EXPERIENTIAL LEARNING SUCCESSFUL! <<<")
    else:
        print("\n>>> FAILED TO BYPASS <<<")

if __name__ == "__main__":
    asyncio.run(main())
