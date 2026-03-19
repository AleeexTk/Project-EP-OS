import hashlib
import random
from typing import List, Set, Dict, Tuple
from collections import defaultdict
from .config import SystemConfig

class MinHash:
    """Deterministic MinHash generator for consistent semantic signatures."""
    def __init__(self, count: int = SystemConfig.MINHASH_COUNT, seed: int = SystemConfig.MINHASH_SEED):
        self.count = count
        self.prime = SystemConfig.MINHASH_PRIME
        self.hash_funcs = self._generate_hash_functions(seed)

    def _generate_hash_functions(self, seed: int) -> List[Tuple[int, int]]:
        rand = random.Random(seed)
        return [(rand.randint(1, self.prime - 1), rand.randint(0, self.prime - 1)) for _ in range(self.count)]

    def create_signature(self, text: str) -> List[int]:
        shingles = self._get_shingles(text)
        if not shingles:
            return [0] * self.count
        
        signature = [self.prime] * self.count
        for s in shingles:
            s_hash = int(hashlib.md5(s.encode('utf-8')).hexdigest(), 16) % self.prime
            for i, (a, b) in enumerate(self.hash_funcs):
                val = (a * s_hash + b) % self.prime
                if val < signature[i]:
                    signature[i] = val
        return signature

    def _get_shingles(self, text: str, k: int = 1) -> Set[str]:
        text = text.lower().strip()
        words = text.split()
        if len(words) < k:
            return set(words)
        return {" ".join(words[i:i+k]) for i in range(len(words)-k+1)}

class LSH:
    """Locality Sensitive Hashing index for bucket-based neighbor lookup."""
    def __init__(self, bands: int = SystemConfig.LSH_BANDS, rows: int = SystemConfig.LSH_ROWS):
        self.bands = bands
        self.rows = rows
        self.buckets: List[Dict[int, Set[str]]] = [defaultdict(set) for _ in range(bands)]

    def add_to_index(self, doc_id: str, signature: List[int]):
        for b in range(self.bands):
            band = tuple(signature[b*self.rows : (b+1)*self.rows])
            band_hash = hash(band)
            self.buckets[b][band_hash].add(doc_id)

    def query(self, signature: List[int]) -> Set[str]:
        candidates = set()
        for b in range(self.bands):
            band = tuple(signature[b*self.rows : (b+1)*self.rows])
            band_hash = hash(band)
            if band_hash in self.buckets[b]:
                candidates.update(self.buckets[b][band_hash])
        return candidates
