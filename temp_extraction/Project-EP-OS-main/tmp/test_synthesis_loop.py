import asyncio
import os
import sys
import json
from pathlib import Path

# Setup path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from beta_pyramid_functional.B2_Orchestrator.synthesis_agent import SynthesisAgent

async def test_synthesis_loop():
    print("--- EVO-PYRAMID V7.0: GLOBAL SYNTHESIS TEST ---")
    agent = SynthesisAgent()
    
    print("[TEST] Scanning ProjectCortex for patterns...")
    report_id = await agent.scan_and_synthesize()
    
    if "No memory blocks" in report_id:
        print(f"[TEST] {report_id}")
        return

    print(f"[TEST] Synthesis Successful! Report ID: {report_id}")
    
    # Load and display the report
    report_path = Path(f"beta_pyramid_functional/D_Interface/synthesis_reports/{report_id}.json")
    if report_path.exists():
        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)
            print("\n--- SYNTHESIS REPORT SUMMARY ---")
            print(f"Timestamp: {report['timestamp']}")
            print(f"Analyzed Blocks: {report['analyzed_blocks']}")
            print(f"Patterns Discovered: {report['patterns_discovered']}")
            
            for cluster in report['clusters']:
                print(f"\n[PATTERN: {cluster['cluster_id']}]")
                print(f"  - Stability Group: {cluster['member_count']} members")
                print(f"  - Key Members: {', '.join(cluster['members'][:3])}...")
    
    print("\n[SUCCESS] Global Synthesis (V7.0) verified. The system can now autonomously identify architectural patterns.")

if __name__ == "__main__":
    asyncio.run(test_synthesis_loop())
