import uuid

import pandas as pd

from app.schemas.issues import DetectedIssue, IssueSeverity, IssueType
from app.services.detectors.base import BaseDetector


class DuplicateDetector(BaseDetector):
    name = "duplicates"

    def detect(self, df: pd.DataFrame) -> list[DetectedIssue]:
        if df.empty:
            return []

        dup_mask = df.duplicated(keep=False)
        dup_count = int(dup_mask.sum())
        if dup_count == 0:
            return []

        unique_dup_groups = int(df[dup_mask].drop_duplicates().shape[0])
        dup_pct = round(dup_count / len(df) * 100, 2)

        if dup_pct >= 20:
            severity = IssueSeverity.HIGH
        elif dup_pct >= 5:
            severity = IssueSeverity.MEDIUM
        else:
            severity = IssueSeverity.LOW

        return [
            DetectedIssue(
                id=str(uuid.uuid4()),
                type=IssueType.DUPLICATES,
                severity=severity,
                title="Exact duplicate rows detected",
                description=(
                    f"Found {dup_count} rows involved in exact duplicates "
                    f"({dup_pct}% of dataset, ~{unique_dup_groups} duplicate patterns)."
                ),
                affected_columns=[str(c) for c in df.columns],
                affected_row_count=dup_count,
                metrics={
                    "duplicate_row_count": dup_count,
                    "duplicate_pct": dup_pct,
                    "duplicate_patterns": unique_dup_groups,
                },
                recommendation=(
                    "Remove exact duplicate rows before training to avoid biased metrics "
                    "and inflated sample counts."
                ),
            )
        ]


class NearDuplicateDetector(BaseDetector):
    name = "near_duplicates"

    def detect(self, df: pd.DataFrame) -> list[DetectedIssue]:
        if df.empty or len(df.columns) < 2:
            return []

        id_cols = [
            col
            for col in df.columns
            if str(col).strip().lower().replace(" ", "_") in {"id", "index", "row_id"}
            or str(col).lower().startswith("unnamed")
        ]
        compare_cols = [col for col in df.columns if col not in id_cols]
        if len(compare_cols) < 2:
            return []

        subset = df[compare_cols]
        near_mask = subset.duplicated(keep=False)
        near_count = int(near_mask.sum())
        if near_count == 0:
            return []

        near_pct = round(near_count / len(df) * 100, 2)
        severity = IssueSeverity.MEDIUM if near_pct >= 10 else IssueSeverity.LOW

        return [
            DetectedIssue(
                id=str(uuid.uuid4()),
                type=IssueType.NEAR_DUPLICATES,
                severity=severity,
                title="Near-duplicate rows detected",
                description=(
                    f"Found {near_count} rows that match on all columns except ID-like fields "
                    f"({near_pct}% of dataset)."
                ),
                affected_columns=[str(c) for c in compare_cols],
                affected_row_count=near_count,
                metrics={"near_duplicate_row_count": near_count, "near_duplicate_pct": near_pct},
                recommendation=(
                    "Review near-duplicates manually. They may be repeated measurements, "
                    "data entry errors, or legitimate replicates."
                ),
            )
        ]
