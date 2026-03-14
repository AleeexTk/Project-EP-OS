from typing import List, Dict
from ..models import Manifest

def generate(manifests: List[Manifest]) -> Dict:
    modules = []
    for m in sorted(manifests, key=lambda x: (-x.coords.z, x.coords.x, x.coords.y)):
        modules.append({
            "module_id": m.module_id,
            "coords": [m.coords.x, m.coords.y, m.coords.z],
            "sector": m.sector.value,
            "provides": m.provides,
            "consumes": m.consumes,
            "egress_capabilities": m.egress_capabilities
        })
    return {"modules": modules}
