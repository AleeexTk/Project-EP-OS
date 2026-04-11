import hashlib
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from .models import TriangleColor, TrinityState, CoherenceLevel, TrinityDirective, ValidationResult, TrinityDecision
from .validator import FormalValidator
from .normalizer import FormalNormalizer

class TriangleState:
    """Состояние отдельного треугольника в FSM"""
    def __init__(self, color: TriangleColor):
        self.color = color
        self.current_state = TrinityState.DORMANT
        self.coherence_score = 1.0
        self.last_activity = datetime.now()
        self.state_history = []

    def transition(self, new_state: TrinityState) -> bool:
        # Простая матрица переходов TRIN v3.0
        valid_transitions = {
            TrinityState.DORMANT: {TrinityState.LISTENING},
            TrinityState.LISTENING: {TrinityState.PARSING, TrinityState.BLOCKED},
            TrinityState.PARSING: {TrinityState.NORMALIZING, TrinityState.BLOCKED},
            TrinityState.NORMALIZING: {TrinityState.VALIDATING, TrinityState.CORRECTING},
            TrinityState.VALIDATING: {TrinityState.EMITTING, TrinityState.CORRECTING, TrinityState.BLOCKED},
            TrinityState.CORRECTING: {TrinityState.EMITTING, TrinityState.BLOCKED},
            TrinityState.EMITTING: {TrinityState.LISTENING, TrinityState.DORMANT},
            TrinityState.BLOCKED: {TrinityState.RECOVERING},
            TrinityState.RECOVERING: {TrinityState.DORMANT}
        }
        if new_state in valid_transitions.get(self.current_state, set()):
            self.state_history.append((self.current_state, datetime.now()))
            self.current_state = new_state
            self.last_activity = datetime.now()
            return True
        return False

class TrinityResonanceEngine:
    """Движок резонанса Trinity (Z17)"""
    
    def __init__(self, admin_name: str = "Админ Алекс"):
        self.version = "3.1.0"
        self.admin = admin_name
        self.creation_time = datetime.now()
        self.session_id = hashlib.sha256(f"{self.admin}_{self.creation_time}".encode()).hexdigest()[:16]
        
        self.validator = FormalValidator(self)
        self.normalizer = FormalNormalizer(self)
        self.triangles = {c: TriangleState(c) for c in TriangleColor if c != TriangleColor.BLACK}

    async def evaluate_task(self, task_id: str, payload: str) -> TrinityDecision:
        """Оркестрация резонанса между тремя ролями"""
        # 1. Парсинг и нормализация
        parsed = await self.validator.parse_input(payload, TriangleColor.BLACK)
        
        # 2. Сбор оценок от ролей
        evals = {}
        for role in [TriangleColor.GOLD, TriangleColor.RED, TriangleColor.PURPLE]:
            evals[role.name] = await self.validator.evaluate_role(role, parsed)
        
        # 3. Расчет резонанса (Взвешенная оценка)
        # GOLD (Integrator) = 0.35, RED (Guardian) = 0.4, PURPLE (Soul) = 0.25
        resonance_score = (
            evals["GOLD"].score * 0.35 +
            evals["RED"].score * 0.4 +
            evals["PURPLE"].score * 0.25
        )
        
        # 4. Проверка ВЕТО (Iron Guardian)
        is_vetoed = False
        veto_reason = None
        if evals["RED"].score < 0.3:
            is_vetoed = True
            veto_reason = f"Guardian Veto: {evals['RED'].rationale}"
        
        # 5. Финальный статус
        if is_vetoed:
            final_status = "REJECTED"
        elif resonance_score >= 0.7:
            final_status = "ACCEPTED"
        elif resonance_score >= 0.4:
            final_status = "CONFLICTED"
        else:
            final_status = "REJECTED"
            
        decision = TrinityDecision(
            task_id=task_id,
            timestamp=datetime.now(),
            consensus_met=(final_status == "ACCEPTED"),
            resonance_score=resonance_score,
            evaluations=evals,
            final_status=final_status,
            is_vetoed=is_vetoed,
            veto_reason=veto_reason,
            audit_trace=hashlib.sha256(f"{task_id}_{final_status}".encode()).hexdigest()
        )
        
        return decision

    async def process(self, message: str, triangle_code: str) -> Dict[str, Any]:
        """Обратная совместимость с оригинальным API TRIN"""
        decision = await self.evaluate_task(f"legacy_{int(time.time())}", message)
        
        return {
            "status": "success" if decision.final_status == "ACCEPTED" else "blocked",
            "decision": decision,
            "resonance_score": decision.resonance_score
        }
