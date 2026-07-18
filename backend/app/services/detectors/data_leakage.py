import uuid

import pandas as pd

from app.schemas.issues import DetectedIssue, IssueSeverity, IssueType
from app.services.detectors.base import BaseDetector

SPLIT_COLUMN_CANDIDATES = ("split", "fold", "subset", "partition", "set")
TRAIN_VALUES = {"train", "training", "tr"}
TEST_VALUES = {"test", "testing", "te", "val", "validation", "valid", "dev"}


def _find_split_column(df: pd.DataFrame) -> str | None:
    for col in df.columns:
        if str(col).lower() in SPLIT_COLUMN_CANDIDATES:
            return str(col)
    return None


def _normalize_split(value: object) -> str | None:
    if pd.isna(value):
        return None
    text = str(value).strip().lower()
    if text in TRAIN_VALUES:
        return "train"
    if text in TEST_VALUES:
        return "test"
    return None


class DataLeakageDetector(BaseDetector):
    name = "data_leakage"

    def detect(self, df: pd.DataFrame) -> list[DetectedIssue]:
        if df.empty:
            return []

        split_col = _find_split_column(df)
        if not split_col:
            return []

        splits = df[split_col].map(_normalize_split)
        if not ((splits == "train").any() and (splits == "test").any()):
            return []

        label_col = None
        for candidate in ("target", "label", "class", "y"):
            matches = [col for col in df.columns if str(col).lower() == candidate]
            if matches:
                label_col = str(matches[0])
                break

        feature_cols = [
            col
            for col in df.columns
            if col != split_col and col != label_col and not str(col).lower().startswith("id")
        ]
        if not feature_cols:
            return []

        train_df = df[splits == "train"]
        test_df = df[splits == "test"]

        overlap_count = 0
        overlapping_features: list[str] = []

        for col in feature_cols:
            train_vals = set(train_df[col].dropna().astype(str))
            test_vals = set(test_df[col].dropna().astype(str))
            overlap = train_vals & test_vals
            if overlap:
                overlap_count += len(overlap)
                overlapping_features.append(str(col))

        if not overlapping_features:
            return []

        severity = IssueSeverity.HIGH if len(overlapping_features) >= 2 else IssueSeverity.MEDIUM

        return [
            DetectedIssue(
                id=str(uuid.uuid4()),
                type=IssueType.DATA_LEAKAGE,
                severity=severity,
                title="Potential train/test distribution overlap",
                description=(
                    f"Split column '{split_col}' separates train and test sets, but "
                    f"{len(overlapping_features)} feature(s) share identical values across splits. "
                    "This can inflate validation scores if splits were not grouped properly."
                ),
                affected_columns=[split_col, *overlapping_features[:5]],
                affected_row_count=overlap_count,
                metrics={
                    "split_column": split_col,
                    "overlapping_feature_count": len(overlapping_features),
                    "overlapping_features": overlapping_features[:10],
                },
                recommendation=(
                    "Verify splits were created by group (user, session, entity) rather than row. "
                    "Remove or hash high-cardinality identifiers from features."
                ),
            )
        ]
