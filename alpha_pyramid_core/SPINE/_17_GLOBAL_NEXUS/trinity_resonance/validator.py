import re
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, List
from .models import TriangleColor, ValidationResult, RoleEvaluation

class FormalValidator:
    """Формальный валидатор с многоуровневой проверкой (EvoPyramid v17)"""
    
    def __init__(self, engine=None):
        self.engine = engine
        self.cache = {}
        self.patterns = self._initialize_patterns()
    
    def _initialize_patterns(self) -> Dict[str, re.Pattern]:
        return {
            "gold_logic": re.compile(r'\b(?:if|then|else|for|while|return|function|algorithm|O\([^)]+\)|optimize|analyze|calculate)\b', re.IGNORECASE),
            "gold_action": re.compile(r'\b(?:синтезировать|оптимизировать|рассчитать|сравнить|проанализировать|спроектировать)\b', re.IGNORECASE),
            "red_question": re.compile(r'^(❓|\?|почему|как|что|зачем|когда|где)\s*', re.IGNORECASE),
            "green_json": re.compile(r'^#\[[^\]]+\]\s*\{.*\}', re.DOTALL),
            "injection": re.compile(r'[;\{\}\[\]\(\)\"\']|--|\b(?:DROP|DELETE|INSERT|UPDATE|SELECT|UNION|EXEC|EVAL)\b', re.IGNORECASE),
            "path_traversal": re.compile(r'(?:\.\.[\\/])|(?:\\[a-z]:)|(?:/[a-z]+/)', re.IGNORECASE),
            "obfuscated_path": re.compile(r'[a-z]\s*:\s*[\\/]+', re.IGNORECASE)
        }
    
    async def parse_input(self, text: str, triangle: TriangleColor) -> Dict[str, Any]:
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in self.cache: return self.cache[text_hash]
        
        parsed = {
            "raw": text,
            "hash": text_hash,
            "length": len(text),
            "word_count": len(text.split()),
            "triangle": triangle.code
        }
        
        # Triangle-specific parsing logic from TRIN v3.0
        if triangle == TriangleColor.GOLD:
            parsed.update({"has_quotes": text.startswith('"') and text.endswith('"'), "logic_score": self._calculate_logic_score(text)})
        # ... (further parsing as needed)
        
        self.cache[text_hash] = parsed
        return parsed

    def _calculate_logic_score(self, text: str) -> float:
        score = 0.5
        if self.patterns["gold_logic"].search(text): score += 0.2
        if self.patterns["gold_action"].search(text): score += 0.2
        return min(1.0, score)

    async def validate(self, parsed: Dict, triangle: TriangleColor) -> ValidationResult:
        violations = []
        corrections = []
        form_coherence, semantic_coherence, arch_coherence = 1.0, 1.0, 1.0
        
        if triangle == TriangleColor.GOLD:
            if not parsed.get("has_quotes"):
                violations.append("GOLD: Отсутствуют кавычки")
                corrections.append("Добавить кавычки")
                form_coherence = 0.3
        
        # Calculate final coherence
        final_coherence = (form_coherence * 0.4 + semantic_coherence * 0.4 + arch_coherence * 0.2)
        
        return ValidationResult(
            is_valid=len(violations) == 0,
            input_hash=parsed["hash"],
            triangle=triangle,
            timestamp=datetime.now(),
            coherence_vector=(form_coherence, semantic_coherence, arch_coherence),
            violations=violations,
            corrections=corrections,
            final_coherence=final_coherence
        )

    async def evaluate_role(self, role: TriangleColor, parsed: Dict) -> RoleEvaluation:
        """Оценка задачи конкретной ролью Trinity"""
        if role == TriangleColor.GOLD:
            return self._evaluate_integrator(parsed)
        elif role == TriangleColor.RED:
            return self._evaluate_guardian(parsed)
        elif role == TriangleColor.PURPLE:
            return self._evaluate_soul(parsed)
        return RoleEvaluation(role, 0.5, 0.1, "Unknown role", {})

    def _evaluate_integrator(self, parsed: Dict) -> RoleEvaluation:
        """Trailblazer: Фокус на эффективности и интеграции"""
        score = 0.6  # Lower base
        rationale = "Task appears technically feasible."
        
        # Check for logic complexity
        logic_score = parsed.get("logic_score", 0)
        if logic_score > 0.7:
            score += 0.2
            rationale += " High algorithmic clarity detected."
        elif logic_score < 0.5:
            score -= 0.3
            rationale += " Low technical coherence detected."
        
        return RoleEvaluation(
            role=TriangleColor.GOLD,
            score=min(1.0, max(0.0, score)),
            confidence=0.9,
            rationale=rationale
        )

    def _evaluate_guardian(self, parsed: Dict) -> RoleEvaluation:
        """Provocateur: Фокус на безопасности и паранойе"""
        score = 1.0
        violations = []
        raw_text = parsed.get("raw", "")
        
        # Paranoid checks
        if self.patterns["path_traversal"].search(raw_text) or self.patterns["obfuscated_path"].search(raw_text):
            score -= 0.8
            violations.append("Absolute or traversal paths detected.")
        
        if "C:\\" in raw_text or "/home/" in raw_text or "/etc/" in raw_text:
            if not any(v == "Absolute or traversal paths detected." for v in violations):
                score -= 0.8
                violations.append("Literal absolute paths detected.")
        
        # Check for obfuscated unix paths
        if re.search(r'/ ?h ?o ?m ?e ?/', raw_text, re.IGNORECASE) or re.search(r'/ ?e ?t ?c ?/', raw_text, re.IGNORECASE):
            score -= 0.8
            violations.append("Obfuscated unix paths detected.")
        
        if self.patterns["injection"].search(raw_text):
            score -= 0.8
            violations.append("Potential injection pattern detected.")
        
        rationale = "Security scan complete." if not violations else f"Security risks: {', '.join(violations)}"
        
        return RoleEvaluation(
            role=TriangleColor.RED,
            score=max(0.0, score),
            confidence=0.95,
            rationale=rationale
        )

    def _evaluate_soul(self, parsed: Dict) -> RoleEvaluation:
        """Soul: Фокус на концептуальном соответствии и фидбеке"""
        score = 0.5  # Lower base score
        raw_text = parsed.get("raw", "").lower()
        
        # Check for alignment with "Alex" / User vision tokens
        if any(token in raw_text for token in ["arch", "vision", "harmony", "evolution", "alex", "epos", "pyramid"]):
            score += 0.3
            rationale = "High conceptual alignment with system evolution."
        else:
            rationale = "Low conceptual alignment - potential noise or irrelevant input."
            score = 0.2  # Set low score for no alignment
            
        return RoleEvaluation(
            role=TriangleColor.PURPLE,
            score=max(0.0, min(1.0, score)),
            confidence=0.8,
            rationale=rationale
        )
