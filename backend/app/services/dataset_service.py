import uuid
from pathlib import Path

import pandas as pd

from app.core.config import settings
from app.schemas.dataset import ColumnProfile, DatasetProfile


def _safe_sample_values(series: pd.Series, limit: int = 5) -> list[str]:
    samples: list[str] = []
    for value in series.dropna().head(limit):
        text = str(value)
        samples.append(text if len(text) <= 80 else f"{text[:77]}...")
    return samples


def profile_dataframe(df: pd.DataFrame, dataset_id: str, filename: str) -> DatasetProfile:
    row_count = len(df)
    columns: list[ColumnProfile] = []

    for name in df.columns:
        series = df[name]
        null_count = int(series.isna().sum())
        non_null_count = row_count - null_count
        null_pct = round((null_count / row_count * 100) if row_count else 0.0, 2)
        unique_count = int(series.nunique(dropna=True))

        columns.append(
            ColumnProfile(
                name=str(name),
                dtype=str(series.dtype),
                non_null_count=non_null_count,
                null_count=null_count,
                null_pct=null_pct,
                unique_count=unique_count,
                sample_values=_safe_sample_values(series),
            )
        )

    memory_mb = round(float(df.memory_usage(deep=True).sum()) / (1024 * 1024), 3)

    return DatasetProfile(
        dataset_id=dataset_id,
        filename=filename,
        row_count=row_count,
        column_count=len(df.columns),
        columns=columns,
        memory_mb=memory_mb,
    )


def save_upload(file_bytes: bytes, filename: str) -> tuple[str, Path]:
    dataset_id = str(uuid.uuid4())
    upload_dir = Path(settings.data_dir) / "uploads" / dataset_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    dest = upload_dir / filename
    dest.write_bytes(file_bytes)
    return dataset_id, dest


def load_dataframe(dataset_id: str, filename: str) -> pd.DataFrame:
    path = Path(settings.data_dir) / "uploads" / dataset_id / filename
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {dataset_id}")

    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported file type: {suffix}")
