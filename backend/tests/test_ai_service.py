import io

import pandas as pd
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.dataset import ColumnProfile, DatasetProfile
from app.schemas.issues import AnalysisResult, DetectedIssue, IssueSeverity, IssueType
from app.services.ai_service import enrich_analysis_with_ai

client = TestClient(app)


def _make_profile() -> DatasetProfile:
    return DatasetProfile(
        dataset_id="test-id",
        filename="sample.csv",
        row_count=5,
        column_count=2,
        columns=[
            ColumnProfile(
                name="age",
                dtype="float64",
                non_null_count=4,
                null_count=1,
                null_pct=20.0,
                unique_count=4,
                sample_values=["25.0", "30.0"],
            ),
            ColumnProfile(
                name="label",
                dtype="object",
                non_null_count=5,
                null_count=0,
                null_pct=0.0,
                unique_count=2,
                sample_values=["A", "B"],
            ),
        ],
        memory_mb=0.001,
    )


def _make_analysis() -> AnalysisResult:
    return AnalysisResult(
        dataset_id="test-id",
        filename="sample.csv",
        health_score=92.0,
        issue_count=1,
        issues_by_severity={"critical": 0, "high": 0, "medium": 0, "low": 1},
        summary="Health score 92/100.",
        issues=[
            DetectedIssue(
                id="issue-1",
                type=IssueType.MISSING_VALUES,
                severity=IssueSeverity.LOW,
                title="Missing values in 'age'",
                description="Column 'age' has 1 missing value (20% of rows).",
                affected_columns=["age"],
                affected_row_count=1,
                metrics={"null_count": 1, "null_pct": 20.0},
                recommendation="Impute or drop missing values.",
            )
        ],
    )


def test_enrich_analysis_without_api_key(monkeypatch):
    monkeypatch.setattr("app.services.ai_service.settings.openai_api_key", "")

    result = enrich_analysis_with_ai(_make_analysis(), _make_profile())

    assert result.ai_enabled is False
    assert result.ai_summary
    assert "OPENAI_API_KEY" in result.ai_summary
    assert len(result.issues[0].repair_options) >= 1
    assert result.issues[0].model_impact
    assert any(opt.recommended for opt in result.issues[0].repair_options)


def test_analyze_includes_ai_fields_without_key(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setattr("app.services.ai_service.settings.openai_api_key", "")

    csv_bytes = io.BytesIO()
    pd.DataFrame({"age": [25, 30, None], "label": ["A", "B", "A"]}).to_csv(csv_bytes, index=False)
    csv_bytes.seek(0)

    upload = client.post(
        "/api/v1/datasets/upload",
        files={"file": ("sample.csv", csv_bytes.getvalue(), "text/csv")},
    ).json()

    response = client.post(
        f"/api/v1/datasets/{upload['dataset_id']}/analyze",
        params={"filename": upload["filename"], "include_ai": True},
    )

    assert response.status_code == 200
    body = response.json()
    assert "ai_summary" in body
    assert body["ai_enabled"] is False
    assert body["issues"][0]["repair_options"]
    assert body["issues"][0]["model_impact"]


def test_analyze_can_skip_ai(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    csv_bytes = io.BytesIO()
    pd.DataFrame({"age": [25, 30, None], "label": ["A", "B", "A"]}).to_csv(csv_bytes, index=False)
    csv_bytes.seek(0)

    upload = client.post(
        "/api/v1/datasets/upload",
        files={"file": ("sample.csv", csv_bytes.getvalue(), "text/csv")},
    ).json()

    response = client.post(
        f"/api/v1/datasets/{upload['dataset_id']}/analyze",
        params={"filename": upload["filename"], "include_ai": False},
    )

    assert response.status_code == 200
    body = response.json()
    assert body.get("ai_summary") is None
    assert not body["issues"][0].get("repair_options")
