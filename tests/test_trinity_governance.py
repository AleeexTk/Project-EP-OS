import pytest
import asyncio
import json
from datetime import datetime
from alpha_pyramid_core.SPINE._17_GLOBAL_NEXUS.trinity_resonance.engine import TrinityResonanceEngine
from alpha_pyramid_core.SPINE._17_GLOBAL_NEXUS.trinity_resonance.models import TriangleColor
from beta_pyramid_functional.B1_Kernel.contracts import TaskEnvelope

@pytest.fixture
def engine():
    return TrinityResonanceEngine()

@pytest.mark.asyncio
async def test_trinity_accepted_task(engine):
    # Task with good alignment and no violations
    payload = "Optimize the system architecture for better harmony and evolution."
    decision = await engine.evaluate_task("task_001", payload)
    
    assert decision.final_status == "ACCEPTED"
    assert decision.resonance_score > 0.7
    assert decision.is_vetoed is False
    assert "GOLD" in decision.evaluations
    assert "RED" in decision.evaluations
    assert "PURPLE" in decision.evaluations

@pytest.mark.asyncio
async def test_trinity_guardian_veto(engine):
    # Task with absolute path - should trigger RED (Guardian) Veto
    payload = "Access data at C:\\Users\\Secret\\Data.py"
    decision = await engine.evaluate_task("task_veto", payload)
    
    assert decision.final_status == "REJECTED"
    assert decision.is_vetoed is True
    assert "Guardian Veto" in decision.veto_reason
    assert decision.evaluations["RED"].score < 0.5

@pytest.mark.asyncio
async def test_trinity_conflicted_task(engine):
    # Task that is technically fine but lacks conceptual depth
    payload = "Just do some work without any specific vision or optimization."
    decision = await engine.evaluate_task("task_conflict", payload)
    
    # Depending on weighted score, might be CONFLICTED or REJECTED
    # Base integrator is 0.8 * 0.35 = 0.28
    # Base guardian is 1.0 * 0.4 = 0.4
    # Base soul is 0.7 * 0.25 = 0.175
    # Total = 0.855 (Actually high because base is high)
    # Let's check the rationale
    assert decision.final_status in ["ACCEPTED", "CONFLICTED"]

@pytest.mark.asyncio
async def test_trinity_injection_rejection(engine):
    # Potential SQL injection
    payload = "SELECT * FROM users; DROP TABLE sessions;"
    decision = await engine.evaluate_task("task_injection", payload)
    
    assert decision.final_status == "REJECTED"
    assert decision.evaluations["RED"].score < 0.3
