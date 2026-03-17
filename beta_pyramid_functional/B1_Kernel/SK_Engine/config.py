"""
SK Engine Configuration & Enums
Harmonized for EvoPyramid OS Integration.
"""
from enum import Enum
from pathlib import Path

class SystemConfig:
    """Centralized configuration for the SK Engine"""
    # MinHash parameters
    MINHASH_PRIME = 2**31 - 1
    MINHASH_SEED = 42
    MINHASH_COUNT = 128
    
    # LSH параметры - adjusted for sensitive architectural discovery
    LSH_BANDS = 64
    LSH_ROWS = 2
    
    # Storage settings - Unified with Project Structure
    DATA_DIR = Path("state/sk_data")
    BACKUP_DIR = Path("state/sk_backups")
    
    # Thresholds
    SK1_SIMILARITY_THRESHOLD = 0.1
    SK2_SIMILARITY_THRESHOLD = 0.15
    SK3_CLUSTER_THRESHOLD = 0.3

class MemoryColor(Enum):
    """
    DNA Colors for Information Fragments.
    Aligned with EvoPyramid Sectors.
    """
    YELLOW = "yellow"      # Concepts (GOLD sector affinity)
    RED = "red"            # Conflicts (RED sector affinity)
    GREEN = "green"        # Strategies (GREEN sector affinity)
    BLUE = "blue"          # Data/Meta (SPINE/BLUE affinity)
    ORANGE = "orange"      # Cache/Transit
    VIOLET = "violet"      # Synthesis (PURPLE sector affinity)
    WHITE = "white"        # Axioms/Core principles

class DynamicState(Enum):
    """Value/Relevance states"""
    NORMAL = "normal"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"

class MethodMode(Enum):
    """Operational modes for EvoMethod_SK"""
    SK1_CHAOS = "sk1"      # Fast, raw processing
    SK2_FUNDAMENTAL = "sk2" # Deep memory storage
    SK3_SYNTHESIS = "sk3"  # Cognitive synthesis
