"""
SK Engine Models - QuantumBlock
The fundamental unit of memory in EvoPyramid OS.
"""
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from .config import MemoryColor, DynamicState

@dataclass
class QuantumBlock:
    """
    Universal memory quantum with intellectual metadata.
    """
    id: str
    content: str
    color: MemoryColor = MemoryColor.WHITE
    state: DynamicState = DynamicState.NORMAL
    
    # Cognitive Metadata
    tags: Set[str] = field(default_factory=set)
    gravity: float = 1.0  # Connectivity weight
    links: Set[str] = field(default_factory=set)  # Connected IDs
    
    # Technical Metadata
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())
    updated_at: float = field(default_factory=lambda: datetime.now().timestamp())
    minhash: List[int] = field(default_factory=list)
    version: int = 1
    
    # Extensible payload for sector-specific data
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary"""
        d = asdict(self)
        d['color'] = self.color.value
        d['state'] = self.state.value
        d['tags'] = list(self.tags)
        d['links'] = list(self.links)
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuantumBlock':
        """Create from dictionary"""
        data['color'] = MemoryColor(data.get('color', 'white'))
        data['state'] = DynamicState(data.get('state', 'normal'))
        data['tags'] = set(data.get('tags', []))
        data['links'] = set(data.get('links', []))
        return cls(**data)
