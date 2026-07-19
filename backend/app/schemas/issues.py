from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.ai import RepairOption


class IssueSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueType(str, Enum):
    MISSING_VALUES = "missing_values"
    DUPLICATES = "duplicates"
    NEAR_DUPLICATES = "near_duplicates"
    OUTLIERS = "outliers"
    CLASS_IMBALANCE = "class_imbalance"
    DATA_LEAKAGE = "data_leakage"


class DetectedIssue(BaseModel):
    id: str
    type: IssueType
    severity: IssueSeverity
    title: str
    description: str
    affected_columns: list[str] = Field(default_factory=list)
    affected_row_count: int = 0
    metrics: dict[str, Any] = Field(default_factory=dict)
    recommendation: str
    ai_explanation: str | None = None
    model_impact: str | None = None
    repair_options: list[RepairOption] = Field(default_factory=list)


class AnalysisResult(BaseModel):
    dataset_id: str
    filename: str
    health_score: float
    issue_count: int
    issues_by_severity: dict[str, int]
    issues: list[DetectedIssue]
    summary: str
    ai_enabled: bool = False
    ai_summary: str | None = None
