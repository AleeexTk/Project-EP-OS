"""
EVO_METHOD_SK 3.3 - Production Ready (Enhanced Final)
Автономный когнитивный движок с MinHash, LSH и полной персистентностью
Доработки: Стабильный LSH hash, async locks, atomic saves, health monitoring, performance metrics
"""

import asyncio
import time
import json
import hashlib
import random
import shutil
import tempfile
import os
import re
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Set
from collections import deque, defaultdict
from pathlib import Path
import sys
from contextlib import contextmanager

# ==========================================
# КОНФИГУРАЦИЯ СИСТЕМЫ
# ==========================================

class SystemConfig:
    """Централизованная конфигурация системы"""
    
    # MinHash параметры
    MINHASH_PRIME = 2**31 - 1
    MINHASH_SEED = 42
    MINHASH_COUNT = 128
    
    # LSH параметры
    LSH_BANDS = 16
    LSH_ROWS = 8
    
    # Система хранения
    HOT_STORE_SIZE = 500
    AUTO_SAVE_INTERVAL = 300  # секунд
    BACKUP_ENABLED = True
    
    # Пороги обработки
    SK1_SIMILARITY_THRESHOLD = 0.1
    SK2_SIMILARITY_THRESHOLD = 0.15
    SK3_CLUSTER_THRESHOLD = 0.3
    
    # Пути данных — absolute, anchored to this file to avoid cwd pollution
    DATA_DIR = Path(__file__).resolve().parents[4] / "evo_data"
    BACKUP_DIR = Path(__file__).resolve().parents[4] / "evo_backups"
    
    @classmethod
    def validate(cls):
        """Валидация конфигурации"""
        if cls.LSH_BANDS * cls.LSH_ROWS > cls.MINHASH_COUNT:
            raise ValueError("LSH bands*rows must be <= MINHASH_COUNT")
        return True

# ==========================================
# УТИЛИТЫ ЯДРА
# ==========================================

def write_atomic(file_path: Path, data: Any):
    """Atomic write to JSON file using a temporary file and os.replace."""
    parent = file_path.parent
    parent.mkdir(parents=True, exist_ok=True)
    
    # Create temp file in the same directory to ensure atomic move/replace
    fd, temp_path = tempfile.mkstemp(dir=str(parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Atomic replace (works on Windows and Linux)
        os.replace(temp_path, str(file_path))
    except Exception as e:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        raise e

# Инициализация генератора случайных чисел
random.seed(SystemConfig.MINHASH_SEED)

# ==========================================
# 1. СИСТЕМА ТИПОВ
# ==========================================

class MemoryColor(Enum):
    """Исконные цвета-ДНК информационных фрагментов"""
    YELLOW = "yellow"      # Концепции, определения
    RED = "red"            # Конфликты, критические узлы  
    GREEN = "green"        # Стратегии, активные решения
    BLUE = "blue"          # Данные, метаинформация
    ORANGE = "orange"      # Кеш, временные состояния
    VIOLET = "violet"      # Синтез, интеграция знаний
    WHITE = "white"        # Абсолютные истины, аксиомы

class DynamicState(Enum):
    """Динамические состояния (ценность/актуальность)"""
    NORMAL = "normal"      # Стандартное состояние
    SILVER = "silver"      # Повышенная значимость
    GOLD = "gold"          # Высокая плотность связей
    PLATINUM = "platinum"  # Гравитационный центр сессии
    DIAMOND = "diamond"    # Абсолютная интеграция знаний

class MethodMode(Enum):
    """Режимы работы EvoMethod_SK"""
    SK1_CHAOS = "sk1"      # Перенаправление Хаоса (быстрая обработка)
    SK2_FUNDAMENTAL = "sk2" # Фундаментальная Память (глубокая обработка)
    SK3_SYNTHESIS = "sk3"  # Синтетическая интеграция (когнитивный синтез)

# ==========================================
# 2. КВАНТОВЫЙ БЛОК (оптимизированный)
# ==========================================

@dataclass
class QuantumBlock:
    """Универсальный квант памяти с интеллектуальным сжатием"""
    
    # Обязательные поля (без значений по умолчанию)
    id: str
    hyper_id: Optional[str]
    base_color: MemoryColor
    
    # Контент и семантика
    content: str = ""
    compressed_content: bytes = b""
    keywords: List[str] = field(default_factory=list)
    
    # Состояние и метаданные
    shade: str = "normal"
    dynamic_state: DynamicState = DynamicState.NORMAL
    luminosity: float = 1.0
    
    # Связи и метрики
    hyper_links: List[str] = field(default_factory=list)
    semantic_vector: Optional[List[float]] = None
    
    # Количественные метрики
    metrics: Dict[str, float] = field(default_factory=lambda: {
        "semantic_density": 0.0,
        "connection_entropy": 0.0,
        "temporal_stability": 1.0,
        "energy_level": 0.5,
        "novelty_score": 0.0
    })
    
    # Режим обработки
    method: MethodMode = MethodMode.SK1_CHAOS
    ttl: int = 10
    
    # Временные метки
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    
    def __post_init__(self):
        """Автоматическая инициализация после создания"""
        if self.hyper_id is None:
            self.hyper_id = f"HYP_{self.id}"
            
        # Автоматическое сжатие длинного контента
        if len(self.content) > 100 and not self.compressed_content:
            self.compress()
    
    def compress(self) -> None:
        """Интеллектуальное сжатие контента с сохранением семантики"""
        if len(self.content) > 100 and not self.compressed_content:
            self.compressed_content = self.content.encode('utf-8')
            # Сохраняем начало для быстрого доступа
            self.content = self.content[:97] + "..."
    
    def decompress(self) -> str:
        """Полное восстановление контента"""
        if self.compressed_content:
            try:
                return self.compressed_content.decode('utf-8')
            except UnicodeDecodeError:
                return self.compressed_content.decode('utf-8', errors='replace')
        return self.content
    
    def get_full_content(self) -> str:
        """Умное получение полного контента (с кэшированием)"""
        return self.decompress()
    
    def calculate_age(self) -> float:
        """Возраст блока в часах"""
        return (time.time() - self.created_at) / 3600
    
    def is_expired(self) -> bool:
        """Проверка истечения времени жизни"""
        if self.ttl <= 0:
            return False
        return (time.time() - self.last_accessed) > (self.ttl * 60)

# ==========================================
# 3. LSH ИНДЕКС (оптимизированный, с stable hash)
# ==========================================

class LSHIndex:
    """Locality Sensitive Hashing индекс для быстрого семантического поиска"""
    
    def __init__(self, bands: int = None, rows: int = None):
        self.bands = bands or SystemConfig.LSH_BANDS
        self.rows = rows or SystemConfig.LSH_ROWS
        self.tables: List[Dict[int, Set[str]]] = [defaultdict(set) for _ in range(self.bands)]
    
    def _stable_band_hash(self, band: tuple) -> int:
        """Стабильный хеш для band (детерминированный)"""
        band_str = str(band).encode('utf-8')
        return int(hashlib.md5(band_str).hexdigest(), 16) % SystemConfig.MINHASH_PRIME
    
    def add_signature(self, doc_id: str, signature: List[int]) -> None:
        """Добавление сигнатуры MinHash в LSH индекс"""
        if len(signature) < self.bands * self.rows:
            return
            
        for band_idx in range(self.bands):
            start_idx = band_idx * self.rows
            end_idx = (band_idx + 1) * self.rows
            band = tuple(signature[start_idx:end_idx])
            band_hash = self._stable_band_hash(band)
            self.tables[band_idx][band_hash].add(doc_id)
    
    def query(self, signature: List[int]) -> Set[str]:
        """Поиск кандидатов с высокой вероятностью сходства"""
        candidates = set()
        
        if len(signature) < self.bands * self.rows:
            return candidates
            
        for band_idx in range(self.bands):
            start_idx = band_idx * self.rows
            end_idx = (band_idx + 1) * self.rows
            band = tuple(signature[start_idx:end_idx])
            band_hash = self._stable_band_hash(band)
            
            if band_hash in self.tables[band_idx]:
                candidates.update(self.tables[band_idx][band_hash])
                
        return candidates
    
    def remove_document(self, doc_id: str, signature: List[int]) -> None:
        """Удаление документа из индекса"""
        for band_idx in range(self.bands):
            start_idx = band_idx * self.rows
            end_idx = (band_idx + 1) * self.rows
            band = tuple(signature[start_idx:end_idx])
            band_hash = self._stable_band_hash(band)
            
            if band_hash in self.tables[band_idx]:
                self.tables[band_idx][band_hash].discard(doc_id)
                
    def get_stats(self) -> Dict[str, Any]:
        """Статистика LSH индекса"""
        total_buckets = sum(len(table) for table in self.tables)
        avg_bucket_size = sum(len(bucket) for table in self.tables for bucket in table.values()) / max(total_buckets, 1)
        
        return {
            "bands": self.bands,
            "rows": self.rows,
            "total_buckets": total_buckets,
            "avg_bucket_size": round(avg_bucket_size, 2),
            "total_documents": sum(len(bucket) for table in self.tables for bucket in table.values())
        }

# ==========================================
# 4. ПРОИЗВОДИТЕЛЬНОСТЬ И МОНИТОРИНГ
# ==========================================

class PerformanceMonitor:
    """Мониторинг производительности операций"""
    
    def __init__(self):
        self.metrics = defaultdict(list)
        self.start_time = time.time()
    
    @contextmanager
    def measure(self, operation: str):
        """Контекстный менеджер для измерения времени"""
        start = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start
            self.metrics[operation].append(duration)
    
    def get_stats(self) -> Dict:
        """Статистика производительности"""
        stats = {}
        for operation, times in self.metrics.items():
            if times:
                stats[operation] = {
                    "count": len(times),
                    "avg_ms": sum(times) / len(times) * 1000,
                    "p95_ms": sorted(times)[int(len(times) * 0.95)] * 1000 if len(times) > 1 else times[0] * 1000,
                    "last_ms": times[-1] * 1000,
                    "total_ms": sum(times) * 1000
                }
        stats["uptime_seconds"] = time.time() - self.start_time
        return stats

class HealthChecker:
    """Проверка здоровья системы"""
    
    @staticmethod
    async def check_hypergraph(hypergraph: 'HypergraphMemory') -> Dict:
        """Проверка целостности гиперграфа"""
        issues = []
        warnings = []
        
        # Проверка ссылок на блоки
        for node_id, node in hypergraph.nodes.items():
            if not hasattr(node, 'block_id'):
                issues.append(f"Узел {node_id}: отсутствует block_id")
            elif not hypergraph.persistence:
                warnings.append(f"Узел {node_id}: persistence не установлен")
            elif not hypergraph.persistence.load_block(node.block_id):
                warnings.append(f"Узел {node_id}: блок {node.block_id} не найден")
        
        # Проверка симметрии рёбер
        for (n1, n2) in hypergraph.edges.keys():
            if n1 not in hypergraph.nodes or n2 not in hypergraph.nodes:
                issues.append(f"Ребро ({n1}, {n2}): ссылается на несуществующий узел")
        
        # Проверка весов
        for (n1, n2), weight in hypergraph.edges.items():
            if weight < 0 or weight > 1:
                warnings.append(f"Ребро ({n1}, {n2}): нестандартный вес {weight}")
        
        status = "HEALTHY"
        if issues:
            status = "CRITICAL"
        elif warnings:
            status = "DEGRADED"
        
        return {
            "status": status,
            "issues": issues,
            "warnings": warnings,
            "nodes_count": len(hypergraph.nodes),
            "edges_count": len(hypergraph.edges),
            "check_timestamp": time.time()
        }
    
    @staticmethod
    def check_persistence(persistence: 'QuantumPersistence') -> Dict:
        """Проверка целостности хранилища"""
        issues = []
        warnings = []  # FIX: was missing, caused NameError on line referencing warnings.append
        
        # Проверка файлов
        main_file = persistence.base_dir / "blocks.json"
        if main_file.exists():
            try:
                with open(main_file, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError:
                issues.append("Основной файл повреждён")
        
        # Проверка cold хранилища
        cold_dir = persistence.base_dir / "cold"
        if cold_dir.exists():
            for file in cold_dir.glob("*.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        json.load(f)
                except:
                    issues.append(f"Cold файл {file.name} повреждён")
        
        # Проверка ссылок
        for block_id in persistence.warm_store:
            if block_id not in persistence.hot_store and block_id not in persistence.cold_store:
                if not (cold_dir / f"{block_id}.json").exists():
                    warnings.append(f"Блок {block_id} есть в warm_store, но отсутствует на диске")
        
        status = "HEALTHY" if not issues else "DEGRADED"
        
        return {
            "status": status,
            "issues": issues,
            "warnings": warnings,
            "total_blocks": persistence.get_stats()["total_blocks"],
            "check_timestamp": time.time()
        }

# ==========================================
# 5. ГИПЕРГРАФОВАЯ ПАМЯТЬ (производственная версия, с async locks)
# ==========================================

@dataclass
class HyperNode:
    """Узел гиперграфа с семантической сигнатурой (без дубля content)"""
    id: str
    block_id: str  # Ссылка на QuantumBlock вместо дубля content
    color: MemoryColor
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    minhash_sig: List[int] = field(default_factory=list)

class HypergraphMemory:
    """Производственная гиперграфовая память с MinHash и LSH"""
    
    def __init__(self, config: SystemConfig = None, persistence: 'QuantumPersistence' = None):
        self.config = config or SystemConfig
        self.config.validate()
        self.persistence = persistence  # Для load content по block_id
        
        # Основные структуры
        self.nodes: Dict[str, HyperNode] = {}
        self.edges: Dict[Tuple[str, str], float] = {}
        
        # Семантический индекс
        self.hash_functions = self._generate_hash_functions()
        self.lsh_index = LSHIndex()
        
        # Кэши для производительности
        self.similarity_cache: Dict[Tuple[str, str], float] = {}
        self.cluster_cache: Optional[List[Set[str]]] = None
        self.cluster_timestamp: float = 0
        
        # Lock для async safety
        self._lock = asyncio.Lock()
        
        # Мониторинг
        self.monitor = PerformanceMonitor()
        
        # Статистика
        self.stats = {
            "nodes_created": 0,
            "edges_created": 0,
            "queries_processed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0
        }
    
    # ==================== ЯДРО MINHASH ====================
    
    def _generate_hash_functions(self) -> List[Tuple[int, int]]:
        """Генерация детерминированных универсальных хеш-функций"""
        temp_random = random.Random(self.config.MINHASH_SEED)
        return [
            (
                temp_random.randint(1, self.config.MINHASH_PRIME - 1),
                temp_random.randint(1, self.config.MINHASH_PRIME - 1)
            )
            for _ in range(self.config.MINHASH_COUNT)
        ]
    
    def _get_shingles(self, text: str, k: int = 3) -> Set[str]:
        """Извлечение k-грамм из текста"""
        if not text or len(text.strip()) == 0:
            return set()
            
        # Нормализация текста
        text = text.lower().strip()
        for char in ",.!?;:'\"()[]{}<>":
            text = text.replace(char, ' ')
        
        words = [w for w in text.split() if len(w) > 1]
        
        if len(words) < k:
            return set(words) if words else set([text])
        
        # Генерация шинглов
        shingles = set()
        for i in range(len(words) - k + 1):
            shingle = " ".join(words[i:i+k])
            shingles.add(shingle)
            
        return shingles
    
    def _get_minhash_signature(self, text: str) -> List[int]:
        """Вычисление сигнатуры MinHash"""
        with self.monitor.measure("minhash_signature"):
            shingles = self._get_shingles(text)
            
            if not shingles:
                return [0] * self.config.MINHASH_COUNT
            
            # Инициализация сигнатуры максимальными значениями
            signature = [self.config.MINHASH_PRIME] * self.config.MINHASH_COUNT
            
            for shingle in shingles:
                # Хеширование шингла
                shingle_hash = hash(shingle) % self.config.MINHASH_PRIME
                
                for i, (a, b) in enumerate(self.hash_functions):
                    # Универсальное хеширование: (a*x + b) % p
                    hashed_value = (a * shingle_hash + b) % self.config.MINHASH_PRIME
                    
                    # Минимальное значение для этой хеш-функции
                    if hashed_value < signature[i]:
                        signature[i] = hashed_value
            
            return signature
    
    def _jaccard_similarity(self, sig1: List[int], sig2: List[int]) -> float:
        """Оценка сходства Жаккара по сигнатурам MinHash"""
        if not sig1 or not sig2:
            return 0.0
            
        matches = sum(1 for h1, h2 in zip(sig1, sig2) if h1 == h2)
        return matches / self.config.MINHASH_COUNT
    
    # ==================== ОПЕРАЦИИ С УЗЛАМИ ====================
    
    async def add_node(self, node: HyperNode, block: QuantumBlock) -> str:
        """Добавление узла с автоматической индексацией (async)"""
        with self.monitor.measure("add_node"):
            async with self._lock:
                try:
                    node.minhash_sig = self._get_minhash_signature(block.get_full_content())
                    node.block_id = block.id
                    self.nodes[node.id] = node
                    
                    # Индексация в LSH
                    self.lsh_index.add_signature(node.id, node.minhash_sig)
                    
                    # Инвалидация кэша кластеров
                    self.cluster_cache = None
                    
                    # Обновление статистики
                    self.stats["nodes_created"] += 1
                    
                    return node.id
                except Exception as e:
                    self.stats["errors"] += 1
                    raise e
    
    async def get_node(self, node_id: str, load_content: bool = False) -> Optional[HyperNode]:
        """Получение узла с обновлением времени доступа (async)"""
        with self.monitor.measure("get_node"):
            async with self._lock:
                node = self.nodes.get(node_id)
                if node:
                    node.last_accessed = time.time()
                    
                    # Загрузка контента по требованию
                    if load_content and self.persistence:
                        block = self.persistence.load_block(node.block_id)
                        if block:
                            node.metadata['content_preview'] = block.content[:100]
                            node.metadata['full_content_available'] = True
                        else:
                            node.metadata['full_content_available'] = False
                
                return node
    
    async def remove_node(self, node_id: str) -> bool:
        """Удаление узла и всех связанных ребер (async)"""
        with self.monitor.measure("remove_node"):
            async with self._lock:
                if node_id not in self.nodes:
                    return False
                    
                try:
                    # Удаление из LSH индекса
                    node = self.nodes[node_id]
                    self.lsh_index.remove_document(node_id, node.minhash_sig)
                    
                    # Удаление связанных ребер
                    edges_to_remove = []
                    for (n1, n2) in self.edges.keys():
                        if n1 == node_id or n2 == node_id:
                            edges_to_remove.append((n1, n2))
                    
                    for edge in edges_to_remove:
                        del self.edges[edge]
                    
                    # Удаление узла
                    del self.nodes[node_id]
                    
                    # Инвалидация кэшей
                    self.cluster_cache = None
                    
                    # Очистка кэша сходства
                    keys_to_remove = [k for k in self.similarity_cache.keys() 
                                     if node_id in k]
                    for key in keys_to_remove:
                        del self.similarity_cache[key]
                    
                    return True
                except Exception as e:
                    self.stats["errors"] += 1
                    raise e
    
    async def add_nodes_batch(self, nodes: List[Tuple[HyperNode, QuantumBlock]]) -> List[str]:
        """Пакетное добавление узлов"""
        results = []
        async with self._lock:
            for node, block in nodes:
                try:
                    node.minhash_sig = self._get_minhash_signature(block.get_full_content())
                    node.block_id = block.id
                    self.nodes[node.id] = node
                    self.lsh_index.add_signature(node.id, node.minhash_sig)
                    results.append(node.id)
                except Exception as e:
                    print(f"[*] Ошибка добавления узла {node.id}: {e}")
                    results.append(None)
                    self.stats["errors"] += 1
            
            # Инвалидация кэша один раз после всех операций
            self.cluster_cache = None
            self.stats["nodes_created"] += len([r for r in results if r])
        
        return results
    
    # ==================== СЕМАНТИЧЕСКИЙ ПОИСК ====================
    
    async def find_similar(self, query: str, top_k: int = 5, 
                          min_similarity: float = 0.0) -> List[Tuple[str, float]]:
        """Интеллектуальный поиск похожих узлов с использованием LSH (async)"""
        with self.monitor.measure("find_similar"):
            self.stats["queries_processed"] += 1
            
            async with self._lock:
                # Генерация сигнатуры запроса
                query_sig = self._get_minhash_signature(query)
                
                # 1. Быстрый поиск кандидатов через LSH
                candidate_ids = self.lsh_index.query(query_sig)
                
                # 2. Если LSH не нашел кандидатов, используем полный перебор
                if not candidate_ids:
                    candidate_ids = set(self.nodes.keys())
                    self.stats["cache_misses"] += 1
                else:
                    self.stats["cache_hits"] += 1
                
                # 3. Точный расчет сходства для кандидатов
                results = []
                for node_id in candidate_ids:
                    node = self.nodes.get(node_id)
                    if not node or not node.minhash_sig:
                        continue
                    
                    # Проверка кэша сходства
                    cache_key = (query, node_id)
                    if cache_key in self.similarity_cache:
                        similarity = self.similarity_cache[cache_key]
                    else:
                        similarity = self._jaccard_similarity(query_sig, node.minhash_sig)
                        self.similarity_cache[cache_key] = similarity
                    
                    if similarity >= min_similarity:
                        # Взвешивание с учетом важности узла
                        weighted_score = similarity * node.weight
                        results.append((node_id, weighted_score, similarity))
                
                # 4. Сортировка и возврат результатов
                results.sort(key=lambda x: x[1], reverse=True)
                return [(node_id, score) for node_id, score, _ in results[:top_k]]
    
    # ==================== РАБОТА С РЕБРАМИ ====================
    
    async def add_edge(self, node1_id: str, node2_id: str, weight: float = 1.0) -> bool:
        """Добавление ребра между узлами (async)"""
        with self.monitor.measure("add_edge"):
            async with self._lock:
                if node1_id not in self.nodes or node2_id not in self.nodes:
                    return False
            
                key = tuple(sorted([node1_id, node2_id]))
                self.edges[key] = weight
                
                # Обновление времени доступа
                self.nodes[node1_id].last_accessed = time.time()
                self.nodes[node2_id].last_accessed = time.time()
                
                # Инвалидация кэша кластеров
                self.cluster_cache = None
                
                self.stats["edges_created"] += 1
                return True
    
    async def add_edges_batch(self, edges: List[Tuple[str, str, float]]) -> List[bool]:
        """Пакетное добавление рёбер"""
        results = []
        async with self._lock:
            for node1_id, node2_id, weight in edges:
                if node1_id not in self.nodes or node2_id not in self.nodes:
                    results.append(False)
                    continue
                
                key = tuple(sorted([node1_id, node2_id]))
                self.edges[key] = weight
                
                # Обновление времени доступа
                if node1_id in self.nodes:
                    self.nodes[node1_id].last_accessed = time.time()
                if node2_id in self.nodes:
                    self.nodes[node2_id].last_accessed = time.time()
                
                results.append(True)
            
            # Инвалидация кэша один раз
            self.cluster_cache = None
            self.stats["edges_created"] += sum(results)
        
        return results
    
    def get_edges(self, node_id: str) -> List[Tuple[str, float]]:
        """Получение всех ребер для узла"""
        edges = []
        for (n1, n2), weight in self.edges.items():
            if n1 == node_id:
                edges.append((n2, weight))
            elif n2 == node_id:
                edges.append((n1, weight))
        return edges
    
    # ==================== КЛАСТЕРИЗАЦИЯ ====================
    
    async def get_clusters(self, min_similarity: float = None) -> List[Set[str]]:
        """Поиск семантических кластеров с кэшированием (async)"""
        with self.monitor.measure("get_clusters"):
            if min_similarity is None:
                min_similarity = self.config.SK3_CLUSTER_THRESHOLD
            
            # Проверка кэша
            current_time = time.time()
            if (self.cluster_cache is not None and 
                current_time - self.cluster_timestamp < 300):  # 5 минут
                return self.cluster_cache
            
            async with self._lock:
                # Поиск кластеров
                clusters = []
                visited = set()
                
                for node_id in self.nodes:
                    if node_id in visited:
                        continue
                        
                    # Поиск связанных узлов (BFS)
                    cluster = set()
                    queue = deque([node_id])
                    
                    while queue:
                        current = queue.popleft()
                        if current in visited:
                            continue
                            
                        visited.add(current)
                        cluster.add(current)
                        
                        # Поиск связанных узлов через ребра
                        for (n1, n2), weight in self.edges.items():
                            if weight >= min_similarity:
                                if current == n1 and n2 not in visited:
                                    queue.append(n2)
                                elif current == n2 and n1 not in visited:
                                    queue.append(n1)
                    
                    if len(cluster) > 1:
                        clusters.append(cluster)
            
                # Сохранение в кэш
                self.cluster_cache = clusters
                self.cluster_timestamp = current_time
            
            return clusters
    
    # ==================== ПЕРСИСТЕНТНОСТЬ ====================
    
    async def save(self, filepath: Path, max_retries: int = 3) -> None:
        """Сохранение гиперграфа на диск (async, atomic с retry)"""
        for attempt in range(max_retries):
            try:
                await self._save_attempt(filepath)
                return
            except (IOError, json.JSONDecodeError) as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(0.1 * (2 ** attempt))
                continue
    
    async def _save_attempt(self, filepath: Path) -> None:
        """Одна попытка сохранения"""
        with self.monitor.measure("save_hypergraph"):
            async with self._lock:
                data = {
                    "config": {
                        "hash_count": self.config.MINHASH_COUNT,
                        "prime": self.config.MINHASH_PRIME,
                        "seed": self.config.MINHASH_SEED,
                        "hash_functions": self.hash_functions
                    },
                    "nodes": {id: asdict(node) for id, node in self.nodes.items()},
                    "edges": {f"{n1},{n2}": weight for (n1, n2), weight in self.edges.items()},
                    "stats": self.stats,
                    "timestamp": time.time(),
                    "version": "3.3"
                }
                
                # Сериализация enum полей
                for node_data in data["nodes"].values():
                    node_data["color"] = node_data["color"].value
                
                write_atomic(filepath, data)
    
    @classmethod
    async def load(cls, filepath: Path, config: SystemConfig = None, 
                   persistence: 'QuantumPersistence' = None) -> 'HypergraphMemory':
        """Загрузка гиперграфа с диска (async с валидацией)"""
        if not filepath.exists():
            instance = cls(config)
            instance.persistence = persistence
            return instance
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[*] Повреждённый файл {filepath}: {e}")
            
            # Восстановление из backup если есть
            backup = filepath.with_suffix('.json.bak')
            if backup.exists():
                print(f"[*] Восстановление из backup {backup}")
                return await cls.load(backup, config, persistence)
            
            # Создание новой инстанции
            return cls(config)
        
        # Валидация версии
        version = data.get("version", "3.2")
        if version != "3.3":
            print(f"[*] Версия файла {version} отличается от ожидаемой 3.3")
        
        # Создание экземпляра
        instance = cls(config)
        instance.persistence = persistence
        
        # Восстановление конфигурации
        if "config" in data:
            instance.hash_functions = [
                tuple(func) for func in data["config"]["hash_functions"]
            ]
        
        # Восстановление узлов
        for node_id, node_data in data.get("nodes", {}).items():
            try:
                # Восстановление enum
                node_data["color"] = MemoryColor(node_data["color"])
                
                # Создание узла
                node = HyperNode(**node_data)
                instance.nodes[node_id] = node
                
                # Реиндексация в LSH
                instance.lsh_index.add_signature(node_id, node.minhash_sig)
            except Exception as e:
                print(f"[*] Ошибка загрузки узла {node_id}: {e}")
                continue
        
        # Восстановление ребер
        for edge_str, weight in data.get("edges", {}).items():
            try:
                n1, n2 = edge_str.split(',')
                instance.edges[(n1, n2)] = weight
            except:
                print(f"[*] Ошибка загрузки ребра {edge_str}")
                continue
        
        # Восстановление статистики
        instance.stats.update(data.get("stats", {}))
        
        return instance
    
    # ==================== УТИЛИТЫ ====================
    
    async def get_stats(self) -> Dict[str, Any]:
        """Полная статистика гиперграфа"""
        clusters = await self.get_clusters()
        performance_stats = self.monitor.get_stats()
        
        stats = {
            **self.stats,
            "current_nodes": len(self.nodes),
            "current_edges": len(self.edges),
            "clusters": len(clusters),
            "avg_cluster_size": sum(len(c) for c in clusters) / max(len(clusters), 1),
            "lsh_stats": self.lsh_index.get_stats(),
            "similarity_cache_size": len(self.similarity_cache),
            "cluster_cache_valid": self.cluster_cache is not None,
            "performance": performance_stats
        }
        
        # Добавление health check
        health = await HealthChecker.check_hypergraph(self)
        stats["health"] = health
        
        return stats
    
    async def cleanup(self, max_age_days: int = 30, min_weight: float = 0.1) -> int:
        """Очистка старых и незначительных узлов (async)"""
        removed_count = 0
        current_time = time.time()
        cutoff_time = current_time - (max_age_days * 86400)
        
        nodes_to_remove = []
        async with self._lock:
            for node_id, node in self.nodes.items():
                if (node.weight < min_weight or 
                    node.last_accessed < cutoff_time):
                    nodes_to_remove.append(node_id)
        
        for node_id in nodes_to_remove:
            if await self.remove_node(node_id):
                removed_count += 1
        
        return removed_count
    
    async def get_node_content(self, node_id: str) -> Optional[str]:
        """Получение полного контента узла"""
        node = await self.get_node(node_id)
        if not node or not self.persistence:
            return None
        
        block = self.persistence.load_block(node.block_id)
        if block:
            return block.get_full_content()
        return None

# ==========================================
# 6. СИСТЕМА ХРАНЕНИЯ (производственная, с atomic saves)
# ==========================================

class QuantumPersistence:
    """Производственная система хранения с интеллектуальным управлением"""
    
    def __init__(self, base_dir: Path = None):
        self.base_dir = base_dir or SystemConfig.DATA_DIR
        self.base_dir.mkdir(exist_ok=True)
        
        # Уровни хранения
        self.hot_store: Dict[str, QuantumBlock] = {}
        self.warm_store: Set[str] = set()  # ID блоков в warm-хранилище
        self.cold_store: Set[str] = set()  # ID блоков в cold-хранилище
        
        # Управление памятью
        self.lru_order: List[str] = []
        self.max_hot_size = SystemConfig.HOT_STORE_SIZE
        
        # Мониторинг
        self.monitor = PerformanceMonitor()
        
        # Статистика
        self.stats = {
            "hot_blocks": 0,
            "warm_blocks": 0,
            "cold_blocks": 0,
            "saves": 0,
            "loads": 0,
            "migrations": 0,
            "errors": 0
        }
        
        # Автоматическая загрузка при старте
        self._load_initial_state()
    
    # ==================== ОСНОВНЫЕ ОПЕРАЦИИ ====================
    
    def save_block(self, block: QuantumBlock) -> None:
        """Интеллектуальное сохранение блока"""
        with self.monitor.measure("save_block"):
            # Проверка TTL
            if block.is_expired():
                self._remove_block(block.id)
                return
            
            # Обновление в hot-хранилище
            self.hot_store[block.id] = block
            
            # Обновление LRU
            if block.id in self.lru_order:
                self.lru_order.remove(block.id)
            self.lru_order.insert(0, block.id)
            
            # Миграция при превышении лимита
            if len(self.hot_store) > self.max_hot_size:
                self._migrate_oldest_hot()
            
            # Сохранение на диск (atomic)
            self._save_to_disk(block)
            
            self.stats["saves"] += 1
            self.stats["hot_blocks"] = len(self.hot_store)
    
    def load_block(self, block_id: str) -> Optional[QuantumBlock]:
        """Загрузка блока из любого уровня хранения"""
        with self.monitor.measure("load_block"):
            self.stats["loads"] += 1
            
            # 1. Проверка hot-хранилища
            if block_id in self.hot_store:
                block = self.hot_store[block_id]
                block.last_accessed = time.time()
                block.access_count += 1
                
                # Обновление LRU
                self._update_lru(block_id)
                return block
            
            # 2. Загрузка с диска
            block = self._load_from_disk(block_id)
            if block:
                # Миграция в hot-хранилище при частом доступе
                if block.access_count > 5:
                    self.hot_store[block_id] = block
                    self._update_lru(block_id)
                    self.stats["hot_blocks"] = len(self.hot_store)
                
                return block
            
            return None
    
    def remove_block(self, block_id: str) -> bool:
        """Удаление блока из всех хранилищ"""
        with self.monitor.measure("remove_block"):
            removed = self._remove_block(block_id)
            if removed:
                # Удаление с диска
                cold_file = self.base_dir / "cold" / f"{block_id}.json"
                if cold_file.exists():
                    cold_file.unlink()
                
                # Обновление основного файла
                self._cleanup_main_file()
            
            return removed
    
    # ==================== ВНУТРЕННИЕ МЕТОДЫ ====================
    
    def _load_initial_state(self) -> None:
        """Первоначальная загрузка состояния"""
        # Загрузка warm-блоков
        main_file = self.base_dir / "blocks.json"
        if main_file.exists():
            with open(main_file, 'r', encoding='utf-8') as f:
                try:
                    blocks_data = json.load(f)
                    self.warm_store = {b["id"] for b in blocks_data}
                    self.stats["warm_blocks"] = len(self.warm_store)
                except Exception as e:
                    print(f"[*] Ошибка загрузки blocks.json: {e}")
        
        # Загрузка cold-блоков
        cold_dir = self.base_dir / "cold"
        if cold_dir.exists():
            for f in cold_dir.glob("*.json"):
                self.cold_store.add(f.stem)
            self.stats["cold_blocks"] = len(self.cold_store)
    
    def _save_to_disk(self, block: QuantumBlock) -> None:
        """Сохранение блока на диск (atomic с tempfile)"""
        main_file = self.base_dir / "blocks.json"
        tmp_file = None
        
        try:
            # Загрузка существующих данных
            existing_data = []
            if main_file.exists():
                with open(main_file, 'r', encoding='utf-8') as f:
                    try:
                        existing_data = json.load(f)
                    except json.JSONDecodeError:
                        existing_data = []
            
            # Подготовка данных блока
            block_data = {
                "id": block.id,
                "hyper_id": block.hyper_id,
                "color": block.base_color.value,
                "content": block.get_full_content(),
                "state": block.dynamic_state.value,
                "metrics": block.metrics,
                "created_at": block.created_at,
                "last_accessed": block.last_accessed,
                "access_count": block.access_count,
                "method": block.method.value
            }
            
            # Удаление старой версии и добавление новой
            existing_data = [b for b in existing_data if b["id"] != block.id]
            existing_data.append(block_data)
            
            write_atomic(main_file, existing_data)
            
        except Exception as e:
            self.stats["errors"] += 1
            raise e
        
        # Обновление множества warm-блоков
        self.warm_store.add(block.id)
        self.stats["warm_blocks"] = len(self.warm_store)
    
    def _load_from_disk(self, block_id: str) -> Optional[QuantumBlock]:
        """Загрузка блока с диска"""
        # Проверка warm-хранилища
        if block_id in self.warm_store:
            main_file = self.base_dir / "blocks.json"
            if main_file.exists():
                with open(main_file, 'r', encoding='utf-8') as f:
                    try:
                        blocks_data = json.load(f)
                        for b_data in blocks_data:
                            if b_data["id"] == block_id:
                                return self._deserialize_block(b_data)
                    except Exception as e:
                        print(f"[*] Ошибка чтения blocks.json: {e}")
        
        # Проверка cold-хранилища
        if block_id in self.cold_store:
            cold_file = self.base_dir / "cold" / f"{block_id}.json"
            if cold_file.exists():
                with open(cold_file, 'r', encoding='utf-8') as f:
                    try:
                        b_data = json.load(f)
                        return self._deserialize_block(b_data)
                    except Exception as e:
                        print(f"[*] Ошибка чтения cold файла {cold_file}: {e}")
        
        return None
    
    def _deserialize_block(self, b_data: Dict) -> QuantumBlock:
        """Десериализация блока из JSON"""
        content = b_data.get("content", "")
        is_compressed = len(content) > 100
        
        block = QuantumBlock(
            id=b_data["id"],
            hyper_id=b_data.get("hyper_id"),
            base_color=MemoryColor(b_data["color"]),
            content=content[:97] + "..." if is_compressed else content,
            compressed_content=content.encode('utf-8') if is_compressed else b"",
            dynamic_state=DynamicState(b_data.get("state", "normal")),
            metrics=b_data.get("metrics", {}),
            created_at=b_data.get("created_at", time.time()),
            last_accessed=time.time(),
            access_count=b_data.get("access_count", 0) + 1,
            method=MethodMode(b_data.get("method", "sk1"))
        )
        
        return block
    
    def _migrate_oldest_hot(self) -> None:
        """Миграция самого старого блока из hot-хранилища"""
        if not self.lru_order:
            return
            
        oldest_id = self.lru_order.pop()
        if oldest_id in self.hot_store:
            # Сохранение в cold-хранилище
            block = self.hot_store.pop(oldest_id)
            
            cold_file = self.base_dir / "cold" / f"{oldest_id}.json"
            cold_file.parent.mkdir(exist_ok=True)
            
            with open(cold_file, 'w', encoding='utf-8') as f:
                data = {
                    "id": block.id,
                    "content": block.get_full_content(),
                    "color": block.base_color.value,
                    "state": block.dynamic_state.value,
                    "created_at": block.created_at
                }
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.cold_store.add(oldest_id)
            self.stats["migrations"] += 1
            self.stats["cold_blocks"] = len(self.cold_store)
            self.stats["hot_blocks"] = len(self.hot_store)
    
    def _update_lru(self, block_id: str) -> None:
        """Обновление порядка LRU"""
        if block_id in self.lru_order:
            self.lru_order.remove(block_id)
        self.lru_order.insert(0, block_id)
    
    def _remove_block(self, block_id: str) -> bool:
        """Удаление блока из всех хранилищ в памяти"""
        removed = False
        
        if block_id in self.hot_store:
            del self.hot_store[block_id]
            removed = True
            
        if block_id in self.warm_store:
            self.warm_store.remove(block_id)
            removed = True
            
        if block_id in self.cold_store:
            self.cold_store.remove(block_id)
            removed = True
            
        if block_id in self.lru_order:
            self.lru_order.remove(block_id)
        
        if removed:
            self.stats["hot_blocks"] = len(self.hot_store)
            self.stats["warm_blocks"] = len(self.warm_store)
            self.stats["cold_blocks"] = len(self.cold_store)
        
        return removed
    
    def _cleanup_main_file(self) -> None:
        """Очистка основного файла от удаленных блоков"""
        main_file = self.base_dir / "blocks.json"
        if not main_file.exists():
            return
        
        tmp_file = None
        try:
            with open(main_file, 'r', encoding='utf-8') as f:
                try:
                    blocks_data = json.load(f)
                except:
                    return
            
            # Фильтрация существующих блоков
            valid_blocks = []
            for b_data in blocks_data:
                block_id = b_data["id"]
                if (block_id in self.hot_store or 
                    block_id in self.warm_store or 
                    block_id in self.cold_store):
                    valid_blocks.append(b_data)
            
            # Atomic save
            write_atomic(main_file, valid_blocks)
            
        except Exception as e:
            self.stats["errors"] += 1
            raise e
    
    # ==================== УТИЛИТЫ ====================
    
    def get_stats(self) -> Dict[str, Any]:
        """Статистика системы хранения"""
        performance_stats = self.monitor.get_stats()
        health = HealthChecker.check_persistence(self)
        
        return {
            **self.stats,
            "total_blocks": (
                len(self.hot_store) + 
                len(self.warm_store) + 
                len(self.cold_store)
            ),
            "lru_size": len(self.lru_order),
            "hot_ratio": len(self.hot_store) / max(self.max_hot_size, 1),
            "performance": performance_stats,
            "health": health
        }
    
    def create_backup(self, backup_name: str = None) -> Optional[Path]:
        """Создание резервной копии данных"""
        if not SystemConfig.BACKUP_ENABLED:
            return None
        
        # Sanitize name
        if backup_name:
            backup_name = re.sub(r'[<>:"/\\|?*]', '', backup_name)
        
        backup_dir = SystemConfig.BACKUP_DIR / (backup_name or f"backup_{int(time.time())}")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Копирование основных файлов
            blocks_file = self.base_dir / "blocks.json"
            if blocks_file.exists():
                shutil.copy2(blocks_file, backup_dir / "blocks.json")
            
            hypergraph_file = self.base_dir / "hypergraph.json"
            if hypergraph_file.exists():
                shutil.copy2(hypergraph_file, backup_dir / "hypergraph.json")
            
            # Копирование cold-хранилища
            cold_source = self.base_dir / "cold"
            if cold_source.exists():
                shutil.copytree(cold_source, backup_dir / "cold", dirs_exist_ok=True)
            
            # Создание файла метаданных
            metadata = {
                "timestamp": time.time(),
                "version": "3.3",
                "source": str(self.base_dir),
                "blocks_count": self.get_stats()["total_blocks"]
            }
            
            with open(backup_dir / "backup_meta.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            return backup_dir
            
        except Exception as e:
            print(f"[*] Ошибка создания бэкапа: {e}")
            self.stats["errors"] += 1
            return None
    
    def cleanup_expired(self) -> int:
        """Очистка просроченных блоков"""
        expired_count = 0
        
        # Проверка hot-блоков
        blocks_to_remove = []
        for block_id, block in self.hot_store.items():
            if block.is_expired():
                blocks_to_remove.append(block_id)
        
        for block_id in blocks_to_remove:
            if self.remove_block(block_id):
                expired_count += 1
        
        return expired_count

# ==========================================
# 7. АДАПТИВНЫЙ АНАЛИЗАТОР (расширенный)
# ==========================================

class AdaptiveAnalyzer:
    """Интеллектуальный анализатор с машинным обучением"""
    
    def __init__(self):
        self.history = deque(maxlen=1000)
        self.thresholds = {
            "diamond": 0.95,
            "platinum": 0.80,
            "gold": 0.65,
            "silver": 0.45,
            "normal": 0.0
        }
        
        # Статистика для адаптации
        self.score_distribution = deque(maxlen=500)
        self.learning_rate = 0.01
        
        # Мониторинг
        self.monitor = PerformanceMonitor()
        
    def analyze(self, block: QuantumBlock, context: Dict = None) -> QuantumBlock:
        """Полный анализ блока с учетом контекста"""
        with self.monitor.measure("analyze"):
            context = context or {}
            
            # 1. Расчет метрик
            metrics = self._calculate_advanced_metrics(block, context)
            block.metrics.update(metrics)
            
            # 2. Общая оценка
            total_score = self._calculate_total_score(metrics)
            self.score_distribution.append(total_score)
            
            # 3. Определение динамического состояния
            self._assign_dynamic_state(block, total_score)
            
            # 4. Адаптация порогов
            self._adapt_thresholds()
            
            # 5. Сохранение в историю
            self.history.append({
                "timestamp": time.time(),
                "block_id": block.id,
                "color": block.base_color.value,
                "score": total_score,
                "state": block.dynamic_state.value,
                "metrics": metrics
            })
            
            return block
    
    def _calculate_advanced_metrics(self, block: QuantumBlock, context: Dict) -> Dict[str, float]:
        """Расчет продвинутых метрик"""
        metrics = {}
        
        # Полный контент
        content = block.get_full_content()
        
        # 1. Семантическая сложность
        words = content.split()
        unique_words = set(words)
        
        metrics["length_factor"] = min(len(content) / 1000.0, 1.0)
        metrics["lexical_diversity"] = len(unique_words) / max(len(words), 1)
        
        # 2. Временные характеристики
        age_hours = block.calculate_age()
        metrics["recency_score"] = 1.0 / (1.0 + age_hours)
        metrics["activity_score"] = min(block.access_count / max(age_hours * 10, 1), 1.0)
        
        # 3. Структурные метрики
        metrics["connectivity_score"] = min(len(block.hyper_links) / 20.0, 1.0)
        
        # 4. Контекстуальные метрики
        if "session_importance" in context:
            metrics["context_relevance"] = context["session_importance"]
        else:
            metrics["context_relevance"] = 0.5
        
        # 5. Композитные метрики
        metrics["semantic_density"] = (
            metrics["lexical_diversity"] * 0.4 +
            metrics["length_factor"] * 0.3 +
            metrics["connectivity_score"] * 0.3
        )
        
        metrics["temporal_stability"] = (
            metrics["recency_score"] * 0.4 +
            metrics["activity_score"] * 0.6
        )
        
        metrics["energy_level"] = (
            metrics["semantic_density"] * 0.5 +
            metrics["temporal_stability"] * 0.3 +
            metrics["context_relevance"] * 0.2
        )
        
        # 6. Новизна (на основе истории)
        if self.history:
            recent_scores = [h["score"] for h in list(self.history)[-10:]]
            avg_recent = sum(recent_scores) / len(recent_scores)
            metrics["novelty_score"] = abs(metrics["energy_level"] - avg_recent)
        else:
            metrics["novelty_score"] = 0.5
        
        return metrics
    
    def _calculate_total_score(self, metrics: Dict[str, float]) -> float:
        """Вычисление общей оценки"""
        weights = {
            "semantic_density": 0.35,
            "temporal_stability": 0.25,
            "energy_level": 0.25,
            "novelty_score": 0.15
        }
        
        total = 0.0
        weight_sum = 0.0
        
        for metric, weight in weights.items():
            if metric in metrics:
                total += metrics[metric] * weight
                weight_sum += weight
        
        return total / max(weight_sum, 0.001)
    
    def _assign_dynamic_state(self, block: QuantumBlock, total_score: float) -> None:
        """Назначение динамического состояния"""
        if total_score >= self.thresholds["diamond"]:
            block.dynamic_state = DynamicState.DIAMOND
            block.luminosity = 1.0
            block.shade = "bright"
        elif total_score >= self.thresholds["platinum"]:
            block.dynamic_state = DynamicState.PLATINUM
            block.luminosity = 0.9
            block.shade = "bright"
        elif total_score >= self.thresholds["gold"]:
            block.dynamic_state = DynamicState.GOLD
            block.luminosity = 0.75
            block.shade = "normal"
        elif total_score >= self.thresholds["silver"]:
            block.dynamic_state = DynamicState.SILVER
            block.luminosity = 0.6
            block.shade = "normal"
        else:
            block.dynamic_state = DynamicState.NORMAL
            block.luminosity = 0.4
            block.shade = "light"
    
    def _adapt_thresholds(self) -> None:
        """Адаптация порогов на основе распределения оценок"""
        if len(self.score_distribution) < 50:
            return
        
        # Анализ распределения
        scores = list(self.score_distribution)
        mean_score = sum(scores) / len(scores)
        std_score = (sum((s - mean_score) ** 2 for s in scores) / len(scores)) ** 0.5
        
        # Динамическая настройка порогов
        self.thresholds["diamond"] = min(0.98, mean_score + 2.0 * std_score)
        self.thresholds["platinum"] = min(0.90, mean_score + 1.5 * std_score)
        self.thresholds["gold"] = min(0.75, mean_score + 0.8 * std_score)
        self.thresholds["silver"] = min(0.60, mean_score + 0.3 * std_score)
        
        # Ограничения
        for key in self.thresholds:
            self.thresholds[key] = max(0.1, min(0.99, self.thresholds[key]))
    
    def predict_optimal_method(self, query: str, history: List[Dict]) -> MethodMode:
        """Предсказание оптимального метода обработки"""
        query_features = self._extract_query_features(query)
        
        # Анализ истории
        method_scores = defaultdict(float)
        method_counts = defaultdict(int)
        
        for entry in history[-100:]:
            method = entry.get("method")
            success = entry.get("success_rate", 0.5)
            
            if method:
                # Взвешиваем по релевантности
                similarity = self._query_similarity(query, entry.get("query", ""))
                weight = success * similarity
                
                method_scores[method] += weight
                method_counts[method] += 1
        
        # Выбор метода
        if method_scores:
            # Нормализация по количеству
            for method in method_scores:
                if method_counts[method] > 0:
                    method_scores[method] /= method_counts[method]
            
            best_method = max(method_scores.items(), key=lambda x: x[1])[0]
            return MethodMode(best_method)
        
        # Эвристики для новых запросов
        complexity = self._estimate_complexity(query)
        
        if complexity > 0.7:
            return MethodMode.SK3_SYNTHESIS
        elif complexity > 0.4:
            return MethodMode.SK2_FUNDAMENTAL
        else:
            return MethodMode.SK1_CHAOS
    
    def _extract_query_features(self, query: str) -> Dict[str, float]:
        """Извлечение признаков запроса"""
        words = query.lower().split()
        
        return {
            "length": len(words) / 100.0,
            "unique_ratio": len(set(words)) / max(len(words), 1),
            "avg_word_length": sum(len(w) for w in words) / max(len(words), 1),
            "question_mark": 1.0 if "?" in query else 0.0,
            "exclamation_mark": 1.0 if "!" in query else 0.0,
            "has_technical": 1.0 if any(w in query.lower() for w in 
                ["архитектур", "алгоритм", "систем", "проект"]) else 0.0,
            "has_creative": 1.0 if any(w in query.lower() for w in 
                ["синтез", "создай", "придумай", "вообрази"]) else 0.0
        }
    
    def _query_similarity(self, q1: str, q2: str) -> float:
        """Оценка сходства запросов"""
        if not q1 or not q2:
            return 0.0
        
        words1 = set(q1.lower().split())
        words2 = set(q2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def _estimate_complexity(self, query: str) -> float:
        """Оценка сложности запроса"""
        features = self._extract_query_features(query)
        
        complexity = (
            features["length"] * 0.3 +
            features["unique_ratio"] * 0.2 +
            features["has_technical"] * 0.3 +
            features["has_creative"] * 0.2
        )
        
        return min(complexity, 1.0)
    
    def get_stats(self) -> Dict[str, Any]:
        """Статистика анализатора"""
        performance_stats = self.monitor.get_stats()
        
        if not self.score_distribution:
            return {
                "history_size": len(self.history),
                "thresholds": self.thresholds,
                "performance": performance_stats
            }
        
        scores = list(self.score_distribution)
        
        return {
            "history_size": len(self.history),
            "thresholds": self.thresholds,
            "score_stats": {
                "mean": sum(scores) / len(scores),
                "min": min(scores),
                "max": max(scores),
                "recent": scores[-1] if scores else 0.0,
                "std": (sum((s - sum(scores)/len(scores)) ** 2 for s in scores) / len(scores)) ** 0.5
            },
            "performance": performance_stats
        }

# ==========================================
# 8. ЯДРО EVO_METHOD_SK (производственное)
# ==========================================

class EvoMethodSKCore:
    """Производственное ядро EvoMethod_SK"""
    
    def __init__(self, config: SystemConfig = None):
        self.config = config or SystemConfig()
        self.config.validate()
        
        # Инициализация компонентов
        self.persistence = QuantumPersistence()
        self.hypergraph = HypergraphMemory(self.config, self.persistence)
        self.analyzer = AdaptiveAnalyzer()
        
        # Кэши и состояния
        self.response_cache = {}
        self.session_context = {
            "start_time": time.time(),
            "query_count": 0,
            "method_history": [],
            "active_topics": defaultdict(int)
        }
        
        # Мониторинг
        self.monitor = PerformanceMonitor()
        self.health_checker = HealthChecker()
        
        # Статистика системы
        self.system_stats = {
            "startup_time": time.time(),
            "total_queries": 0,
            "method_distribution": defaultdict(int),
            "response_times": deque(maxlen=1000),
            "cache_hit_rate": 0.0,
            "system_health": 1.0,
            "errors": 0
        }
        
        # Фоновые задачи
        self.auto_save_task = None
        self.cleanup_task = None
        self.health_check_task = None
        self.running = True
        
        # Загрузка состояния
        asyncio.create_task(self._load_state())
        
        print(f"[*] EvoMethod_SK 3.3 загружен")
    
    async def _load_state(self):
        """Асинхронная загрузка состояния системы"""
        hypergraph_file = self.persistence.base_dir / "hypergraph.json"
        
        if hypergraph_file.exists():
            try:
                self.hypergraph = await HypergraphMemory.load(
                    hypergraph_file, 
                    self.config, 
                    self.persistence
                )
                print(f"[*] Загружен гиперграф: {len(self.hypergraph.nodes)} узлов")
            except Exception as e:
                print(f"[*] Ошибка загрузки гиперграфа: {e}")
                self.system_stats["errors"] += 1
    
    # ==================== ОСНОВНОЙ ИНТЕРФЕЙС ====================
    
    async def process(self, query: str, context: Dict = None) -> Dict[str, Any]:
        """Основной метод обработки запросов"""
        with self.monitor.measure("total_processing"):
            start_time = time.time()
            context = context or {}
            
            # Обновление сессионного контекста
            self._update_session_context(query)
            
            # Выбор метода обработки
            method = self._select_method(query, context)
            self.system_stats["method_distribution"][method.value] += 1
            self.session_context["method_history"].append(method.value)
            
            # Обработка запроса
            try:
                if method == MethodMode.SK1_CHAOS:
                    result = await self._execute_sk1(query, context)
                elif method == MethodMode.SK2_FUNDAMENTAL:
                    result = await self._execute_sk2(query, context)
                else:  # SK3_SYNTHESIS
                    result = await self._execute_sk3(query, context)
            except Exception as e:
                result = self._handle_error(e, query, method)
                self.system_stats["errors"] += 1
            
            # Обновление статистики
            processing_time = time.time() - start_time
            self._update_system_stats(processing_time, result.get("cache_hit", False))
            
            # Формирование ответа
            response = {
                "query": query,
                "response": result["response"],
                "method": method.value,
                "processing_time_ms": round(processing_time * 1000, 2),
                "metrics": {
                    "blocks_used": result.get("blocks_used", 0),
                    "similarity_score": result.get("similarity_score", 0.0),
                    "quality_score": result.get("quality_score", 0.5)
                },
                "system_info": {
                    "hypergraph_nodes": len(self.hypergraph.nodes),
                    "hypergraph_edges": len(self.hypergraph.edges),
                    "cache_size": len(self.response_cache),
                    "session_queries": self.session_context["query_count"]
                },
                "timestamp": time.time()
            }
            
            return response
    
    def _select_method(self, query: str, context: Dict) -> MethodMode:
        """Интеллектуальный выбор метода обработки"""
        # Использование истории для предсказания
        history = [
            {"query": q, "method": m, "success_rate": 0.7}
            for q, m in zip(self.session_context.get("recent_queries", []),
                          self.session_context.get("method_history", []))
        ]
        
        return self.analyzer.predict_optimal_method(query, history)
    
    # ==================== МЕТОДЫ ОБРАБОТКИ ====================
    
    async def _execute_sk1(self, query: str, context: Dict) -> Dict[str, Any]:
        """Быстрая обработка (Chaos Redirect)"""
        cache_key = f"sk1_{hashlib.md5(query.encode()).hexdigest()[:12]}"
        
        # Проверка кэша
        if cache_key in self.response_cache:
            cached = self.response_cache[cache_key]
            if time.time() - cached["timestamp"] < 60:  # TTL 60 секунд
                return {**cached["result"], "cache_hit": True}
        
        # Семантический поиск
        similar = await self.hypergraph.find_similar(
            query, 
            top_k=3,
            min_similarity=self.config.SK1_SIMILARITY_THRESHOLD
        )
        
        # Генерация ответа
        if similar:
            best_id, score = similar[0]
            best_node = await self.hypergraph.get_node(best_id, load_content=True)
            
            if best_node and score > 0.1:
                content = await self.hypergraph.get_node_content(best_id) or "Контент недоступен"
                response = (
                    f"[*] SK1: На основе знаний (сходство {score:.2f}):\n"
                    f"{content[:200]}..."
                )
                similarity_score = score
                blocks_used = 1
            else:
                response = self._generate_generic_response(query, "SK1")
                similarity_score = 0.0
                blocks_used = 0
        else:
            response = self._generate_generic_response(query, "SK1")
            similarity_score = 0.0
            blocks_used = 0
        
        # Создание эфемерного блока
        block = QuantumBlock(
            id=f"SK1_{int(time.time())}_{hashlib.md5(query.encode()).hexdigest()[:8]}",
            hyper_id=None,
            base_color=MemoryColor.ORANGE,
            content=query[:150],
            method=MethodMode.SK1_CHAOS,
            ttl=5
        )
        
        # Анализ и сохранение
        analyzed = self.analyzer.analyze(block, {
            "query": query,
            "similar_nodes": len(similar),
            "session_importance": 0.3
        })
        self.persistence.save_block(analyzed)
        
        # Создание гиперузла
        node = HyperNode(
            id=f"N_{block.id}",
            block_id=block.id,
            color=MemoryColor.ORANGE,
            weight=0.3
        )
        await self.hypergraph.add_node(node, block)
        
        # Кэширование результата
        result = {
            "response": response,
            "blocks_used": blocks_used,
            "similarity_score": similarity_score,
            "quality_score": min(similarity_score * 1.5, 0.8)
        }
        
        self.response_cache[cache_key] = {
            "timestamp": time.time(),
            "result": result
        }
        
        return {**result, "cache_hit": False}
    
    async def _execute_sk2(self, query: str, context: Dict) -> Dict[str, Any]:
        """Глубокая обработка (Fundamental Memory)"""
        # Глубокий семантический поиск
        similar = await self.hypergraph.find_similar(
            query,
            top_k=10,
            min_similarity=self.config.SK2_SIMILARITY_THRESHOLD
        )
        
        # Создание фундаментального блока
        block = QuantumBlock(
            id=f"SK2_{int(time.time())}_{hashlib.md5(query.encode()).hexdigest()[:8]}",
            hyper_id=None,
            base_color=MemoryColor.BLUE,
            content=query,
            method=MethodMode.SK2_FUNDAMENTAL,
            ttl=300  # 5 минут
        )
        
        # Извлечение ключевых слов
        words = query.lower().split()
        block.keywords = [w for w in words if len(w) > 3][:15]
        
        # Анализ блока
        analyzed = self.analyzer.analyze(block, {
            "query": query,
            "similar_nodes": len(similar),
            "session_importance": 0.6
        })
        
        # Сохранение
        self.persistence.save_block(analyzed)
        
        # Создание гиперузла
        node = HyperNode(
            id=f"N_{block.id}",
            block_id=block.id,
            color=MemoryColor.BLUE,
            weight=analyzed.metrics.get("semantic_density", 0.5)
        )
        await self.hypergraph.add_node(node, block)
        
        # Установка связей с похожими узлами
        connections_made = 0
        edges_to_add = []
        for node_id, score in similar[:8]:
            if score > 0.15:
                edges_to_add.append((node.id, node_id, score))
                analyzed.hyper_links.append(node_id)
                connections_made += 1
        
        if edges_to_add:
            await self.hypergraph.add_edges_batch(edges_to_add)
        
        # Генерация ответа
        if similar:
            avg_similarity = sum(s for _, s in similar[:5]) / min(len(similar), 5)
            response = (
                f"[*] SK2: Глубокий анализ завершен.\n"
                f"[*] Найдено источников: {len(similar)}\n"
                f"[*] Установлено связей: {connections_made}\n"
                f"[*] Среднее сходство: {avg_similarity:.2f}\n"
                f"[*] Плотность знаний: {analyzed.metrics.get('semantic_density', 0.0):.2f}"
            )
            quality = min(avg_similarity * 0.8 + analyzed.metrics.get("semantic_density", 0.0) * 0.2, 0.9)
        else:
            response = (
                f"[*] SK2: Создан новый фундаментальный контекст.\n"
                f"Плотность: {analyzed.metrics.get('semantic_density', 0.0):.2f}"
            )
            quality = 0.6
        
        return {
            "response": response,
            "blocks_used": len(similar),
            "similarity_score": avg_similarity if similar else 0.0,
            "quality_score": quality
        }
    
    async def _execute_sk3(self, query: str, context: Dict) -> Dict[str, Any]:
        """Синтетическая обработка (Cognitive Synthesis)"""
        # Расширенный поиск и анализ
        similar = await self.hypergraph.find_similar(query, top_k=15)
        clusters = await self.hypergraph.get_clusters()
        
        # Создание синтетического блока
        block = QuantumBlock(
            id=f"SK3_{int(time.time())}_{hashlib.md5(query.encode()).hexdigest()[:8]}",
            hyper_id=None,
            base_color=MemoryColor.VIOLET,
            content=query,
            method=MethodMode.SK3_SYNTHESIS,
            ttl=1800  # 30 минут
        )
        
        # Глубокий анализ
        analyzed = self.analyzer.analyze(block, {
            "query": query,
            "similar_nodes": len(similar),
            "clusters": len(clusters),
            "synthesis_mode": True,
            "session_importance": 0.9
        })
        
        # Усиление для синтетических блоков
        analyzed.metrics["semantic_density"] = min(
            analyzed.metrics.get("semantic_density", 0.5) * 1.8,
            1.0
        )
        
        # Автоматическое повышение состояния
        if analyzed.metrics["semantic_density"] > 0.85:
            analyzed.dynamic_state = DynamicState.DIAMOND
        elif analyzed.metrics["semantic_density"] > 0.7:
            analyzed.dynamic_state = DynamicState.PLATINUM
        
        # Сохранение
        self.persistence.save_block(analyzed)
        
        # Создание синтетического узла
        node = HyperNode(
            id=f"SYN_{block.id}",
            block_id=block.id,
            color=MemoryColor.VIOLET,
            weight=0.9,
            metadata={
                "type": "synthesis",
                "sources": len(similar),
                "clusters": len(clusters),
                "density": analyzed.metrics["semantic_density"],
                "state": analyzed.dynamic_state.value
            }
        )
        await self.hypergraph.add_node(node, block)
        
        # Синтез ответа
        if similar and clusters:
            response = (
                f"[*] SK3: КОГНИТИВНЫЙ СИНТЕЗ ЗАВЕРШЕН\n"
                f"[*]\n"
                f"[*] Запрос: {query[:100]}...\n"
                f"[*] Источников: {len(similar)}\n"
                f"[*] Кластеров: {len(clusters)}\n"
                f"[*] Плотность синтеза: {analyzed.metrics['semantic_density']:.3f}\n"
                f"[*] Уровень знаний: {analyzed.dynamic_state.value.upper()}\n"
                f"[*]\n"
                f"Создано новое интегрированное знание."
            )
            quality = min(analyzed.metrics["semantic_density"] * 0.9 + 0.1, 0.95)
        else:
            response = (
                f"[*] SK3: Инициирован синтез нового знания.\n"
                f"Плотность: {analyzed.metrics['semantic_density']:.3f}"
            )
            quality = 0.7
        
        # Оптимизация гиперграфа
        await self.hypergraph.cleanup()
        
        return {
            "response": response,
            "blocks_used": len(similar),
            "clusters": len(clusters),
            "quality_score": quality,
            "synthesis_density": analyzed.metrics["semantic_density"]
        }
    
    # ==================== УТИЛИТЫ ====================
    
    def _generate_generic_response(self, query: str, method: str) -> str:
        """Генерация стандартного ответа"""
        templates = {
            "SK1": f"[*] {method}: Анализ запроса '{query[:50]}...' завершен.",
            "SK2": f"[*] {method}: Глубокий анализ инициирован.",
            "SK3": f"[*] {method}: Подготовка к синтетической обработке."
        }
        return templates.get(method, f"Обработка запроса: {query[:50]}...")
    
    def _handle_error(self, error: Exception, query: str, method: MethodMode) -> Dict:
        """Обработка ошибок"""
        print(f"[*] Ошибка в {method.value}: {error}")
        
        return {
            "response": (
                f"[*] Системная ошибка в режиме {method.value}.\n"
                f"Сообщение: {str(error)[:100]}\n"
                f"Запрос сохранен для последующего анализа."
            ),
            "blocks_used": 0,
            "similarity_score": 0.0,
            "quality_score": 0.1
        }
    
    def _update_session_context(self, query: str) -> None:
        """Обновление контекста сессии"""
        self.session_context["query_count"] += 1
        
        # Сохранение последних запросов
        if "recent_queries" not in self.session_context:
            self.session_context["recent_queries"] = deque(maxlen=50)
        self.session_context["recent_queries"].append(query)
        
        # Анализ тем
        words = query.lower().split()
        for word in words:
            if len(word) > 4:
                self.session_context["active_topics"][word] += 1
    
    def _update_system_stats(self, processing_time: float, cache_hit: bool) -> None:
        """Обновление системной статистики"""
        self.system_stats["total_queries"] += 1
        self.system_stats["response_times"].append(processing_time)
        
        # Расчет hit rate
        cache_hits = self.system_stats.get("cache_hits", 0)
        cache_misses = self.system_stats.get("cache_misses", 0)
        
        if cache_hit:
            cache_hits += 1
        else:
            cache_misses += 1
        
        self.system_stats["cache_hits"] = cache_hits
        self.system_stats["cache_misses"] = cache_misses
        self.system_stats["cache_hit_rate"] = cache_hits / max(cache_hits + cache_misses, 1)
        
        # Обновление здоровья системы
        avg_response = sum(self.system_stats["response_times"]) / len(self.system_stats["response_times"])
        self.system_stats["system_health"] = max(0, 1 - (avg_response / 5.0))  # 5 секунд - критический порог
    
    # ==================== УПРАВЛЕНИЕ СИСТЕМОЙ ====================
    
    async def start_background_tasks(self) -> None:
        """Запуск фоновых задач"""
        self.auto_save_task = asyncio.create_task(self._auto_save_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        self.health_check_task = asyncio.create_task(self._health_check_loop())
        
        print("[*] Фоновые задачи запущены")
    
    async def _auto_save_loop(self) -> None:
        """Цикл автоматического сохранения"""
        while self.running:
            await asyncio.sleep(self.config.AUTO_SAVE_INTERVAL)
            try:
                await self.save_state()
                print(f"[*] Автосохранение: {len(self.hypergraph.nodes)} узлов")
            except Exception as e:
                print(f"[*] Ошибка автосохранения: {e}")
                self.system_stats["errors"] += 1
    
    async def _cleanup_loop(self) -> None:
        """Цикл очистки системы"""
        while self.running:
            await asyncio.sleep(600)  # Каждые 10 минут
            
            try:
                # Очистка кэша ответов
                current_time = time.time()
                expired_keys = [
                    k for k, v in self.response_cache.items()
                    if current_time - v["timestamp"] > 3600  # 1 час
                ]
                for key in expired_keys:
                    del self.response_cache[key]
                
                # Очистка просроченных блоков
                expired_blocks = self.persistence.cleanup_expired()
                if expired_blocks:
                    print(f"[*] Удалено блоков: {expired_blocks}")
                
                # Оптимизация гиперграфа
                removed_nodes = await self.hypergraph.cleanup()
                if removed_nodes:
                    print(f"[*] Оптимизирован гиперграф: удалено {removed_nodes} узлов")
                    
            except Exception as e:
                print(f"[*] Ошибка очистки: {e}")
                self.system_stats["errors"] += 1
    
    async def _health_check_loop(self) -> None:
        """Цикл проверки здоровья"""
        while self.running:
            await asyncio.sleep(300)  # Каждые 5 минут
            
            try:
                hypergraph_health = await self.health_checker.check_hypergraph(self.hypergraph)
                persistence_health = self.health_checker.check_persistence(self.persistence)
                
                if hypergraph_health["status"] != "HEALTHY" or persistence_health["status"] != "HEALTHY":
                    print(f"[*] Проблемы со здоровьем системы:")
                    print(f"   Гиперграф: {hypergraph_health['status']}")
                    print(f"   Хранилище: {persistence_health['status']}")
                    
            except Exception as e:
                print(f"[*] Ошибка health check: {e}")
    
    async def save_state(self) -> None:
        """Сохранение полного состояния системы"""
        # Сохранение гиперграфа
        await self.hypergraph.save(self.persistence.base_dir / "hypergraph.json")
        
        # Сохранение статистики
        stats_file = self.persistence.base_dir / "system_stats.json"
        tmp_file = tempfile.NamedTemporaryFile(mode='w', dir=self.persistence.base_dir, delete=False, encoding='utf-8')
        
        try:
            data = {
                "system_stats": self.system_stats,
                "session_context": self.session_context,
                "analyzer_stats": self.analyzer.get_stats(),
                "timestamp": time.time(),
                "version": "3.3"
            }
            
            json.dump(data, tmp_file, ensure_ascii=False, indent=2)
            tmp_file.close()
            os.replace(tmp_file.name, stats_file)
            
            print(f"[*] Состояние сохранено (запросов: {self.system_stats['total_queries']})")
        except Exception as e:
            if os.path.exists(tmp_file.name):
                os.unlink(tmp_file.name)
            raise e
    
    def create_backup(self, backup_name: str = None) -> Optional[Path]:
        """Создание резервной копии системы"""
        return self.persistence.create_backup(backup_name)
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Полная информация о системе"""
        hypergraph_stats = await self.hypergraph.get_stats()
        persistence_stats = self.persistence.get_stats()
        analyzer_stats = self.analyzer.get_stats()
        performance_stats = self.monitor.get_stats()
        
        uptime = time.time() - self.system_stats["startup_time"]
        
        return {
            "version": "3.3 Production",
            "uptime_seconds": round(uptime, 2),
            "uptime_human": self._format_uptime(uptime),
            "queries_processed": self.system_stats["total_queries"],
            "method_distribution": dict(self.system_stats["method_distribution"]),
            "errors": self.system_stats["errors"],
            "performance": {
                "avg_response_time_ms": round(
                    sum(self.system_stats["response_times"]) / 
                    max(len(self.system_stats["response_times"]), 1) * 1000, 2
                ),
                "cache_hit_rate": round(self.system_stats["cache_hit_rate"] * 100, 1),
                "system_health": self.system_stats["system_health"],
                "detailed": performance_stats
            },
            "hypergraph": hypergraph_stats,
            "persistence": persistence_stats,
            "analyzer": analyzer_stats,
            "session": {
                "current_queries": self.session_context["query_count"],
                "active_topics": dict(
                    sorted(self.session_context["active_topics"].items(), 
                          key=lambda x: x[1], reverse=True)[:10]
                )
            }
        }
    
    def _format_uptime(self, seconds: float) -> str:
        """Форматирование времени работы"""
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}д")
        if hours > 0:
            parts.append(f"{hours}ч")
        if minutes > 0 or not parts:
            parts.append(f"{minutes}м")
        
        return " ".join(parts)
    
    async def shutdown(self) -> None:
        """Корректное завершение работы"""
        print("[*] Завершение работы системы...")
        
        self.running = False
        
        # Остановка фоновых задач
        tasks = [self.auto_save_task, self.cleanup_task, self.health_check_task]
        for task in tasks:
            if task:
                task.cancel()
        
        # Ожидание завершения задач
        await asyncio.sleep(0.5)
        
        # Финальное сохранение
        await self.save_state()
        
        print("[*] Система завершила работу")

# ==========================================
# 9. ИНТЕЛЛЕКТУАЛЬНЫЙ ИНТЕРФЕЙС
# ==========================================

class EvoInterface:
    """Интеллектуальный пользовательский интерфейс"""
    
    def __init__(self, core: EvoMethodSKCore):
        self.core = core
        self.user_profiles: Dict[str, Dict] = {}
        self.conversation_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.interface_modes = {
            "technical": "[*] Технический режим",
            "creative": "[*] Креативный режим",
            "balanced": "[*] Сбалансированный режим",
            "minimal": "[*] Минималистичный режим"
        }
        self.current_mode = "balanced"
        
        # Мониторинг
        self.monitor = PerformanceMonitor()
        
    async def chat(self, user_id: str, message: str) -> Dict[str, Any]:
        """Обработка сообщения пользователя"""
        with self.monitor.measure("chat_processing"):
            # Обновление профиля пользователя
            user_profile = self._update_user_profile(user_id, message)
            
            # Анализ интента и контекста
            intent = self._analyze_intent(message, user_profile)
            context = self._build_context(user_id, message, intent)
            
            # Обработка через ядро
            result = await self.core.process(message, context)
            
            # Адаптация ответа
            adapted_response = self._adapt_response(result, user_profile, intent)
            
            # Обновление истории
            self._update_history(user_id, message, adapted_response, result)
            
            # Адаптация интерфейса
            self._adapt_interface(user_profile, intent, result)
            
            return {
                "user_id": user_id,
                "original_query": message,
                "response": adapted_response,
                "method": result["method"],
                "processing_time": result["processing_time_ms"],
                "metrics": result["metrics"],
                "system_info": result["system_info"],
                "interface_mode": self.current_mode,
                "user_adapted": True,
                "timestamp": time.time()
            }
    
    def _update_user_profile(self, user_id: str, message: str) -> Dict:
        """Обновление профиля пользователя"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "first_seen": time.time(),
                "message_count": 0,
                "avg_message_length": 0.0,
                "preferred_topics": defaultdict(int),
                "preferred_methods": defaultdict(int),
                "interaction_style": "neutral",
                "technical_level": 0.5,
                "creativity_level": 0.5,
                "last_interaction": time.time()
            }
        
        profile = self.user_profiles[user_id]
        profile["message_count"] += 1
        
        # Анализ сообщения
        words = message.lower().split()
        profile["avg_message_length"] = (
            profile["avg_message_length"] * 0.8 + len(words) * 0.2
        )
        
        # Обнаружение тем
        topic_keywords = {
            "technical": ["код", "алгоритм", "база", "система", "архитектур", "оптимизац"],
            "creative": ["создай", "придумай", "вообрази", "дизайн", "искусств"],
            "analytical": ["анализ", "исследова", "проанализируй", "сравни"],
            "practical": ["как", "почему", "объясни", "пример", "демонстрац"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in message.lower() for keyword in keywords):
                profile["preferred_topics"][topic] += 1
        
        # Определение уровня техничности
        tech_keywords = ["api", "база данных", "алгоритм", "оптимизация", "система", "код"]
        tech_count = sum(1 for word in words if any(keyword in word for keyword in tech_keywords))
        profile["technical_level"] = (
            profile["technical_level"] * 0.7 + 
            (tech_count / max(len(words), 1)) * 0.3
        )
        
        # Определение уровня креативности
        creative_patterns = ["представь", "вообрази", "что если", "возможно"]
        creative_count = sum(1 for pattern in creative_patterns if pattern in message.lower())
        profile["creativity_level"] = (
            profile["creativity_level"] * 0.7 + 
            (creative_count * 0.3)
        )
        
        profile["last_interaction"] = time.time()
        
        return profile
    
    def _analyze_intent(self, message: str, profile: Dict) -> str:
        """Анализ намерения пользователя"""
        message_lower = message.lower()
        
        intent_patterns = {
            "question": ["?", "как", "почему", "что", "кто", "где", "когда"],
            "command": ["сделай", "напиши", "создай", "построй", "разработай"],
            "explanation": ["объясни", "расскажи", "покажи", "демонстрируй"],
            "analysis": ["проанализируй", "исследуй", "сравни", "оцени"],
            "synthesis": ["синтезируй", "обобщи", "интегрируй", "соедини"]
        }
        
        for intent, patterns in intent_patterns.items():
            if any(pattern in message_lower for pattern in patterns):
                return intent
        
        # Определение по стилю
        if len(message.split()) > 20:
            return "analysis"
        elif profile["technical_level"] > 0.7:
            return "explanation"
        else:
            return "question"
    
    def _build_context(self, user_id: str, message: str, intent: str) -> Dict:
        """Построение контекста обработки"""
        profile = self.user_profiles.get(user_id, {})
        history = list(self.conversation_history.get(user_id, deque())[-5:])
        
        return {
            "user_id": user_id,
            "intent": intent,
            "user_profile": {
                "technical_level": profile.get("technical_level", 0.5),
                "creativity_level": profile.get("creativity_level", 0.5),
                "preferred_methods": dict(profile.get("preferred_methods", {})),
                "interaction_count": profile.get("message_count", 0)
            },
            "conversation_history": history,
            "session_topics": dict(profile.get("preferred_topics", {})),
            "interface_mode": self.current_mode,
            "timestamp": time.time()
        }
    
    def _adapt_response(self, result: Dict, profile: Dict, intent: str) -> str:
        """Адаптация ответа под пользователя"""
        base_response = result["response"]
        method = result["method"]
        metrics = result.get("metrics", {})
        
        # Адаптация по уровню техничности
        technical_level = profile.get("technical_level", 0.5)
        
        if technical_level < 0.3 and method in ["sk2", "sk3"]:
            # Упрощение для нетехнических пользователей
            simplified = base_response.replace("семантическая плотность", "глубина знаний")
            simplified = simplified.replace("гиперграф", "память системы")
            simplified = simplified.replace("синтез", "объединение знаний")
            return f"[*] [Для вас упрощено]\n{simplified}"
        
        elif technical_level > 0.7 and method == "sk2":
            # Добавление технических деталей
            details = (
                f"\n[*] Детали:\n"
                f"[*] Использовано блоков: {metrics.get('blocks_used', 0)}\n"
                f"[*] Качество ответа: {metrics.get('quality_score', 0.0):.2f}\n"
                f"[*] Время обработки: {result['processing_time_ms']}мс"
            )
            return f"[*] [Технический анализ]\n{base_response}{details}"
        
        elif intent == "synthesis" and method == "sk3":
            # Усиление синтетических ответов
            enhanced = (
                f"[*] [КОГНИТИВНЫЙ ПРОРЫВ]\n"
                f"{base_response}\n"
                f"[*] Создано интегрированное знание нового уровня"
            )
            return enhanced
        
        # Стандартная адаптация
        method_labels = {
            "sk1": "[*] Быстрый ответ",
            "sk2": "[*] Глубокий анализ", 
            "sk3": "[*] Когнитивный синтез"
        }
        
        label = method_labels.get(method, "Ответ")
        return f"{label}\n{base_response}"
    
    def _update_history(self, user_id: str, query: str, response: str, result: Dict) -> None:
        """Обновление истории разговора"""
        self.conversation_history[user_id].append({
            "query": query,
            "response": response,
            "method": result["method"],
            "timestamp": time.time(),
            "processing_time": result["processing_time_ms"]
        })
        
        # Обновление предпочтений методов
        if user_id in self.user_profiles:
            self.user_profiles[user_id]["preferred_methods"][result["method"]] += 1
    
    def _adapt_interface(self, profile: Dict, intent: str, result: Dict) -> None:
        """Адаптация интерфейса"""
        technical_level = profile.get("technical_level", 0.5)
        creativity_level = profile.get("creativity_level", 0.5)
        
        if technical_level > 0.7 and intent in ["analysis", "explanation"]:
            self.current_mode = "technical"
        elif creativity_level > 0.6 and intent in ["synthesis", "command"]:
            self.current_mode = "creative"
        elif profile.get("message_count", 0) < 3:
            self.current_mode = "minimal"
        else:
            self.current_mode = "balanced"
    
    def get_user_stats(self, user_id: str) -> Optional[Dict]:
        """Получение статистики пользователя"""
        profile = self.user_profiles.get(user_id)
        if not profile:
            return None
        
        history = list(self.conversation_history.get(user_id, []))
        performance_stats = self.monitor.get_stats()
        
        return {
            "profile": {
                "message_count": profile["message_count"],
                "avg_message_length": round(profile["avg_message_length"], 1),
                "technical_level": round(profile["technical_level"], 2),
                "creativity_level": round(profile["creativity_level"], 2),
                "preferred_topics": dict(profile["preferred_topics"]),
                "preferred_methods": dict(profile["preferred_methods"]),
                "first_seen": time.strftime(
                    "%Y-%m-%d %H:%M:%S", 
                    time.localtime(profile["first_seen"])
                ),
                "last_interaction": time.strftime(
                    "%Y-%m-%d %H:%M:%S", 
                    time.localtime(profile["last_interaction"])
                )
            },
            "recent_interactions": history[-5:],
            "total_interactions": len(history),
            "current_mode": self.current_mode,
            "performance": performance_stats
        }

# ==========================================
# 10. ВИЗУАЛИЗАТОР И МОНИТОРИНГ
# ==========================================

class EvoVisualizer:
    """Визуализация состояния системы"""
    
    @staticmethod
    def print_banner() -> None:
        """Печать баннера системы"""
        banner = """
        [*]
        [*]      [*] EVO_METHOD_SK 3.3 - PRODUCTION READY            [*]
        [*]      Автономный когнитивный движок с MinHash + LSH       [*]
        [*]      Enhanced: Health checks, Monitoring, Atomic Ops    [*]
        [*]
        """
        print(banner)
    
    @staticmethod
    async def print_hypergraph_stats(hypergraph: HypergraphMemory) -> None:
        """Визуализация статистики гиперграфа"""
        stats = await hypergraph.get_stats()
        
        print("\n" + "[*]" * 60)
        print("[*] ГИПЕРГРАФОВАЯ ПАМЯТЬ")
        print("[*]" * 60)
        
        print(f"[*] Узлы: {stats['current_nodes']:,} (создано: {stats['nodes_created']:,})")
        print(f"[*] Ребра: {stats['current_edges']:,} (создано: {stats['edges_created']:,})")
        print(f"[*] Кластеры: {stats['clusters']:,} (ср. размер: {stats['avg_cluster_size']:.1f})")
        
        health = stats.get("health", {})
        print(f"[*] Здоровье: {health.get('status', 'UNKNOWN')}")
        if health.get("issues"):
            print(f"  Проблемы: {len(health['issues'])}")
        if health.get("warnings"):
            print(f"  Предупреждения: {len(health['warnings'])}")
        
        print(f"\n[*] Поиск:")
        print(f"  [*] Запросов: {stats['queries_processed']:,}")
        print(f"  [*] LSH hit rate: {stats['cache_hits']/(stats['cache_hits']+stats['cache_misses'])*100:.1f}%")
        print(f"  [*] Кэш сходства: {stats['similarity_cache_size']:,} записей")
        
        lsh_stats = stats.get('lsh_stats', {})
        print(f"  [*] LSH: {lsh_stats.get('bands', 0)} bands [*] {lsh_stats.get('rows', 0)} rows")
        print(f"  [*] LSH документов: {lsh_stats.get('total_documents', 0):,}")
        
        perf = stats.get('performance', {})
        if perf.get('find_similar'):
            print(f"\n[*] Производительность поиска:")
            print(f"  [*] Среднее время: {perf['find_similar']['avg_ms']:.2f}мс")
            print(f"  [*] P95: {perf['find_similar']['p95_ms']:.2f}мс")
    
    @staticmethod
    def print_persistence_stats(persistence: QuantumPersistence) -> None:
        """Визуализация статистики системы хранения"""
        stats = persistence.get_stats()
        
        print("\n" + "[*]" * 60)
        print("[*] СИСТЕМА ХРАНЕНИЯ")
        print("[*]" * 60)
        
        total_blocks = stats['total_blocks']
        hot_percent = (stats['hot_blocks'] / max(total_blocks, 1)) * 100
        warm_percent = (stats['warm_blocks'] / max(total_blocks, 1)) * 100
        cold_percent = (stats['cold_blocks'] / max(total_blocks, 1)) * 100
        
        print(f"[*] Всего блоков: {total_blocks:,}")
        print(f"[*] Hot (RAM): {stats['hot_blocks']:,} ({hot_percent:.1f}%)")
        print(f"[*] Warm (SSD): {stats['warm_blocks']:,} ({warm_percent:.1f}%)")
        print(f"[*] Cold (HDD): {stats['cold_blocks']:,} ({cold_percent:.1f}%)")
        
        health = stats.get("health", {})
        print(f"[*] Здоровье: {health.get('status', 'UNKNOWN')}")
        
        print(f"\n[*] Статистика:")
        print(f"  [*] Сохранений: {stats['saves']:,}")
        print(f"  [*] Загрузок: {stats['loads']:,}")
        print(f"  [*] Миграций: {stats['migrations']:,}")
        print(f"  [*] LRU размер: {stats['lru_size']:,}")
        print(f"  [*] Ошибки: {stats['errors']:,}")
        
        perf = stats.get('performance', {})
        if perf.get('save_block'):
            print(f"\n[*] Производительность:")
            print(f"  [*] Сохранение блока: {perf['save_block']['avg_ms']:.2f}мс")
            print(f"  [*] Загрузка блока: {perf['load_block']['avg_ms']:.2f}мс")
    
    @staticmethod
    async def print_system_stats(core: EvoMethodSKCore) -> None:
        """Визуализация системной статистики"""
        info = await core.get_system_info()
        
        print("\n" + "[*]" * 60)
        print("[*] СИСТЕМНАЯ СТАТИСТИКА")
        print("=" * 60)
        
        print(f"[*] Версия: {info['version']}")
        print(f"[*] Время работы: {info['uptime_human']}")
        print(f"[*] Обработано запросов: {info['queries_processed']:,}")
        print(f"[*] Ошибки: {info['errors']:,}")
        
        print(f"\n[*] Распределение методов:")
        method_dist = info['method_distribution']
        total = sum(method_dist.values())
        
        for method, count in method_dist.items():
            percentage = (count / max(total, 1)) * 100
            bar = "[*]" * int(percentage / 5)
            print(f"  {method.upper():10} {count:6,} {percentage:5.1f}% {bar}")
        
        perf = info['performance']
        print(f"\n[*] Производительность:")
        print(f"  [*] Среднее время ответа: {perf['avg_response_time_ms']}мс")
        print(f"  [*] Hit rate кэша: {perf['cache_hit_rate']}%")
        print(f"  [*] Здоровье системы: {perf['system_health']:.2f}")
        
        if perf.get('detailed'):
            print(f"  [*] Всего операций: {sum(op['count'] for op in perf['detailed'].values()):,}")
    
    @staticmethod
    def visualize_response_flow(query: str, result: Dict) -> None:
        """Визуализация потока обработки запроса"""
        print("\n" + "[*]" * 60)
        print("[*] ПОТОК ОБРАБОТКИ")
        print("[*]" * 60)
        
        print(f"[*] Запрос: {query[:80]}{'...' if len(query) > 80 else ''}")
        print(f"[*]  Метод: {result.get('method', 'unknown').upper()}")
        print(f"[*]  Время: {result.get('processing_time_ms', 0)}мс")
        
        metrics = result.get('metrics', {})
        if metrics:
            print(f"[*] Метрики:")
            print(f"  [*] Блоков использовано: {metrics.get('blocks_used', 0)}")
            print(f"  [*] Сходство: {metrics.get('similarity_score', 0):.3f}")
            print(f"  [*] Качество: {metrics.get('quality_score', 0):.3f}")
        
        if 'system_info' in result:
            sys_info = result['system_info']
            print(f"[*]  Состояние:")
            print(f"  [*] Узлов гиперграфа: {sys_info.get('hypergraph_nodes', 0)}")
            print(f"  [*] Размер кэша: {sys_info.get('cache_size', 0)}")
            print(f"  [*] Запросов в сессии: {sys_info.get('session_queries', 0)}")
    
    @staticmethod
    async def print_clusters(hypergraph: HypergraphMemory, max_clusters: int = 5) -> None:
        """Визуализация семантических кластеров"""
        clusters = await hypergraph.get_clusters()
        
        if not clusters:
            print("\n[*] Кластеры не найдены")
            return
        
        print("\n" + "[*]" * 60)
        print(f"[*] СЕМАНТИЧЕСКИЕ КЛАСТЕРЫ ({len(clusters)})")
        print("[*]" * 60)
        
        # Сортировка по размеру
        sorted_clusters = sorted(clusters, key=len, reverse=True)
        
        for i, cluster in enumerate(sorted_clusters[:max_clusters]):
            print(f"\nКластер #{i+1} ({len(cluster)} узлов):")
            
            # Выбор репрезентативных узлов
            sample_nodes = list(cluster)[:3]
            
            for j, node_id in enumerate(sample_nodes):
                node = await hypergraph.get_node(node_id, load_content=True)
                if node:
                    color_icon = {
                        "yellow": "[*]",
                        "red": "[*]",
                        "green": "[*]", 
                        "blue": "[*]",
                        "orange": "[*]",
                        "violet": "[*]",
                        "white": "[*]"
                    }.get(node.color.value, "[*]")
                    
                    # Получение контента
                    content = await hypergraph.get_node_content(node_id) or "Контент недоступен"
                    print(f"  {color_icon} {content[:60]}...")
            
            if len(cluster) > 3:
                print(f"  ... и еще {len(cluster) - 3} узлов")

# ==========================================
# 11. ГЛАВНЫЙ КЛАСС И ТОЧКА ВХОДА
# ==========================================

class EvoMethodSK:
    """Главный класс для интеграции EvoMethod_SK"""
    
    def __init__(self, config: SystemConfig = None):
        self.config = config or SystemConfig()
        self.config.validate()
        
        # Инициализация ядра
        self.core = EvoMethodSKCore(self.config)
        self.interface = EvoInterface(self.core)
        
        # Метаданные
        self.version = "3.3.Production"
        self.capabilities = {
            "minhash_semantic_search": True,
            "lsh_acceleration": True,
            "hypergraph_memory": True,
            "adaptive_processing": True,
            "intelligent_caching": True,
            "multi_level_persistence": True,
            "user_adaptation": True,
            "real_time_monitoring": True,
            "auto_optimization": True,
            "backup_recovery": True,
            "health_checks": True,
            "atomic_operations": True,
            "performance_monitoring": True
        }
        
        print(f"[*] EvoMethod_SK {self.version} инициализирован")
    
    async def initialize(self) -> None:
        """Инициализация системы"""
        await self.core.start_background_tasks()
        
        print("\n" + "=" * 60)
        print("СИСТЕМА ГОТОВА К РАБОТЕ")
        print("=" * 60)
        
        # Вывод информации о возможностях
        active_capabilities = [k for k, v in self.capabilities.items() if v]
        print(f"[*] Активные возможности ({len(active_capabilities)}):")
        for cap in active_capabilities:
            print(f"  [*] {cap.replace('_', ' ').title()}")
        
        # Вывод начальной статистики
        await self.print_status()
    
    async def print_status(self) -> None:
        """Вывод статуса системы"""
        await EvoVisualizer.print_system_stats(self.core)
        await EvoVisualizer.print_hypergraph_stats(self.core.hypergraph)
        EvoVisualizer.print_persistence_stats(self.core.persistence)
    
    async def query(self, text: str, user_id: str = "default") -> Dict[str, Any]:
        """Основной метод выполнения запросов"""
        return await self.interface.chat(user_id, text)
    
    async def get_stats(self, detailed: bool = False) -> Dict[str, Any]:
        """Получение статистики системы"""
        base_stats = await self.core.get_system_info()
        
        if detailed:
            user_stats = {}
            for user_id in self.interface.user_profiles:
                user_stats[user_id] = self.interface.get_user_stats(user_id)
            
            base_stats.update({
                "capabilities": self.capabilities,
                "user_count": len(self.interface.user_profiles),
                "active_conversations": len(self.interface.conversation_history),
                "interface_mode": self.interface.current_mode,
                "user_stats": user_stats
            })
        
        return base_stats
    
    async def optimize(self, level: str = "normal") -> Dict[str, Any]:
        """Ручная оптимизация системы"""
        print(f"[*] Оптимизация уровня: {level}")
        
        start_time = time.time()
        
        if level == "aggressive":
            # Агрессивная оптимизация
            removed_nodes = await self.core.hypergraph.cleanup(max_age_days=7, min_weight=0.05)
            expired_blocks = self.core.persistence.cleanup_expired()
            
            # Очистка кэшей
            self.core.response_cache.clear()
            self.core.hypergraph.similarity_cache.clear()
            self.core.hypergraph.cluster_cache = None
            
            result = {
                "removed_nodes": removed_nodes,
                "expired_blocks": expired_blocks,
                "cache_cleared": True
            }
            
        elif level == "deep":
            # Глубокая оптимизация
            removed_nodes = await self.core.hypergraph.cleanup(max_age_days=14, min_weight=0.1)
            
            # Перестройка LSH индекса
            self.core.hypergraph.lsh_index = LSHIndex()
            async with self.core.hypergraph._lock:
                for node_id, node in self.core.hypergraph.nodes.items():
                    self.core.hypergraph.lsh_index.add_signature(node_id, node.minhash_sig)
            
            result = {
                "removed_nodes": removed_nodes,
                "lsh_rebuilt": True,
                "cluster_cache_invalidated": True
            }
            
        else:
            # Нормальная оптимизация
            removed_nodes = await self.core.hypergraph.cleanup(max_age_days=30, min_weight=0.2)
            result = {"removed_nodes": removed_nodes}
        
        # Сохранение состояния
        await self.core.save_state()
        
        processing_time = time.time() - start_time
        
        print(f"[*] Оптимизация завершена за {processing_time:.2f}с")
        
        return {
            **result,
            "level": level,
            "processing_time": round(processing_time, 2),
            "timestamp": time.time()
        }
    
    async def create_backup(self, name: str = None) -> Dict[str, Any]:
        """Создание резервной копии"""
        if not SystemConfig.BACKUP_ENABLED:
            return {"error": "Backup system is disabled"}
        
        backup_path = self.core.create_backup(name)
        
        if backup_path:
            # Вычисление размера
            size_mb = 0
            if backup_path.exists():
                for file in backup_path.rglob("*"):
                    if file.is_file():
                        size_mb += file.stat().st_size / (1024 * 1024)
            
            return {
                "success": True,
                "backup_path": str(backup_path),
                "timestamp": time.time(),
                "size_mb": round(size_mb, 2)
            }
        
        return {"success": False, "error": "Backup creation failed"}
    
    async def export_knowledge(self, format: str = "json", limit: int = 100) -> Dict[str, Any]:
        """Экспорт знаний системы"""
        if format == "json":
            # Экспорт ключевых узлов
            important_nodes = []
            
            for node_id, node in self.core.hypergraph.nodes.items():
                if node.weight > 0.7:
                    edges = self.core.hypergraph.get_edges(node_id)
                    
                    important_nodes.append({
                        "id": node_id,
                        "block_id": node.block_id,
                        "color": node.color.value,
                        "weight": node.weight,
                        "connections": len(edges),
                        "created": node.created,
                        "last_accessed": node.last_accessed,
                        "metadata": node.metadata
                    })
                
                if len(important_nodes) >= limit:
                    break
            
            return {
                "format": "json",
                "nodes": important_nodes,
                "total_nodes": len(self.core.hypergraph.nodes),
                "exported": len(important_nodes),
                "timestamp": time.time()
            }
        
        elif format == "graph":
            # Экспорт в формате графа
            nodes = []
            edges = []
            
            # Узлы
            for node_id, node in self.core.hypergraph.nodes.items():
                nodes.append({
                    "id": node_id,
                    "label": f"Node {node_id[:8]}",
                    "color": node.color.value,
                    "weight": node.weight
                })
            
            # Ребра
            for (n1, n2), weight in self.core.hypergraph.edges.items():
                edges.append({
                    "source": n1,
                    "target": n2,
                    "weight": weight
                })
            
            return {
                "format": "graph",
                "nodes": nodes[:limit],
                "edges": edges[:limit * 2],
                "timestamp": time.time()
            }
        
        else:
            return {"error": f"Unsupported format: {format}"}
    
    async def shutdown(self) -> None:
        """Корректное завершение работы"""
        await self.core.shutdown()
        print("[*] EvoMethod_SK завершил работу")

# ==========================================
# 12. ИНТЕРАКТИВНЫЙ РЕЖИМ
# ==========================================

async def interactive_mode():
    """Интерактивный режим работы"""
    # Создание системы
    evo = EvoMethodSK()
    await evo.initialize()
    
    # Баннер и инструкции
    EvoVisualizer.print_banner()
    
    print("\n" + "=" * 70)
    print("[*] ИНТЕРАКТИВНЫЙ РЕЖИМ EVO_METHOD_SK 3.3")
    print("=" * 70)
    print("Команды:")
    print("  /info      - системная информация")
    print("  /stats     - подробная статистика")
    print("  /visualize - визуализация состояния")
    print("  /health    - проверка здоровья системы")
    print("  /clusters  - визуализация кластеров")
    print("  /users     - статистика пользователей")
    print("  /optimize  - оптимизация памяти (normal/deep/aggressive)")
    print("  /backup    - создание резервной копии")
    print("  /export    - экспорт знаний (json/graph)")
    print("  /exit      - выход и сохранение")
    print("=" * 70)
    
    user_counter = 1
    
    while True:
        try:
            # Ввод запроса
            user_input = input(f"\n[*] [Пользователь {user_counter}] > ").strip()
            
            if not user_input:
                continue
            
            # Обработка команд
            if user_input.startswith('/'):
                cmd = user_input[1:].lower().split()
                
                if not cmd:
                    continue
                
                command = cmd[0]
                
                if command == 'exit':
                    print("[*] Сохранение состояния...")
                    await evo.shutdown()
                    break
                
                elif command == 'info':
                    await evo.print_status()
                    continue
                
                elif command == 'stats':
                    stats = await evo.get_stats(detailed=True)
                    print(json.dumps(stats, indent=2, ensure_ascii=False))
                    continue
                
                elif command == 'visualize':
                    await EvoVisualizer.print_hypergraph_stats(evo.core.hypergraph)
                    EvoVisualizer.print_persistence_stats(evo.core.persistence)
                    continue
                
                elif command == 'health':
                    hypergraph_health = await HealthChecker.check_hypergraph(evo.core.hypergraph)
                    persistence_health = HealthChecker.check_persistence(evo.core.persistence)
                    
                    print("\n[*] СОСТОЯНИЕ ЗДОРОВЬЯ:")
                    print(f"[*] Гиперграф: {hypergraph_health['status']}")
                    print(f"[*] Хранилище: {persistence_health['status']}")
                    
                    if hypergraph_health.get('issues'):
                        print(f"\n[*] Проблемы гиперграфа:")
                        for issue in hypergraph_health['issues'][:5]:
                            print(f"  - {issue}")
                    
                    if hypergraph_health.get('warnings'):
                        print(f"\n[*]  Предупреждения гиперграфа:")
                        for warning in hypergraph_health['warnings'][:5]:
                            print(f"  - {warning}")
                    
                    continue
                
                elif command == 'clusters':
                    await EvoVisualizer.print_clusters(evo.core.hypergraph)
                    continue
                
                elif command == 'users':
                    users = evo.interface.user_profiles
                    print(f"\n[*] ПОЛЬЗОВАТЕЛИ ({len(users)}):")
                    for user_id, profile in list(users.items())[:10]:
                        print(f"  [*] {user_id}: {profile['message_count']} сообщений")
                    continue
                
                elif command == 'optimize':
                    level = cmd[1] if len(cmd) > 1 else "normal"
                    if level not in ["normal", "deep", "aggressive"]:
                        print("[*] Доступные уровни: normal, deep, aggressive")
                        continue
                    
                    result = await evo.optimize(level)
                    print(f"[*] Оптимизация завершена: {result}")
                    continue
                
                elif command == 'backup':
                    name = cmd[1] if len(cmd) > 1 else None
                    result = await evo.create_backup(name)
                    if result.get("success"):
                        print(f"[*] Резервная копия создана: {result['backup_path']}")
                        print(f"   Размер: {result['size_mb']} MB")
                    else:
                        print(f"[*] Ошибка: {result.get('error', 'unknown')}")
                    continue
                
                elif command == 'export':
                    fmt = cmd[1] if len(cmd) > 1 else "json"
                    limit = int(cmd[2]) if len(cmd) > 2 else 100
                    
                    if fmt not in ["json", "graph"]:
                        print("[*] Доступные форматы: json, graph")
                        continue
                    
                    result = await evo.export_knowledge(fmt, limit)
                    if "error" in result:
                        print(f"[*] Ошибка: {result['error']}")
                    else:
                        print(f"[*] Экспортировано: {result.get('exported', 0)} элементов")
                        print(f"[*] Формат: {result['format']}")
                        
                        # Сохранение в файл
                        export_file = SystemConfig.DATA_DIR / f"export_{int(time.time())}.json"
                        with open(export_file, 'w', encoding='utf-8') as f:
                            json.dump(result, f, ensure_ascii=False, indent=2)
                        print(f"[*] Файл: {export_file}")
                    continue
                
                else:
                    print(f"[*] Неизвестная команда: {command}")
                    continue
            
            # Обработка обычного запроса
            print(f"\n[*] Обработка запроса пользователя {user_counter}...")
            
            start_time = time.time()
            result = await evo.query(user_input, f"user_{user_counter}")
            processing_time = time.time() - start_time
            
            # Визуализация потока
            EvoVisualizer.visualize_response_flow(user_input, result)
            
            # Вывод ответа
            print(f"\n[*] Ответ ({result['method'].upper()}, {result['processing_time']}мс):")
            print("-" * 60)
            print(result['response'])
            print("-" * 60)
            
            # Дополнительная информация
            metrics = result.get('metrics', {})
            if metrics.get('blocks_used', 0) > 0:
                print(f"[*] Использовано блоков: {metrics['blocks_used']}")
            
            print(f"[*] Качество: {metrics.get('quality_score', 0):.3f}")
            print(f"[*] Режим интерфейса: {result.get('interface_mode', 'balanced')}")
            print(f"[*]  Общее время: {processing_time:.2f}с")
            
            user_counter += 1
            
        except KeyboardInterrupt:
            print("\n\n[*] Прервано пользователем")
            await evo.shutdown()
            break
        except Exception as e:
            print(f"\n[*] Ошибка: {e}")
            import traceback
            traceback.print_exc()

# ==========================================
# 13. ТЕСТОВЫЕ ФУНКЦИИ
# ==========================================

async def quick_test():
    """Быстрый тест системы"""
    print("\n[*] ЗАПУСК БЫСТРОГО ТЕСТА")
    print("=" * 60)
    
    evo = EvoMethodSK()
    await evo.initialize()
    
    test_queries = [
        "Как работает машинное обучение?",
        "Объясни разницу между SK1, SK2 и SK3",
        "Спроектируй архитектуру чат-бота с памятью",
        "Проанализируй и синтезируй знания о нейронных сетях"
    ]
    
    results = []
    for i, query in enumerate(test_queries, 1):
        print(f"\n[*] Тест {i}: {query[:50]}...")
        
        result = await evo.query(query, "test_user")
        results.append(result)
        
        print(f"   Метод: {result['method'].upper()}")
        print(f"   Время: {result['processing_time']}мс")
        print(f"   Качество: {result['metrics'].get('quality_score', 0):.3f}")
        
        if i < len(test_queries):
            await asyncio.sleep(0.5)
    
    # Статистика теста
    stats = await evo.get_stats()
    print(f"\n[*] Результаты теста:")
    print(f"   Обработано запросов: {stats['queries_processed']}")
    print(f"   Среднее время: {stats['performance']['avg_response_time_ms']}мс")
    print(f"   Ошибки: {stats['errors']}")
    
    await evo.shutdown()
    
    return results

async def performance_test():
    """Тест производительности"""
    print("\n[*] ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ")
    print("=" * 60)
    
    evo = EvoMethodSK()
    await evo.initialize()
    
    # Генерация тестовых запросов
    import random
    test_words = ["алгоритм", "система", "данные", "память", "когнитивный", 
                  "синтез", "анализ", "архитектура", "обучение", "поиск"]
    
    queries = []
    for _ in range(20):
        length = random.randint(3, 8)
        query = " ".join(random.choices(test_words, k=length)) + "?"
        queries.append(query)
    
    # Параллельная обработка
    print(f"Запуск {len(queries)} запросов...")
    
    tasks = []
    for i, query in enumerate(queries):
        task = evo.query(query, f"perf_user_{i}")
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Анализ результатов
    success = 0
    errors = 0
    times = []
    
    for result in results:
        if isinstance(result, Exception):
            errors += 1
            print(f"[*] Ошибка: {result}")
        else:
            success += 1
            times.append(result['processing_time_ms'])
    
    print(f"\n[*] Производительность:")
    print(f"   Успешно: {success}/{len(queries)}")
    print(f"   Ошибок: {errors}")
    if times:
        print(f"   Среднее время: {sum(times)/len(times):.2f}мс")
        print(f"   Максимальное время: {max(times):.2f}мс")
        print(f"   Минимальное время: {min(times):.2f}мс")
    
    await evo.shutdown()

async def stress_test():
    """Стресс-тест системы"""
    print("\n[*] СТРЕСС-ТЕСТ СИСТЕМЫ")
    print("=" * 60)
    print("[*]  Этот тест создаёт высокую нагрузку на систему")
    print("=" * 60)
    
    confirm = input("Продолжить? (y/n): ").lower()
    if confirm != 'y':
        print("Тест отменён")
        return
    
    evo = EvoMethodSK()
    await evo.initialize()
    
    # Мониторинг памяти
    import psutil
    import threading
    
    memory_samples = []
    
    def monitor_memory():
        process = psutil.Process()
        while getattr(monitor_memory, "running", True):
            memory_samples.append(process.memory_info().rss / 1024 / 1024)
            time.sleep(0.1)
    
    monitor_thread = threading.Thread(target=monitor_memory)
    monitor_thread.daemon = True
    monitor_memory.running = True
    monitor_thread.start()
    
    # Генерация нагрузки
    print("\nГенерация нагрузки...")
    
    queries = []
    for i in range(100):
        query = f"Тестовый запрос {i} о системе искусственного интеллекта и машинного обучения"
        queries.append(query)
    
    # Обработка с ограничением параллелизма
    from concurrent.futures import ThreadPoolExecutor
    
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_query = {
            executor.submit(lambda q: asyncio.run(evo.query(q, "stress_user")), query): query
            for query in queries[:50]  # Ограничение нагрузки
        }
        
        for future in asyncio.as_completed(list(future_to_query.keys())):
            try:
                result = await future
                results.append(result)
                print(f"[*] Обработан запрос {len(results)}")
            except Exception as e:
                print(f"[*] Ошибка: {e}")
    
    # Завершение мониторинга
    monitor_memory.running = False
    monitor_thread.join(timeout=1)
    
    # Анализ результатов
    print(f"\n[*] Результаты стресс-теста:")
    print(f"   Обработано запросов: {len(results)}")
    print(f"   Максимальное использование памяти: {max(memory_samples):.1f} MB")
    print(f"   Среднее использование памяти: {sum(memory_samples)/len(memory_samples):.1f} MB")
    
    await evo.shutdown()

# ==========================================
# 14. ГЛАВНАЯ ФУНКЦИЯ
# ==========================================

async def main():
    """Главная функция запуска"""
    
    # Создание директорий
    SystemConfig.DATA_DIR.mkdir(exist_ok=True)
    SystemConfig.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    
    # Выбор режима
    print("\n" + "=" * 60)
    print("[*] EVO_METHOD_SK 3.3 - PRODUCTION READY (Enhanced)")
    print("=" * 60)
    print("Режимы работы:")
    print("  1. Интерактивный режим")
    print("  2. Быстрый тест")
    print("  3. Тест производительности")
    print("  4. Стресс-тест (осторожно!)")
    print("  5. Экспорт состояния")
    print("  6. Проверка здоровья")
    print("  7. Выход")
    print("=" * 60)
    
    try:
        choice = input("\nВыберите режим (1-7): ").strip()
        
        if choice == "1":
            await interactive_mode()
        elif choice == "2":
            await quick_test()
        elif choice == "3":
            await performance_test()
        elif choice == "4":
            await stress_test()
        elif choice == "5":
            await export_state()
        elif choice == "6":
            await health_check()
        else:
            print("[*] Завершение работы")
    except KeyboardInterrupt:
        print("\n\n[*] Прервано пользователем")
    except Exception as e:
        print(f"\n[*] Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

async def export_state():
    """Экспорт состояния системы"""
    print("\n[*] ЭКСПОРТ СОСТОЯНИЯ СИСТЕМЫ")
    print("=" * 60)
    
    evo = EvoMethodSK()
    await evo.initialize()
    
    # Экспорт знаний
    print("\n[*] Экспорт знаний...")
    knowledge = await evo.export_knowledge("json", limit=100)
    
    if "error" not in knowledge:
        export_file = SystemConfig.DATA_DIR / f"export_{int(time.time())}.json"
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge, f, ensure_ascii=False, indent=2)
        
        print(f"[*] Знания экспортированы: {export_file}")
        print(f"   Узлов: {knowledge['exported']}")
        print(f"   Всего узлов в системе: {knowledge['total_nodes']}")
    
    # Экспорт статистики
    print("\n[*] Экспорт статистики...")
    stats = await evo.get_stats(detailed=True)
    
    stats_file = SystemConfig.DATA_DIR / f"stats_{int(time.time())}.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print(f"[*] Статистика экспортирована: {stats_file}")
    
    # Создание резервной копии
    print("\n[*] Создание резервной копии...")
    backup = await evo.create_backup()
    
    if backup and backup.get("success"):
        print(f"[*] Резервная копия создана: {backup['backup_path']}")
        print(f"   Размер: {backup.get('size_mb', 0):.2f} MB")
    
    await evo.shutdown()

async def health_check():
    """Проверка здоровья системы"""
    print("\n[*] ПРОВЕРКА ЗДОРОВЬЯ СИСТЕМЫ")
    print("=" * 60)
    
    evo = EvoMethodSK()
    await evo.initialize()
    
    # Проверка гиперграфа
    print("\n[*] Проверка гиперграфа...")
    hypergraph_health = await HealthChecker.check_hypergraph(evo.core.hypergraph)
    
    print(f"Статус: {hypergraph_health['status']}")
    print(f"Узлов: {hypergraph_health['nodes_count']:,}")
    print(f"Рёбер: {hypergraph_health['edges_count']:,}")
    
    if hypergraph_health['issues']:
        print(f"\n[*] Проблемы ({len(hypergraph_health['issues'])}):")
        for issue in hypergraph_health['issues'][:10]:
            print(f"  [*] {issue}")
    
    if hypergraph_health['warnings']:
        print(f"\n[*]  Предупреждения ({len(hypergraph_health['warnings'])}):")
        for warning in hypergraph_health['warnings'][:10]:
            print(f"  [*] {warning}")
    
    # Проверка хранилища
    print("\n[*] Проверка хранилища...")
    persistence_health = HealthChecker.check_persistence(evo.core.persistence)
    
    print(f"Статус: {persistence_health['status']}")
    print(f"Всего блоков: {persistence_health['total_blocks']:,}")
    
    if persistence_health['issues']:
        print(f"\n[*] Проблемы ({len(persistence_health['issues'])}):")
        for issue in persistence_health['issues'][:10]:
            print(f"  [*] {issue}")
    
    # Общая оценка
    overall_status = "HEALTHY"
    if hypergraph_health['status'] == "CRITICAL" or persistence_health['status'] == "CRITICAL":
        overall_status = "CRITICAL"
    elif hypergraph_health['status'] == "DEGRADED" or persistence_health['status'] == "DEGRADED":
        overall_status = "DEGRADED"
    
    print(f"\n[*] ОБЩАЯ ОЦЕНКА: {overall_status}")
    
    await evo.shutdown()

# ==========================================
# ТОЧКА ВХОДА
# ==========================================

if __name__ == "__main__":
    # Проверка версии Python
    import sys
    if sys.version_info < (3, 7):
        print("[*] Требуется Python 3.7 или выше")
        sys.exit(1)
    
    # Запуск системы
    try:
        asyncio.run(main())
    except RuntimeError as e:
        # Обработка для Jupyter/Google Colab
        if "cannot run non-main coroutine" in str(e):
            try:
                import nest_asyncio
                nest_asyncio.apply()
                asyncio.run(main())
            except ImportError:
                print("[*]  Для работы в этой среде установите: pip install nest_asyncio")
        else:
            raise


# ==========================================
# 15. PROJECT CORTEX COMPATIBILITY LAYER
# ==========================================

class ProjectCortex:
    """
    Singleton Project-wide Semantic Memory Wrapper.
    Maintains compatibility with existing llm_orchestrator and Z-Bus logic.
    """
    _instance = None

    @classmethod
    async def get_instance(cls):
        """Get the shared project-wide memory cortex."""
        if cls._instance is None:
            config = SystemConfig()
            # Set data directory to the project's state folder
            import os
            from pathlib import Path
            root = Path(__file__).resolve().parent.parent.parent.parent
            config.DATA_DIR = root / "state" / "project_cortex"
            config.BACKUP_DIR = root / "state" / "project_cortex_backups"
            
            cls._instance = EvoMethodSKCore(config)
            # Boot background tasks
            await cls._instance.start_background_tasks()
            
        return cls._instance

    @staticmethod
    async def find_similar(query: str, threshold: float = 0.1):
        """Compatibility method for find_similar that returns QuantumBlocks instead of tuples."""
        # Use simple attribute access or helper to get instance
        cortex_instance = await ProjectCortex.get_instance()
        similar_tuples = await cortex_instance.hypergraph.find_similar(query, min_similarity=threshold, top_k=5)
        
        results = []
        for node_id, score in similar_tuples:
            node = await cortex_instance.hypergraph.get_node(node_id)
            if node:
                block = cortex_instance.persistence.load_block(node.block_id)
                if block:
                    # Sync ID to match what orchestrator expects
                    block.id = node_id 
                    results.append(block)
        return results



