import uuid

import pandas as pd

from app.schemas.issues import DetectedIssue, IssueSeverity, IssueType
from app.services.detectors.base import BaseDetector


class MissingValuesDetector(BaseDetector):
    name = "missing_values"

    def detect(self, df: pd.DataFrame) -> list[DetectedIssue]:
        if df.empty:
            return []

        issues: list[DetectedIssue] = []
        row_count = len(df)

        for column in df.columns:
            null_count = int(df[column].isna().sum())
            if null_count == 0:
                continue

            null_pct = round(null_count / row_count * 100, 2)
            if null_pct >= 30:
                severity = IssueSeverity.CRITICAL
            elif null_pct >= 10:
                severity = IssueSeverity.HIGH
            elif null_pct >= 5:
                severity = IssueSeverity.MEDIUM
            else:
                severity = IssueSeverity.LOW

            issues.append(
                DetectedIssue(
                    id=str(uuid.uuid4()),
                    type=IssueType.MISSING_VALUES,
                    severity=severity,
                    title=f"Missing values in '{column}'",
                    description=(
                        f"Column '{column}' has {null_count} missing values "
                        f"({null_pct}% of rows)."
                    ),
                    affected_columns=[str(column)],
                    affected_row_count=null_count,
                    metrics={"null_count": null_count, "null_pct": null_pct},
                    recommendation=(
                        "Impute missing values (mean/median/mode), drop rows, "
                        "or add an indicator column depending on why data is missing."
                    ),
                )
            )

        return issues
