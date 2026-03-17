from typing import List, Dict
from ..models import Manifest

INTERACTION_MATRIX = {
    ("spine", "purple"): "analysis_request",
    ("spine", "red"): "validation_request",
    ("purple", "gold"): "policy_request",
    ("gold", "green"): "execution_request",
    ("green", "spine"): "integrity_signal",
    ("red", "spine"): "escalation",
}

def generate(manifests: List[Manifest], routing: Dict) -> Dict:
    passports = []
    capability_map = routing.get("capability_to_module", {})
    # Build a lookup map of manifests by their Z-level
    by_z: Dict[int, List[Manifest]] = {}
    for m in manifests:
        if m.coords and m.coords.z is not None:
            if m.coords.z not in by_z:
                by_z[m.coords.z] = []
            by_z[m.coords.z].append(m)

    for z in range(16, 0, -2):
        if z not in by_z:
            continue
        routers = [m for m in by_z[z] if m.sector.value == "spine"]
        if not routers:
            continue
        router = routers[0]
        z_up = z + 1
        z_down = z - 1
        if z_down not in by_z:
            continue
        for target in by_z[z_down]:
            for cap in target.provides:
                if cap not in capability_map:
                    continue
                allowed = target.allowed_calls
                spine_allowed = False
                for rule in allowed:
                    if rule == "spine:*" or rule == f"spine:{router.module_id}":
                        spine_allowed = True
                        break
                if not spine_allowed:
                    continue
                interaction = INTERACTION_MATRIX.get((router.sector.value, target.sector.value), "custom")
                passports.append({
                    "link_id": f"Z{z}-LINK-{len(passports)+1:03}",
                    "z_level": z,
                    "between_levels": [z_up, z_down],
                    "source": {
                        "module_id": router.module_id,
                        "coords": [router.coords.x, router.coords.y, router.coords.z],
                        "sector": router.sector.value
                    },
                    "caller": None,
                    "target": {
                        "module_id": target.module_id,
                        "coords": [target.coords.x, target.coords.y, target.coords.z],
                        "sector": target.sector.value
                    },
                    "capability": cap,
                    "purpose": f"{router.sector.value} requests {cap} from {target.sector.value}",
                    "sector_interaction": {
                        "from_sector": router.sector.value,
                        "to_sector": target.sector.value,
                        "interaction_type": interaction
                    },
                    "egress": target.egress_capabilities
                })
    return {"link_passports": passports}
