import json
from pathlib import Path
from typing import List
from .models import Manifest, Coordinates, Sector

def load_manifests(modules_path: Path) -> List[Manifest]:
    manifests = []
    for path in modules_path.rglob(".node_manifest.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        coords_data = data.get("coords", {"x": 9, "y": 9, "z": data.get("z_level", 0)})
        coords = Coordinates(
            x=coords_data["x"],
            y=coords_data["y"],
            z=coords_data["z"],
        )
        # Geometry-specific kind (structural/transitional)
        # If not provided, infer from Z-parity to meet geometry.py rules
        layer_kind = data.get("layer_kind")
        if not layer_kind:
            layer_kind = "structural" if coords.z % 2 == 1 else "transitional"

        manifest = Manifest(
            module_id=data.get("id") or data.get("node_id"),
            coords=coords,
            sector=Sector(data["sector"].lower()),
            layer_kind=layer_kind,
            provides=data.get("provides", []),
            consumes=data.get("consumes", []),
            egress_capabilities=data.get("egress_capabilities", []),
            allowed_calls=data.get("allowed_calls", []),
            file_path=str(path),
        )
        manifests.append(manifest)
    return manifests
