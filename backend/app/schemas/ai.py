from enum import Enum

from pydantic import BaseModel, Field


class RepairEffort(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RepairOption(BaseModel):
    id: str
    title: str
    description: str
    effort: RepairEffort
    expected_impact: str
    recommended: bool = False
