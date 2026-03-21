from typing import List, Dict
from ..models import Manifest
from ..exceptions import CapabilityConflictError

def generate(manifests: List[Manifest]) -> Dict:
    table = {}
    for m in manifests:
        for cap in m.provides:
            if cap in table:
                raise CapabilityConflictError(f"Capability conflict: '{cap}' provided by multiple modules")
            table[cap] = m.module_id
    return {"capability_to_module": table}
