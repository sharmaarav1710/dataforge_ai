from datetime import datetime, timezone

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "dataforge-ai"
    version: str = "0.1.0"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ColumnProfile(BaseModel):
    name: str
    dtype: str
    non_null_count: int
    null_count: int
    null_pct: float
    unique_count: int
    sample_values: list[str] = Field(default_factory=list)


class DatasetProfile(BaseModel):
    dataset_id: str
    filename: str
    row_count: int
    column_count: int
    columns: list[ColumnProfile]
    memory_mb: float


class DatasetUploadResponse(BaseModel):
    dataset_id: str
    filename: str
    message: str
    profile: DatasetProfile
