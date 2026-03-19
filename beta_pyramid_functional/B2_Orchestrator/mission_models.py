import uuid
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field

class MissionStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    BLOCKED = "blocked"
    COMPLETED = "completed"

class MissionTask(BaseModel):
    task_id: str = Field(default_factory=lambda: f"task_{uuid.uuid4().hex[:6]}")
    assigned_role: str
    z_level: int
    intent: str
    status: str = "pending"
    result_ref: Optional[str] = None

class Mission(BaseModel):
    id: str = Field(default_factory=lambda: f"miss_{uuid.uuid4().hex[:8]}")
    title: str
    objective: str
    tasks: List[MissionTask] = []
    status: MissionStatus = MissionStatus.DRAFT
