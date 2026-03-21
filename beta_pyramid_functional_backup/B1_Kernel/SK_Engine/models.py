from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
import time
import json
from .config import MemoryColor, DynamicState, MethodMode

@dataclass
class QuantumBlock:
    id: str
    hyper_id: Optional[str] = None
    base_color: MemoryColor = MemoryColor.BLUE
    content: str = ""
    compressed_content: bytes = b""
    keywords: List[str] = field(default_factory=list)
    minhash: List[int] = field(default_factory=list)
    shade: str = "normal"
    dynamic_state: DynamicState = DynamicState.NORMAL
    luminosity: float = 1.0
    hyper_links: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=lambda: {
        "semantic_density": 0.0,
        "connection_entropy": 0.0,
        "temporal_stability": 1.0,
        "energy_level": 0.5,
        "novelty_score": 0.0
    })
    method: MethodMode = MethodMode.SK1_CHAOS
    ttl: int = 10
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    gravity: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.hyper_id is None:
            self.hyper_id = f"HYP_{self.id}"

    def to_dict(self):
        d = asdict(self)
        d["base_color"] = self.base_color.value
        d["dynamic_state"] = self.dynamic_state.value
        d["method"] = self.method.value
        if isinstance(d["compressed_content"], bytes):
            d["compressed_content"] = d["compressed_content"].hex()
        return d

    @classmethod
    def from_dict(cls, data: dict):
        if "base_color" in data: data["base_color"] = MemoryColor(data["base_color"])
        if "dynamic_state" in data: data["dynamic_state"] = DynamicState(data["dynamic_state"])
        if "method" in data: data["method"] = MethodMode(data["method"])
        if "compressed_content" in data and isinstance(data["compressed_content"], str):
            data["compressed_content"] = bytes.fromhex(data["compressed_content"])
        return cls(**data)
