from enum import Enum, auto
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set

class TriangleColor(Enum):
    """Формальные цвета треугольника с каноническими ролями в EvoPyramid"""
    # Маппинг цветов TRIN v3.0 на координаты EP-OS
    BLACK = ("BLACK", "🖤", "Meta", "Z17 - Apex Orchestration")
    GOLD = ("GOLD", "🟨", "Integrator", "Z12 - Synthesis & Integration")
    RED = ("RED", "🟥", "Guardian", "Z14 - Security & Stability")
    GREEN = ("GREEN", "🟩", "Trailblazer", "Z16 - Efficiency & Routes")
    PURPLE = ("PURPLE", "🟪", "Soul", "Z5 - Creativity & Vision")
    
    def __init__(self, code: str, symbol: str, role: str, description: str):
        self.code = code
        self.symbol = symbol
        self.role = role
        self.description = description

class TrinityState(Enum):
    """Конечный автомат состояний треугольника"""
    DORMANT = auto()      # Спящий режим
    LISTENING = auto()    # Ожидание ввода
    PARSING = auto()      # Синтаксический анализ
    NORMALIZING = auto()  # Нормализация формы
    VALIDATING = auto()   # Семантическая валидация
    CORRECTING = auto()   # Автоматическая коррекция
    EMITTING = auto()     # Эмиссия результата
    BLOCKED = auto()      # Блокировка из-за нарушений
    RECOVERING = auto()   # Восстановление после ошибки

class CoherenceLevel(Enum):
    """Уровни когерентности с пороговыми значениями"""
    CRITICAL = (0.0, 0.3, "⚡ КРИТИЧЕСКИЙ", "Система нестабильна")
    WARNING = (0.3, 0.7, "⚠️ ПРЕДУПРЕЖДЕНИЕ", "Частичные нарушения")
    STABLE = (0.7, 0.9, "✅ СТАБИЛЬНО", "Минимальные отклонения")
    OPTIMAL = (0.9, 1.0, "✨ ОПТИМАЛЬНО", "Полная когерентность")
    
    def __init__(self, min_val: float, max_val: float, icon: str, description: str):
        self.min = min_val
        self.max = max_val
        self.icon = icon
        self.description = description
    
    @classmethod
    def from_value(cls, value: float) -> 'CoherenceLevel':
        for level in cls:
            if level.min <= value < level.max:
                return level
        return cls.CRITICAL

@dataclass
class TrinityDirective:
    """Формальная директива активации"""
    id: str
    timestamp: datetime
    version: str
    admin: str
    resonance_signature: str
    coherence_threshold: float = 0.7
    max_corrections: int = 3
    ttl_seconds: int = 3600

@dataclass
class RoleEvaluation:
    """Результат оценки отдельной ролью"""
    role: TriangleColor
    score: float  # 0.0 to 1.0 (0.0=Reject, 1.0=Full Support)
    confidence: float
    rationale: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TrinityDecision:
    """Финальное решение Trinity Resonance Engine"""
    task_id: str
    timestamp: datetime
    consensus_met: bool
    resonance_score: float  # Weighted average
    evaluations: Dict[str, RoleEvaluation]  # Role code -> Evaluation
    final_status: str  # ACCEPTED, REJECTED, CONFLICTED
    is_vetoed: bool = False
    veto_reason: Optional[str] = None
    audit_trace: str = ""  # Hash for ledger

@dataclass
class ValidationResult:
    """Формальный результат валидации"""
    is_valid: bool
    input_hash: str
    triangle: TriangleColor
    timestamp: datetime
    coherence_vector: Tuple[float, float, float]
    violations: List[str] = field(default_factory=list)
    corrections: List[str] = field(default_factory=list)
    transformations: List[Dict] = field(default_factory=list)
    final_coherence: float = 1.0
    explainability_trace: List[str] = field(default_factory=list)
    decision: Optional[TrinityDecision] = None
