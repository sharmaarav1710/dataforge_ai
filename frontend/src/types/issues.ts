export type IssueSeverity = "low" | "medium" | "high" | "critical";

export type IssueType =
  | "missing_values"
  | "duplicates"
  | "near_duplicates"
  | "outliers"
  | "class_imbalance"
  | "data_leakage";

export interface DetectedIssue {
  id: string;
  type: IssueType;
  severity: IssueSeverity;
  title: string;
  description: string;
  affected_columns: string[];
  affected_row_count: number;
  metrics: Record<string, unknown>;
  recommendation: string;
}

export interface AnalysisResult {
  dataset_id: string;
  filename: string;
  health_score: number;
  issue_count: number;
  issues_by_severity: Record<IssueSeverity, number>;
  issues: DetectedIssue[];
  summary: string;
}

export const ISSUE_TYPE_LABELS: Record<IssueType, string> = {
  missing_values: "Missing values",
  duplicates: "Duplicates",
  near_duplicates: "Near duplicates",
  outliers: "Outliers",
  class_imbalance: "Class imbalance",
  data_leakage: "Data leakage",
};

export const SEVERITY_STYLES: Record<
  IssueSeverity,
  { badge: string; border: string }
> = {
  low: {
    badge: "bg-slate-800 text-slate-300",
    border: "border-slate-700",
  },
  medium: {
    badge: "bg-amber-900/50 text-amber-300",
    border: "border-amber-800/60",
  },
  high: {
    badge: "bg-orange-900/50 text-orange-300",
    border: "border-orange-800/60",
  },
  critical: {
    badge: "bg-rose-900/50 text-rose-300",
    border: "border-rose-800/60",
  },
};
