import io

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "dataforge-ai"


def test_upload_csv(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    csv_bytes = io.BytesIO()
    pd.DataFrame(
        {
            "age": [25, 30, None],
            "label": ["A", "B", "A"],
        }
    ).to_csv(csv_bytes, index=False)
    csv_bytes.seek(0)

    response = client.post(
        "/api/v1/datasets/upload",
        files={"file": ("sample.csv", csv_bytes.getvalue(), "text/csv")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "sample.csv"
    assert body["profile"]["row_count"] == 3
    assert body["profile"]["column_count"] == 2
