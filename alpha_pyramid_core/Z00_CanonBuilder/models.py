from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class Sector(str, Enum):
    SPINE = "spine"
    PURPLE = "purple"
    RED = "red"
    GOLD = "gold"
    GREEN = "green"
    SANDBOX = "sandbox"

@dataclass(frozen=True)
class Coordinates:
    x: int
    y: int
    z: int

@dataclass
class Manifest:
    module_id: str
    coords: Coordinates
    sector: Sector
    layer_kind: str
    provides: List[str]
    consumes: List[str]
    egress_capabilities: List[str]
    allowed_calls: List[str]
    file_path: Optional[str] = None
