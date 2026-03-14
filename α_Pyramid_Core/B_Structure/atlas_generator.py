import os
import json
from pathlib import Path

# Z15: Atlas Generator - Alpha Layer
# Manifest-driven 3D Projection & Atlas Sync

class AtlasGenerator:
    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.state_path = self.root_dir / "state" / "pyramid_state.json"
        
    def scan_parity(self):
        """Проверяет физическое наличие папок для узлов Пирамиды"""
        if not self.state_path.exists():
            return
            
        with open(self.state_path, "r", encoding="utf-8") as f:
            state = json.load(f)
            
        updated = False
        for node_id, node in state.get("nodes", {}).items():
            # Простая эвристика поиска папки по названию или ID
            # В будущем будет использоваться точный путь из манифеста
            search_name = node["title"].replace(" ", "_")
            found = False
            
            # Проверка в α, β, γ
            for layer_prefix in ["α_Pyramid_Core", "β_Pyramid_Functional", "γ_Pyramid_Reflective"]:
                layer_path = self.root_dir / layer_prefix
                if layer_path.exists():
                    # Проверяем наличие подпапок
                    for entry in layer_path.iterdir():
                        if entry.is_dir() and (node_id in entry.name or search_name in entry.name):
                            found = True
                            break
                if found: break
                
            # Обновление статуса в стейте
            current_status = node.get("state", "planned")
            if found and current_status == "planned":
                node["state"] = "active"
                print(f"📡 [Z15] Atlas: Node '{node_id}' manifested on disk. Updating state to 'active'.")
                updated = True
            elif not found and current_status == "active":
                # Мы не деактивируем автоматически без подтверждения, но помечаем как "missing"
                print(f"⚠️ [Z15] Atlas: WARNING - Active node '{node_id}' not found on disk.")
                
        if updated:
            with open(self.state_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
                
        return updated

if __name__ == "__main__":
    atlas = AtlasGenerator(Path("."))
    atlas.scan_parity()
    print("🗺️ [Z15] Atlas scan complete.")
