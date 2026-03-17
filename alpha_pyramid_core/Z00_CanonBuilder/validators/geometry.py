from typing import List
from ..models import Manifest
from ..exceptions import GeometryError

def _radius(z: int) -> int:
    if z % 2 == 1:
        return (17 - z) // 2
    else:
        return (17 - (z + 1)) // 2

def validate(manifests: List[Manifest]) -> None:
    for m in manifests:
        R = _radius(m.coords.z)
        if abs(m.coords.x - 9) > R or abs(m.coords.y - 9) > R:
            raise GeometryError(f"{m.module_id} at {m.coords} violates radius R={R}")
        if m.coords.z % 2 == 1 and m.layer_kind != "structural":
            raise GeometryError(f"{m.module_id}: odd Z must be structural")
        if m.coords.z % 2 == 0 and m.layer_kind != "transitional":
            raise GeometryError(f"{m.module_id}: even Z must be transitional")
