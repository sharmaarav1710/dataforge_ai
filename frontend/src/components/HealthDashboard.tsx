import type { DetectedIssue, IssueSeverity } from "../types/issues";
import { ISSUE_TYPE_LABELS, SEVERITY_STYLES } from "../types/issues";

function healthScoreColor(score: number): string {
  if (score >= 85) return "text-emerald-400";
  if (score >= 70) return "text-amber-400";
  return "text-rose-400";
}

function healthScoreRing(score: number): string {
  if (score >= 85) return "border-emerald-500/40 bg-emerald-950/30";
  if (score >= 70) return "border-amber-500/40 bg-amber-950/30";
  return "border-rose-500/40 bg-rose-950/30";
}

function IssueCard({ issue }: { issue: DetectedIssue }) {
  const styles = SEVERITY_STYLES[issue.severity];

  return (
    <article className={`rounded-xl border ${styles.border} bg-slate-900/50 p-5`}>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-500">
            {ISSUE_TYPE_LABELS[issue.type]}
          </p>
          <h4 className="mt-1 text-base font-semibold text-white">{issue.title}</h4>
        </div>
        <span className={`rounded-full px-2.5 py-1 text-xs font-medium capitalize ${styles.badge}`}>
          {issue.severity}
        </span>
      </div>

      <p className="mt-3 text-sm leading-relaxed text-slate-300">{issue.description}</p>

      <div className="mt-4 flex flex-wrap gap-2 text-xs text-slate-400">
        {issue.affected_columns.length > 0 && (
          <span className="rounded-md bg-slate-800 px-2 py-1">
            Columns: {issue.affected_columns.join(", ")}
          </span>
        )}
        {issue.affected_row_count > 0 && (
          <span className="rounded-md bg-slate-800 px-2 py-1">
            Rows affected: {issue.affected_row_count.toLocaleString()}
          </span>
        )}
      </div>

      <p className="mt-4 rounded-lg bg-slate-950/70 px-3 py-2 text-sm text-slate-400">
        <span className="font-medium text-slate-300">Recommendation: </span>
        {issue.recommendation}
      </p>
    </article>
  );
}

export function HealthDashboard({
  healthScore,
  summary,
  issuesBySeverity,
  issues,
}: {
  healthScore: number;
  summary: string;
  issuesBySeverity: Record<IssueSeverity, number>;
  issues: DetectedIssue[];
}) {
  return (
    <section className="mt-8 space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h3 className="text-lg font-semibold">Dataset health</h3>
          <p className="mt-1 text-sm text-slate-400">{summary}</p>
        </div>

        <div
          className={`flex h-28 w-28 flex-col items-center justify-center rounded-full border-4 ${healthScoreRing(healthScore)}`}
        >
          <span className={`text-3xl font-bold ${healthScoreColor(healthScore)}`}>
            {healthScore}
          </span>
          <span className="text-xs text-slate-400">/ 100</span>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {(["critical", "high", "medium", "low"] as IssueSeverity[]).map((severity) => (
          <div
            key={severity}
            className="rounded-xl border border-slate-800 bg-slate-900/60 px-4 py-3"
          >
            <p className="text-xs uppercase tracking-wide text-slate-500">{severity}</p>
            <p className="mt-1 text-xl font-semibold text-white">
              {issuesBySeverity[severity] ?? 0}
            </p>
          </div>
        ))}
      </div>

      {issues.length === 0 ? (
        <div className="rounded-xl border border-emerald-900/50 bg-emerald-950/20 p-6 text-sm text-emerald-300">
          No significant issues detected. Your dataset looks ready for modeling.
        </div>
      ) : (
        <div className="space-y-4">
          <h4 className="text-base font-semibold text-white">
            Detected issues ({issues.length})
          </h4>
          {issues.map((issue) => (
            <IssueCard key={issue.id} issue={issue} />
          ))}
        </div>
      )}
    </section>
  );
}
