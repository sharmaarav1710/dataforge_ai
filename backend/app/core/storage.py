from pathlib import Path

from app.core.config import settings


def ensure_data_dirs() -> None:
    for sub in ("uploads", "versions", "exports"):
        Path(settings.data_dir, sub).mkdir(parents=True, exist_ok=True)
