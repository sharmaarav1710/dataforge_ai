import json
import uuid
from typing import Any

from app.core.config import settings
from app.schemas.ai import RepairEffort, RepairOption
from app.schemas.dataset import DatasetProfile
from app.schemas.issues import AnalysisResult, DetectedIssue, IssueType

FALLBACK_TEMPLATES: dict[IssueType, list[dict[str, Any]]] = {
    IssueType.MISSING_VALUES: [
        {
            "title": "Median/mode imputation",
            "description": "Fill missing values using column median (numeric) or mode (categorical).",
            "effort": RepairEffort.LOW,
            "expected_impact": "Restores row count; may slightly reduce variance.",
            "recommended": True,
        },
        {
            "title": "Drop affected rows",
            "description": "Remove rows with missing values in critical columns.",
            "effort": RepairEffort.LOW,
            "expected_impact": "Simple fix but reduces training data size.",
            "recommended": False,
        },
        {
            "title": "Missing indicator feature",
            "description": "Add binary flags for missingness so the model can learn missing patterns.",
            "effort": RepairEffort.MEDIUM,
            "expected_impact": "Useful when missingness is informative (MNAR).",
            "recommended": False,
        },
    ],
    IssueType.DUPLICATES: [
        {
            "title": "Drop exact duplicates",
            "description": "Keep first occurrence of each duplicate row.",
            "effort": RepairEffort.LOW,
            "expected_impact": "Prevents inflated metrics and overfitting to repeated samples.",
            "recommended": True,
        },
    ],
    IssueType.NEAR_DUPLICATES: [
        {
            "title": "Manual review + dedupe",
            "description": "Inspect near-duplicate groups and keep one representative row per group.",
            "effort": RepairEffort.MEDIUM,
            "expected_impact": "Reduces redundancy without blindly deleting valid repeats.",
            "recommended": True,
        },
    ],
    IssueType.OUTLIERS: [
        {
            "title": "Winsorize (cap at IQR bounds)",
            "description": "Cap extreme values at the 1.5×IQR fence instead of deleting them.",
            "effort": RepairEffort.LOW,
            "expected_impact": "Reduces outlier influence while preserving row count.",
            "recommended": True,
        },
        {
            "title": "Log transform",
            "description": "Apply log1p transform to skewed numeric columns.",
            "effort": RepairEffort.MEDIUM,
            "expected_impact": "Can normalize distributions for linear models.",
            "recommended": False,
        },
    ],
    IssueType.CLASS_IMBALANCE: [
        {
            "title": "Class weights in loss function",
            "description": "Weight the loss inversely to class frequency during training.",
            "effort": RepairEffort.LOW,
            "expected_impact": "Improves recall on minority classes without changing data.",
            "recommended": True,
        },
        {
            "title": "Stratified resampling (SMOTE / undersampling)",
            "description": "Balance classes via oversampling minority or undersampling majority.",
            "effort": RepairEffort.MEDIUM,
            "expected_impact": "Can boost minority-class performance; watch for overfitting.",
            "recommended": False,
        },
    ],
    IssueType.DATA_LEAKAGE: [
        {
            "title": "Group-based split",
            "description": "Re-split by entity (user/session) so the same entity never appears in both train and test.",
            "effort": RepairEffort.HIGH,
            "expected_impact": "Gives honest validation scores; may lower reported metrics.",
            "recommended": True,
        },
        {
            "title": "Remove leaky features",
            "description": "Drop columns that encode split information or post-outcome data.",
            "effort": RepairEffort.MEDIUM,
            "expected_impact": "Prevents the model from cheating on validation.",
            "recommended": False,
        },
    ],
}

FALLBACK_IMPACT: dict[IssueType, str] = {
    IssueType.MISSING_VALUES: "Can cause training errors or biased predictions if the model cannot handle NaNs.",
    IssueType.DUPLICATES: "Inflates accuracy and makes cross-validation overly optimistic.",
    IssueType.NEAR_DUPLICATES: "May cause the model to memorize repeated patterns.",
    IssueType.OUTLIERS: "Can skew linear models and distance-based algorithms.",
    IssueType.CLASS_IMBALANCE: "Model may ignore minority classes; accuracy becomes misleading.",
    IssueType.DATA_LEAKAGE: "Validation scores will not generalize to production.",
}


def _build_repair_option(template: dict[str, Any]) -> RepairOption:
    return RepairOption(
        id=str(uuid.uuid4()),
        title=template["title"],
        description=template["description"],
        effort=template["effort"],
        expected_impact=template["expected_impact"],
        recommended=template.get("recommended", False),
    )


def _fallback_enrich_issue(issue: DetectedIssue) -> DetectedIssue:
    templates = FALLBACK_TEMPLATES.get(issue.type, [])
    repair_options = [_build_repair_option(t) for t in templates]

    return issue.model_copy(
        update={
            "model_impact": FALLBACK_IMPACT.get(
                issue.type,
                "May reduce model reliability if left unaddressed.",
            ),
            "repair_options": repair_options or [
                RepairOption(
                    id=str(uuid.uuid4()),
                    title="Review manually",
                    description=issue.recommendation,
                    effort=RepairEffort.MEDIUM,
                    expected_impact="Addressing this issue should improve dataset quality.",
                    recommended=True,
                )
            ],
        }
    )


def _build_profile_context(profile: DatasetProfile) -> dict[str, Any]:
    return {
        "filename": profile.filename,
        "row_count": profile.row_count,
        "column_count": profile.column_count,
        "columns": [
            {
                "name": col.name,
                "dtype": col.dtype,
                "null_pct": col.null_pct,
                "unique_count": col.unique_count,
            }
            for col in profile.columns
        ],
    }


def _build_issues_context(issues: list[DetectedIssue]) -> list[dict[str, Any]]:
    return [
        {
            "issue_id": issue.id,
            "type": issue.type.value,
            "severity": issue.severity.value,
            "title": issue.title,
            "description": issue.description,
            "affected_columns": issue.affected_columns,
            "affected_row_count": issue.affected_row_count,
            "metrics": issue.metrics,
            "recommendation": issue.recommendation,
        }
        for issue in issues
    ]


def _parse_ai_response(raw: str, issues: list[DetectedIssue]) -> tuple[str, list[DetectedIssue]]:
    data = json.loads(raw)
    ai_summary = str(data.get("ai_summary", "")).strip()
    enrichments = {item["issue_id"]: item for item in data.get("issues", []) if "issue_id" in item}

    enriched_issues: list[DetectedIssue] = []
    for issue in issues:
        item = enrichments.get(issue.id)
        if not item:
            enriched_issues.append(_fallback_enrich_issue(issue))
            continue

        repair_options = [
            RepairOption(
                id=str(uuid.uuid4()),
                title=opt.get("title", "Suggested fix"),
                description=opt.get("description", ""),
                effort=RepairEffort(opt.get("effort", "medium")),
                expected_impact=opt.get("expected_impact", "Should improve model reliability."),
                recommended=bool(opt.get("recommended", False)),
            )
            for opt in item.get("repair_options", [])
            if opt.get("title")
        ]

        enriched_issues.append(
            issue.model_copy(
                update={
                    "ai_explanation": item.get("ai_explanation") or None,
                    "model_impact": item.get("model_impact") or None,
                    "repair_options": repair_options or _fallback_enrich_issue(issue).repair_options,
                }
            )
        )

    if not ai_summary:
        ai_summary = "AI analysis complete. Review each issue and recommended repairs below."

    return ai_summary, enriched_issues


def _call_openai(profile: DatasetProfile, analysis: AnalysisResult) -> tuple[str, list[DetectedIssue]]:
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)

    system_prompt = (
        "You are an expert ML data quality engineer. Given dataset profile and detected issues, "
        "provide clear explanations and ranked repair options. Respond ONLY with valid JSON matching "
        "this schema: {\"ai_summary\": string, \"issues\": [{\"issue_id\": string, "
        "\"ai_explanation\": string, \"model_impact\": string, \"repair_options\": "
        "[{\"title\": string, \"description\": string, \"effort\": \"low\"|\"medium\"|\"high\", "
        "\"expected_impact\": string, \"recommended\": boolean}]}]}. "
        "Provide 1-3 repair_options per issue. Mark exactly one as recommended when possible. "
        "Be specific to the dataset context. Keep explanations concise (2-3 sentences)."
    )

    user_payload = {
        "dataset_profile": _build_profile_context(profile),
        "health_score": analysis.health_score,
        "detected_issues": _build_issues_context(analysis.issues),
    }

    response = client.chat.completions.create(
        model=settings.openai_model,
        response_format={"type": "json_object"},
        temperature=0.3,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_payload)},
        ],
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("Empty response from OpenAI")

    return _parse_ai_response(content, analysis.issues)


def enrich_analysis_with_ai(
    analysis: AnalysisResult,
    profile: DatasetProfile,
) -> AnalysisResult:
    if not analysis.issues:
        return analysis.model_copy(
            update={
                "ai_enabled": bool(settings.openai_api_key),
                "ai_summary": (
                    "No issues detected — dataset appears ready for modeling."
                    if settings.openai_api_key
                    else "No issues detected. Add OPENAI_API_KEY for AI-powered insights."
                ),
            }
        )

    if not settings.openai_api_key:
        enriched = [_fallback_enrich_issue(issue) for issue in analysis.issues]
        return analysis.model_copy(
            update={
                "issues": enriched,
                "ai_enabled": False,
                "ai_summary": (
                    "OpenAI API key not configured. Showing rule-based repair suggestions. "
                    "Add OPENAI_API_KEY to .env for AI-powered explanations."
                ),
            }
        )

    try:
        ai_summary, enriched_issues = _call_openai(profile, analysis)
        return analysis.model_copy(
            update={
                "issues": enriched_issues,
                "ai_enabled": True,
                "ai_summary": ai_summary,
            }
        )
    except Exception as exc:
        enriched = [_fallback_enrich_issue(issue) for issue in analysis.issues]
        return analysis.model_copy(
            update={
                "issues": enriched,
                "ai_enabled": False,
                "ai_summary": f"AI analysis unavailable ({exc}). Showing rule-based suggestions.",
            }
        )
