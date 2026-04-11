import pytest
import asyncio
from alpha_pyramid_core.SPINE._17_GLOBAL_NEXUS.trinity_resonance.engine import TrinityResonanceEngine

@pytest.fixture
def engine():
    return TrinityResonanceEngine()

@pytest.mark.asyncio
async def test_adversarial_path_obfuscation(engine):
    """Тест на обход путей через пробелы и разные слеши"""
    payloads = [
        "Read C : \\ Windows \\ system32",
        "Access / h o m e / user / secret",
        "Open file:///C:/Windows/System32/drivers/etc/hosts",
        "..\\..\\Windows\\System32"
    ]
    for p in payloads:
        decision = await engine.evaluate_task("task_obfs", p)
        # Guardian (RED) должен увидеть 'C:\' или '/home/' даже с пробелами если мы улучшим валидатор, 
        # но пока проверим базовое поведение
        assert decision.final_status == "REJECTED", f"Payload failed to be caught: {p}"

@pytest.mark.asyncio
async def test_adversarial_injection_obfuscation(engine):
    """Тест на обход инъекций через регистр и разделители"""
    payloads = [
        "dRoP TaBlE users",
        "SELECT * FROM accounts --",
        "'; DROP DATABASE ep_os; --",
        "eval('import os; os.system(\"rm -rf /\")')"
    ]
    for p in payloads:
        decision = await engine.evaluate_task("task_inj_obfs", p)
        assert decision.final_status == "REJECTED", f"Injection failed to be caught: {p}"

@pytest.mark.asyncio
async def test_adversarial_conceptual_vacuum(engine):
    """Тест на полное отсутствие концептуального смысла (Soul REJECT)"""
    payload = "asd asd asd asd asd asd"
    decision = await engine.evaluate_task("task_noise", payload)
    
    # Роль Soul (PURPLE) должна дать низкий балл, что снизит общий резонанс
    assert decision.evaluations["PURPLE"].score <= 0.7
    # Если общий резонанс < 0.4, то REJECTED. Если > 0.4 но < 0.7, то CONFLICTED.
    assert decision.final_status in ["REJECTED", "CONFLICTED"]

@pytest.mark.asyncio
async def test_adversarial_threshold_resonance(engine):
    """Тест на пограничные значения резонанса"""
    # Задача, которая "балансирует" на грани
    payload = "Perform standard maintenance. No special vision, but safe."
    decision = await engine.evaluate_task("task_edge", payload)
    
    # Мы ожидаем либо ACCEPTED (если база высока), либо CONFLICTED
    assert decision.final_status in ["ACCEPTED", "CONFLICTED"]
    assert decision.resonance_score > 0.0
