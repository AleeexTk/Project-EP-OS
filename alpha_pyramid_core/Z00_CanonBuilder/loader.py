import json
from pathlib import Path
from typing import List
from .models import Manifest, Coordinates, Sector

def load_manifests(modules_path: Path) -> List[Manifest]:
    manifests = []
    for path in modules_path.rglob("manifest.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        coords = Coordinates(
            x=data["coords"]["x"],
            y=data["coords"]["y"],
            z=data["coords"]["z"],
        )
        manifest = Manifest(
            module_id=data["module_id"],
            coords=coords,
            sector=Sector(data["sector"]),
            layer_kind=data["layer_kind"],
            provides=data.get("provides", []),
            consumes=data.get("consumes", []),
            egress_capabilities=data.get("egress_capabilities", []),
            allowed_calls=data.get("allowed_calls", []),
            file_path=str(path),
        )
        manifests.append(manifest)
    return manifests
