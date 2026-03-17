import json
from pathlib import Path
from typing import Dict, Any

# Z17: Apex Core - alpha Layer
# Global Module Registry & Canon Root

class ApexCore:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.registry_path = self.root_dir / "state" / "pyramid_state.json"
        self.canon_path = self.root_dir / "alpha_pyramid_core" / "A_Principles" / "canon.json"
        
    def get_full_state(self) -> Dict[str, Any]:
        """Возвращает текущее состояние всей пирамиды Z17"""
        if not self.registry_path.exists():
            return {"nodes": {}, "links": []}
        with open(self.registry_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def register_node(self, node_id: str, metadata: Dict[str, Any]):
        """Регистрирует новый узел в глобальном реестре"""
        state = self.get_full_state()
        state["nodes"][node_id] = metadata
        
        with open(self.registry_path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        print(f"📌 [Z17] Node '{node_id}' registered in Apex Registry.")

    def validate_canon(self) -> bool:
        """Проверяет целостность канонических правил на уровне Z17"""
        # В будущем здесь будет проверка подписей и хешей
        return self.canon_path.exists()

if __name__ == "__main__":
    core = ApexCore(Path("."))
    print(f"👑 Apex Core initialized at Z17. Nodes: {len(core.get_full_state()['nodes'])}")
