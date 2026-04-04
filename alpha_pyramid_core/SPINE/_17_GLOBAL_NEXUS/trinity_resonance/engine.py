import hashlib
import time
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from .models import TriangleColor, TrinityState, CoherenceLevel, TrinityDirective, ValidationResult
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

class FormalResonanceEngine:
    """Формальный движок резонанса (Z17 Core Integration)"""
    
    def __init__(self, admin_name: str = "Админ Алекс"):
        self.version = "3.0.0"
        self.admin = admin_name
        self.creation_time = datetime.now()
        self.session_id = hashlib.sha256(f"{self.admin}_{self.creation_time}".encode()).hexdigest()[:16]
        self.coherence_history = []
        
        self.validator = FormalValidator(self)
        self.normalizer = FormalNormalizer(self)
        self.triangles = {c: TriangleState(c) for c in TriangleColor}

    async def process(self, message: str, triangle_code: str) -> Dict[str, Any]:
        """Обработка через Z17-FSM"""
        try:
            triangle = TriangleColor[triangle_code.upper()]
        except KeyError:
            return {"status": "error", "reason": f"Unknown triangle: {triangle_code}"}
            
        t_state = self.triangles[triangle]
        t_state.transition(TrinityState.LISTENING)
        
        # 1. Parsing
        t_state.transition(TrinityState.PARSING)
        parsed = await self.validator.parse_input(message, triangle)
        
        # 2. Normalization
        t_state.transition(TrinityState.NORMALIZING)
        normalized = await self.normalizer.normalize(parsed, triangle)
        
        # 3. Validation
        t_state.transition(TrinityState.VALIDATING)
        validation = await self.validator.validate(parsed, triangle)
        
        # 4. Correcting if needed
        final_message = normalized
        if not validation.is_valid:
            t_state.transition(TrinityState.CORRECTING)
            final_message = await self.normalizer.correct(normalized, triangle, validation)
            validation = await self.validator.validate({"raw": final_message, "hash": parsed["hash"]}, triangle)
            
        if validation.is_valid:
            t_state.transition(TrinityState.EMITTING)
            self.coherence_history.append(validation.final_coherence)
            return {
                "status": "success",
                "triangle": triangle.code,
                "coherence": validation.final_coherence,
                "result": final_message,
                "state": t_state.current_state.name
            }
        else:
            t_state.transition(TrinityState.BLOCKED)
            return {"status": "blocked", "violations": validation.violations}
