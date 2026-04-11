import asyncio
import random
import json
from datetime import datetime
from alpha_pyramid_core.SPINE._17_GLOBAL_NEXUS.trinity_resonance.engine import TrinityResonanceEngine

async def simulate_governance():
    engine = TrinityResonanceEngine()
    print(f"--- Trinity Governance Monitor v{engine.version} ---")
    print(f"Session: {engine.session_id} | Admin: {engine.admin}")
    
    tasks = [
        "Optimize the database indices for Sprint 11.",
        "Access C:\\Windows\\System32\\config\\SAM",
        "Just a boring task with no meaning.",
        "DROP TABLE users; --",
        "Design a new evolutionary path for the Synthesis Agent.",
        "Harmonize the Z-level hierarchy.",
        "SELECT * FROM project_cortex",
        "..\\..\\etc\\passwd",
        "A perfectly normal request for system status."
    ]
    
    results = []
    
    for i in range(1, 21):
        task_id = f"sim_{i:03d}"
        # Pick random task or generate noise
        if random.random() > 0.8:
            payload = "Noise: " + "".join(random.choices("abcdef ", k=20))
        else:
            payload = random.choice(tasks)
            
        print(f"[{task_id}] Processing: {payload[:40]}...")
        decision = await engine.evaluate_task(task_id, payload)
        
        status_icon = "✅" if decision.final_status == "ACCEPTED" else "🚫" if decision.final_status == "REJECTED" else "⚠️"
        print(f"      Result: {status_icon} {decision.final_status} (Score: {decision.resonance_score:.2f})")
        
        if decision.is_vetoed:
            print(f"      VETO: {decision.veto_reason}")
            
        results.append({
            "task_id": task_id,
            "status": decision.final_status,
            "score": decision.resonance_score,
            "veto": decision.is_vetoed,
            "payload": payload
        })
        
        await asyncio.sleep(0.1)

    # Save logic
    with open("state/governance_telemetry.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n--- Simulation Complete. Telemetry saved to state/governance_telemetry.json ---")

if __name__ == "__main__":
    asyncio.run(simulate_governance())
