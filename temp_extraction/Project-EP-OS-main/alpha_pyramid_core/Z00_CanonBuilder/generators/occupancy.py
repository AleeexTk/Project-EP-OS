from typing import List, Dict
from ..models import Manifest

def _radius(z: int) -> int:
    if z % 2 == 1:
        return (17 - z) // 2
    else:
        return (17 - (z + 1)) // 2

def generate(manifests: List[Manifest]) -> Dict:
    occupancy = {}
    coord_map = {(m.coords.x, m.coords.y, m.coords.z): m.module_id for m in manifests}
    for z in range(17, 0, -1):
        R = _radius(z)
        cells = []
        for x in range(9 - R, 9 + R + 1):
            for y in range(9 - R, 9 + R + 1):
                key = (x, y, z)
                if key in coord_map:
                    cells.append({"x": x, "y": y, "status": "occupied", "module_id": coord_map[key]})
                else:
                    cells.append({"x": x, "y": y, "status": "free"})
        occupancy[str(z)] = cells
    return {"occupancy": occupancy}
