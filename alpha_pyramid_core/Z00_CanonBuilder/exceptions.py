class CanonError(Exception):
    pass

class GeometryError(CanonError):
    pass

class UniquenessError(CanonError):
    pass

class SectorError(CanonError):
    pass

class CapabilityConflictError(CanonError):
    pass
