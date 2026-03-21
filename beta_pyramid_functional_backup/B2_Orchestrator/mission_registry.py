import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Optional
from beta_pyramid_functional.B2_Orchestrator.mission_models import Mission, MissionStatus

class MissionRegistry:
    """
    Persistent store for Swarm Missions.
    Saves and loads Mission state from state/missions/.
    """
    
    _instance: Optional['MissionRegistry'] = None
    
    def __init__(self, storage_path: str = "state/missions"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.missions: Dict[str, Mission] = {}
        self._load_all()

    @classmethod
    async def get_instance(cls) -> 'MissionRegistry':
        if cls._instance is None:
            cls._instance = MissionRegistry()
        return cls._instance

    def _load_all(self):
        """Load all mission JSONs from disk."""
        for file in self.storage_path.glob("miss_*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                    mission = Mission.model_validate(data)
                    self.missions[mission.id] = mission
            except Exception as e:
                print(f"[REGISTRY] Failed to load mission {file}: {e}")

    async def save_mission(self, mission: Mission):
        """Persist mission state to disk."""
        self.missions[mission.id] = mission
        file_path = self.storage_path / f"{mission.id}.json"
        
        # Async-safe write
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._save_internal, file_path, mission)

    def _save_internal(self, path: Path, mission: Mission):
        with open(path, "w") as f:
            f.write(mission.model_dump_json(indent=2))

    def get_mission(self, mission_id: str) -> Optional[Mission]:
        return self.missions.get(mission_id)

    def list_active(self) -> Dict[str, Mission]:
        return {k: v for k, v in self.missions.items() if v.status == MissionStatus.ACTIVE}
