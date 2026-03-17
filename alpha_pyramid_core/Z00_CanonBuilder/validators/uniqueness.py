from typing import List
from ..models import Manifest
from ..exceptions import UniquenessError

def validate(manifests: List[Manifest]) -> None:
    ids = set()
    coords = set()
    for m in manifests:
        if m.module_id in ids:
            raise UniquenessError(f"Duplicate module_id: {m.module_id}")
        ids.add(m.module_id)
        key = (m.coords.x, m.coords.y, m.coords.z)
        if key in coords:
            raise UniquenessError(f"Duplicate coordinates: {key}")
        coords.add(key)
