import os
from pathlib import Path

target = r'C:\Users\Alex Bear\Desktop\EvoPyramid OS\beta_pyramid_functional\B1_Kernel\SK_Engine\engine.py'

content = r'''

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
'''

with open(target, 'a', encoding='utf-8') as f:
    f.write(content)
print(f"Successfully appended compatibility layer to {target}")
