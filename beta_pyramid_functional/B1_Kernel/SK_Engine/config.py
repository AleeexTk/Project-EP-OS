from enum import Enum
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path

class MemoryColor(str, Enum):
    YELLOW = "yellow"
    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    ORANGE = "orange"
    VIOLET = "violet"
    WHITE = "white"

class DynamicState(str, Enum):
    NORMAL = "normal"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"

class MethodMode(str, Enum):
    SK1_CHAOS = "sk1"
    SK2_FUNDAMENTAL = "sk2"
    SK3_SYNTHESIS = "sk3"

class SystemConfig:
    MINHASH_PRIME = 2**31 - 1
    MINHASH_SEED = 42
    MINHASH_COUNT = 128
    LSH_BANDS = 16
    LSH_ROWS = 8
    DATA_DIR = Path("state/evo_data")
    BACKUP_DIR = Path("state/evo_backups")
    SK1_SIMILARITY_THRESHOLD = 0.1
    SK3_CLUSTER_THRESHOLD = 0.3
