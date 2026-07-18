import uuid

import pandas as pd

from app.schemas.issues import DetectedIssue, IssueSeverity, IssueType
from app.services.detectors.base import BaseDetector

LABEL_CANDIDATES = ("target", "label", "class", "y", "category")


def _infer_label_column(df: pd.DataFrame) -> str | None:
    lower_map = {str(col).lower(): col for col in df.columns}

    for candidate in LABEL_CANDIDATES:
        if candidate in lower_map:
            return str(lower_map[candidate])

    for col in reversed(df.columns):
        series = df[col]
        if pd.api.types.is_numeric_dtype(series):
            unique_count = series.nunique(dropna=True)
            if unique_count <= 20 and unique_count >= 2:
                return str(col)
        elif series.nunique(dropna=True) <= 20 and series.nunique(dropna=True) >= 2:
            return str(col)

    return None


class ClassImbalanceDetector(BaseDetector):
    name = "class_imbalance"

    def detect(self, df: pd.DataFrame) -> list[DetectedIssue]:
        if df.empty:
            return []

        label_col = _infer_label_column(df)
        if not label_col:
            return []

        counts = df[label_col].value_counts(dropna=True)
        if len(counts) < 2:
            return []

        majority = int(counts.iloc[0])
        minority = int(counts.iloc[-1])
        imbalance_ratio = round(majority / minority, 2) if minority else float("inf")
        minority_pct = round(minority / len(df) * 100, 2)

        if imbalance_ratio >= 10 or minority_pct < 5:
            severity = IssueSeverity.HIGH
        elif imbalance_ratio >= 4 or minority_pct < 10:
            severity = IssueSeverity.MEDIUM
        elif imbalance_ratio >= 2:
            severity = IssueSeverity.LOW
        else:
            return []

        distribution = {str(k): int(v) for k, v in counts.head(10).items()}

        return [
            DetectedIssue(
                id=str(uuid.uuid4()),
                type=IssueType.CLASS_IMBALANCE,
                severity=severity,
                title=f"Class imbalance in '{label_col}'",
                description=(
                    f"Label column '{label_col}' has an imbalance ratio of {imbalance_ratio}:1. "
                    f"The smallest class is {minority_pct}% of the dataset."
                ),
                affected_columns=[label_col],
                affected_row_count=int(counts.iloc[-1]),
                metrics={
                    "label_column": label_col,
                    "imbalance_ratio": imbalance_ratio,
                    "minority_pct": minority_pct,
                    "class_distribution": distribution,
                },
                recommendation=(
                    "Consider class weights, resampling (SMOTE/undersampling), "
                    "or stratified splits. Use metrics beyond accuracy (F1, AUC)."
                ),
            )
        ]
