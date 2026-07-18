import pandas as pd

from app.schemas.issues import AnalysisResult, DetectedIssue, IssueSeverity
from app.services.detectors import ALL_DETECTORS

SEVERITY_ORDER = {
    IssueSeverity.CRITICAL: 0,
    IssueSeverity.HIGH: 1,
    IssueSeverity.MEDIUM: 2,
    IssueSeverity.LOW: 3,
}

SEVERITY_PENALTY = {
    IssueSeverity.CRITICAL: 25,
    IssueSeverity.HIGH: 15,
    IssueSeverity.MEDIUM: 8,
    IssueSeverity.LOW: 3,
}


def _compute_health_score(issues: list[DetectedIssue]) -> float:
    score = 100.0
    for issue in issues:
        score -= SEVERITY_PENALTY[issue.severity]
    return max(0.0, round(score, 1))


def _issues_by_severity(issues: list[DetectedIssue]) -> dict[str, int]:
    counts = {severity.value: 0 for severity in IssueSeverity}
    for issue in issues:
        counts[issue.severity.value] += 1
    return counts


def _build_summary(issues: list[DetectedIssue], health_score: float) -> str:
    if not issues:
        return "No significant data quality issues detected. Dataset looks healthy for modeling."

    critical = sum(1 for i in issues if i.severity == IssueSeverity.CRITICAL)
    high = sum(1 for i in issues if i.severity == IssueSeverity.HIGH)

    if critical:
        return (
            f"Health score {health_score}/100. Found {len(issues)} issue(s) including "
            f"{critical} critical — address these before training."
        )
    if high:
        return (
            f"Health score {health_score}/100. Found {len(issues)} issue(s) with "
            f"{high} high-severity items worth fixing."
        )
    return (
        f"Health score {health_score}/100. Found {len(issues)} minor issue(s) — "
        "review recommendations before training."
    )


def analyze_dataframe(df: pd.DataFrame, dataset_id: str, filename: str) -> AnalysisResult:
    issues: list[DetectedIssue] = []
    for detector in ALL_DETECTORS:
        issues.extend(detector.detect(df))

    issues.sort(key=lambda issue: (SEVERITY_ORDER[issue.severity], issue.title))
    health_score = _compute_health_score(issues)

    return AnalysisResult(
        dataset_id=dataset_id,
        filename=filename,
        health_score=health_score,
        issue_count=len(issues),
        issues_by_severity=_issues_by_severity(issues),
        issues=issues,
        summary=_build_summary(issues, health_score),
    )
