export type IssueSeverity = "low" | "medium" | "high" | "critical";

export type IssueType =
  | "missing_values"
  | "duplicates"
  | "near_duplicates"
  | "outliers"
  | "class_imbalance"
  | "data_leakage";

export type RepairEffort = "low" | "medium" | "high";

export interface RepairOption {
  id: string;
  title: string;
  description: string;
  effort: RepairEffort;
  expected_impact: string;
  recommended: boolean;
}

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
  ai_explanation?: string | null;
  model_impact?: string | null;
  repair_options?: RepairOption[];
}

export interface AnalysisResult {
  dataset_id: string;
  filename: string;
  health_score: number;
  issue_count: number;
  issues_by_severity: Record<IssueSeverity, number>;
  issues: DetectedIssue[];
  summary: string;
  ai_enabled?: boolean;
  ai_summary?: string | null;
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

export const EFFORT_STYLES: Record<RepairEffort, string> = {
  low: "bg-emerald-900/40 text-emerald-300",
  medium: "bg-amber-900/40 text-amber-300",
  high: "bg-rose-900/40 text-rose-300",
};
