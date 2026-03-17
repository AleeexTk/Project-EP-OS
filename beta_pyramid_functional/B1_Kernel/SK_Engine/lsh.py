"""
MinHash & LSH (Locality Sensitive Hashing)
Core algorithms for associative memory and similarity detection.
"""
import hashlib
import random
import re
from typing import List, Set, Tuple, Dict
from .config import SystemConfig

class MinHash:
    """MinHash signature generator for text content"""
    
    def __init__(self, num_perm: int = SystemConfig.MINHASH_COUNT, seed: int = SystemConfig.MINHASH_SEED):
        self.num_perm = num_perm
        self.seed = seed
        self.permutations = self._generate_permutations()

    def _generate_permutations(self) -> List[Tuple[int, int]]:
        """Generate static permutation parameters for consistency"""
        perms = []
        gen = random.Random(self.seed)
        for _ in range(self.num_perm):
            a = gen.randint(1, SystemConfig.MINHASH_PRIME - 1)
            b = gen.randint(0, SystemConfig.MINHASH_PRIME - 1)
            perms.append((a, b))
        return perms

    @staticmethod
    def get_shingles(text: str, k: int = 1) -> Set[str]:
        """Extract k-gram shingles from text (default k=1 for better node recall)"""
        text = re.sub(r'[^\w\s]', '', text.lower())
        tokens = text.split()
        if len(tokens) < k:
            return {text} if text else set()
        return {" ".join(tokens[i:i+k]) for i in range(len(tokens) - k + 1)}

    def create_signature(self, text: str) -> List[int]:
        """Generate MinHash signature for a piece of text"""
        shingles = self.get_shingles(text)
        if not shingles:
            return [SystemConfig.MINHASH_PRIME] * self.num_perm
            
        shingle_hashes = [int(hashlib.sha256(s.encode()).hexdigest(), 16) % SystemConfig.MINHASH_PRIME 
                         for s in shingles]
        
        signature = []
        for a, b in self.permutations:
            min_val = SystemConfig.MINHASH_PRIME
            for sh_hash in shingle_hashes:
                perm_hash = (a * sh_hash + b) % SystemConfig.MINHASH_PRIME
                if perm_hash < min_val:
                    min_val = perm_hash
            signature.append(min_val)
        return signature

class LSH:
    """Locality Sensitive Hashing for efficient similarity indexing"""
    
    def __init__(self, bands: int = SystemConfig.LSH_BANDS, rows: int = SystemConfig.LSH_ROWS):
        self.bands = bands
        self.rows = rows
        # bucket: { band_index: { hash_value: [id1, id2, ...] } }
        self.buckets: List[Dict[int, List[str]]] = [{} for _ in range(bands)]

    def add_to_index(self, item_id: str, signature: List[int]):
        """Add an item signature to the LSH index"""
        for i in range(self.bands):
            band = signature[i * self.rows : (i + 1) * self.rows]
            band_hash = hash(tuple(band))
            if band_hash not in self.buckets[i]:
                self.buckets[i][band_hash] = []
            if item_id not in self.buckets[i][band_hash]:
                self.buckets[i][band_hash].append(item_id)

    def query(self, signature: List[int]) -> Set[str]:
        """Query for candidate IDs that share at least one band bucket"""
        candidates = set()
        for i in range(self.bands):
            band = signature[i * self.rows : (i + 1) * self.rows]
            band_hash = hash(tuple(band))
            if band_hash in self.buckets[i]:
                candidates.update(self.buckets[i][band_hash])
        return candidates

    def remove_from_index(self, item_id: str):
        """Remove item from all buckets"""
        for band_dict in self.buckets:
            for bucket_list in band_dict.values():
                if item_id in bucket_list:
                    bucket_list.remove(item_id)
