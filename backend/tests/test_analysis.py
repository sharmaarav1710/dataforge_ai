import io

import pandas as pd
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _upload_csv(df: pd.DataFrame, filename: str = "sample.csv") -> dict:
    csv_bytes = io.BytesIO()
    df.to_csv(csv_bytes, index=False)
    csv_bytes.seek(0)

    response = client.post(
        "/api/v1/datasets/upload",
        files={"file": (filename, csv_bytes.getvalue(), "text/csv")},
    )
    assert response.status_code == 200
    return response.json()


def test_analyze_detects_missing_values(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    upload = _upload_csv(
        pd.DataFrame(
            {
                "age": [25, 30, None],
                "label": ["A", "B", "A"],
            }
        )
    )

    response = client.post(f"/api/v1/datasets/{upload['dataset_id']}/analyze")
    assert response.status_code == 200

    body = response.json()
    assert body["issue_count"] >= 1
    assert any(issue["type"] == "missing_values" for issue in body["issues"])
    assert body["health_score"] < 100


def test_analyze_detects_multiple_issue_types(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    df = pd.DataFrame(
        {
            "id": [1, 2, 3, 4, 5, 6, 7],
            "feature_a": [10.5, 10.6, 99.0, None, 10.5, 10.5, 10.5],
            "feature_b": ["abc"] * 7,
            "target": ["A", "A", "B", "B", "A", "B", "A"],
            "split": ["train", "train", "train", "test", "test", "train", "train"],
        }
    )

    upload = _upload_csv(df, "issues_sample.csv")
    response = client.post(f"/api/v1/datasets/{upload['dataset_id']}/analyze")
    assert response.status_code == 200

    body = response.json()
    issue_types = {issue["type"] for issue in body["issues"]}

    assert "missing_values" in issue_types
    assert "class_imbalance" in issue_types or "data_leakage" in issue_types
    assert body["issues_by_severity"]["high"] + body["issues_by_severity"]["medium"] >= 1
    assert body["summary"]
