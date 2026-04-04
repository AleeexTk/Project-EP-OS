import re
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, List
from .models import TriangleColor, ValidationResult

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
            "injection": re.compile(r'[;\{\}\[\]\(\)\"\']|--|\b(?:DROP|DELETE|INSERT|UPDATE|SELECT)\b', re.IGNORECASE)
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
