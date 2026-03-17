"""
CortexMemory - The cognitive engine of SK.
Handles associative memory, LSH indexing, and atomic persistence.
"""
import asyncio
import json
import logging
import shutil
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from .config import SystemConfig, MemoryColor, DynamicState
from .models import QuantumBlock
from .lsh import MinHash, LSH

logger = logging.getLogger("SK_Engine")

class CortexMemory:
    """
    Main memory interface for the SK engine.
    Orchestrates QuantumBlocks, MinHash, and LSH.
    """
    def __init__(self, data_dir: Path = SystemConfig.DATA_DIR):
        self.data_dir = data_dir
        self.blocks_dir = data_dir / "blocks"
        self.index_file = data_dir / "index.json"
        
        # In-memory structures
        self.blocks: Dict[str, QuantumBlock] = {}
        self.minhash = MinHash()
        self.lsh = LSH()
        
        self.lock = asyncio.Lock()
        self._ensure_dirs()

    def _ensure_dirs(self):
        """Create necessary directories if they don't exist"""
        self.blocks_dir.mkdir(parents=True, exist_ok=True)
        SystemConfig.BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    async def add_block(self, block: QuantumBlock, persist: bool = True):
        """Add a memory block to the engine"""
        async with self.lock:
            # Generate minhash if missing
            if not block.minhash:
                block.minhash = self.minhash.create_signature(block.content)
            
            self.blocks[block.id] = block
            self.lsh.add_to_index(block.id, block.minhash)
            
            if persist:
                await self._save_block_atomic(block)

    async def _save_block_atomic(self, block: QuantumBlock):
        """Save a single block using atomic write (write to temp then rename)"""
        block_path = self.blocks_dir / f"{block.id}.json"
        
        # Create temp file in the same directory to ensure same-volume rename
        fd, temp_path = tempfile.mkstemp(dir=str(self.blocks_dir), suffix=".tmp")
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(block.to_dict(), f, indent=2, ensure_ascii=False)
            
            # Atomic swap
            if os.path.exists(block_path):
                os.replace(temp_path, block_path)
            else:
                os.rename(temp_path, block_path)
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            logger.error(f"Atomic save failed for block {block.id}: {e}")

    async def find_similar(self, content: str, threshold: float = SystemConfig.SK1_SIMILARITY_THRESHOLD) -> List[QuantumBlock]:
        """Find related blocks using LSH and Jaccard similarity"""
        query_sig = self.minhash.create_signature(content)
        candidates = self.lsh.query(query_sig)
        
        results = []
        for block_id in candidates:
            block = self.blocks.get(block_id)
            if not block:
                continue
            
            # Calculate Jaccard similarity
            sim = self._jaccard_similarity(query_sig, block.minhash)
            if sim >= threshold:
                results.append((block, sim))
        
        # Sort by similarity descending
        results.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in results]

    @staticmethod
    def _jaccard_similarity(sig1: List[int], sig2: List[int]) -> float:
        """Estimate Jaccard similarity from MinHash signatures"""
        if not sig1 or not sig2 or len(sig1) != len(sig2):
            return 0.0
        matches = sum(1 for a, b in zip(sig1, sig2) if a == b)
        return matches / len(sig1)

    async def save_index(self):
        """Persist the LSH index (rebuildable, but cacheable)"""
        async with self.lock:
            index_data = {
                "lsh_buckets": [ {str(k): v for k, v in b.items()} for b in self.lsh.buckets ]
            }
            write_atomic(self.index_file, index_data)

    async def load_all(self):
        """Load all persistent memory blocks from disk"""
        async with self.lock:
            if not self.blocks_dir.exists():
                return
                
            for file_path in self.blocks_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        block = QuantumBlock.from_dict(data)
                        self.blocks[block.id] = block
                        self.lsh.add_to_index(block.id, block.minhash)
                except Exception as e:
                    logger.error(f"Failed to load block {file_path}: {e}")
            
            logger.info(f"Loaded {len(self.blocks)} memory blocks.")

def write_atomic(file_path: Path, data: Any):
    """General utility for atomic JSON writes"""
    fd, temp_path = tempfile.mkstemp(dir=str(file_path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(temp_path, file_path)
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise e
