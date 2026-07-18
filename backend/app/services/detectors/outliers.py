import uuid

import numpy as np
import pandas as pd

from app.schemas.issues import DetectedIssue, IssueSeverity, IssueType
from app.services.detectors.base import BaseDetector


class OutlierDetector(BaseDetector):
    name = "outliers"

    def detect(self, df: pd.DataFrame) -> list[DetectedIssue]:
        if df.empty:
            return []

        issues: list[DetectedIssue] = []
        row_count = len(df)

        for column in df.select_dtypes(include=[np.number]).columns:
            series = df[column].dropna()
            if len(series) < 4:
                continue

            q1 = float(series.quantile(0.25))
            q3 = float(series.quantile(0.75))
            iqr = q3 - q1
            if iqr == 0:
                continue

            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            outlier_mask = (df[column] < lower) | (df[column] > upper)
            outlier_count = int(outlier_mask.sum())
            if outlier_count == 0:
                continue

            outlier_pct = round(outlier_count / row_count * 100, 2)
            if outlier_pct >= 10:
                severity = IssueSeverity.HIGH
            elif outlier_pct >= 3:
                severity = IssueSeverity.MEDIUM
            else:
                severity = IssueSeverity.LOW

            issues.append(
                DetectedIssue(
                    id=str(uuid.uuid4()),
                    type=IssueType.OUTLIERS,
                    severity=severity,
                    title=f"Statistical outliers in '{column}'",
                    description=(
                        f"Column '{column}' has {outlier_count} IQR-based outliers "
                        f"({outlier_pct}% of rows), outside [{lower:.2g}, {upper:.2g}]."
                    ),
                    affected_columns=[str(column)],
                    affected_row_count=outlier_count,
                    metrics={
                        "outlier_count": outlier_count,
                        "outlier_pct": outlier_pct,
                        "lower_bound": round(lower, 4),
                        "upper_bound": round(upper, 4),
                    },
                    recommendation=(
                        "Inspect outliers for data errors. Cap, transform, or remove only "
                        "if they are clearly invalid—not all outliers are mistakes."
                    ),
                )
            )

        return issues
