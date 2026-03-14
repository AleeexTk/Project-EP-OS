from typing import List
from ..models import Manifest, Sector
from ..exceptions import SectorError

def validate(manifests: List[Manifest]) -> None:
    for m in manifests:
        if not isinstance(m.sector, Sector):
            raise SectorError(f"{m.module_id}: invalid sector {m.sector}")
