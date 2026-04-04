import json
from datetime import datetime
from typing import Dict, Optional
from .models import TriangleColor, ValidationResult

class FormalNormalizer:
    """Формальный нормализатор с безопасной автокоррекцией (EvoPyramid Z14 Adaptation)"""
    
    def __init__(self, engine=None):
        self.engine = engine
        self.correction_history = []
        self.max_corrections = 3
    
    async def normalize(self, parsed: Dict, triangle: TriangleColor) -> str:
        raw_text = parsed["raw"]
        
        if triangle == TriangleColor.GOLD:
            if not parsed.get("has_quotes", False):
                return f'"{raw_text}"'
        elif triangle == TriangleColor.RED:
            if not raw_text.startswith("❓"):
                return f"❓ {raw_text.rstrip('?')}?"
        elif triangle == TriangleColor.GREEN:
            if "#[" not in raw_text:
                data_id = f"D{int(datetime.now().timestamp())}"
                json_data = {"content": raw_text, "id": data_id, "timestamp": datetime.now().isoformat()}
                return f"#[{data_id}] {json.dumps(json_data, ensure_ascii=False)}"
        return raw_text

    async def correct(self, text: str, triangle: TriangleColor, validation: ValidationResult) -> str:
        if len(self.correction_history) >= self.max_corrections:
            raise RuntimeError(f"Достигнут лимит коррекций: {self.max_corrections}")
        
        corrected = text
        for correction in validation.corrections[:2]:
            if "кавычки" in correction.lower():
                corrected = f'"{corrected}"' if not (corrected.startswith('"') and corrected.endswith('"')) else corrected
            elif "вопрос" in correction.lower() or "❓" in correction:
                corrected = f"❓ {corrected.rstrip('?')}?"
        
        self.correction_history.append({"timestamp": datetime.now().isoformat(), "triangle": triangle.code, "original": text[:50], "corrected": corrected[:50]})
        return corrected
