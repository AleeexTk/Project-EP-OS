from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseNode(ABC):
    """
    Standard interface for all EP-OS execution nodes.
    """
    
    def __init__(self, node_id: str, z_level: int):
        self.node_id = node_id
        self.z_level = z_level

    @abstractmethod
    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute node logic. Must return the updated context.
        """
        pass
