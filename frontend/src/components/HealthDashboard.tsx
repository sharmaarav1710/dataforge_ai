// frontend/src/components/HealthDashboard.tsx
import type { DetectedIssue, IssueSeverity, RepairOption } from "../types/issues";
import {
  EFFORT_STYLES,
  ISSUE_TYPE_LABELS,
  SEVERITY_STYLES,
} from "../types/issues";
import { VersionTimeline } from './VersionTimeline';
import { VersionManifest } from '../types/dataset';

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

interface RepairOptionCardProps {
  option: RepairOption;
  rank: number;
  issueType: string;
  targetColumn?: string;
  onApply: (issueType: string, config: Record<string, any>) => void;
}

function RepairOptionCard({ option, rank, issueType, targetColumn, onApply }: RepairOptionCardProps) {
  return (
    <div
      className={`rounded-lg border p-4 ${
        option.recommended
          ? "border-indigo-500/50 bg-indigo-950/30"
          : "border-slate-800 bg-slate-950/50"
      }`}
    >
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="flex items-start gap-2">
          <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-800 text-xs font-semibold text-slate-300">
            {rank}
          </span>
          <div>
            <p className="font-medium text-white">{option.title}</p>
            {option.recommended && (
              <span className="mt-1 inline-block rounded-full bg-indigo-600/80 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-indigo-100">
                Recommended
              </span>
            )}
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span
            className={`rounded-full px-2 py-0.5 text-[10px] font-medium capitalize ${EFFORT_STYLES[option.effort]}`}
          >
            {option.effort} effort
          </span>
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              onApply(issueType, { column: targetColumn, strategy: option.id || 'default' });
            }}
            className="rounded bg-indigo-600 px-2.5 py-1 text-xs font-medium text-white transition-colors hover:bg-indigo-500 active:bg-indigo-700"
          >
            Apply Fix
          </button>
        </div>
      </div>
      <p className="mt-3 text-sm text-slate-300">{option.description}</p>
      <p className="mt-2 text-xs text-slate-500">
        <span className="font-medium text-slate-400">Expected impact: </span>
        {option.expected_impact}
      </p>
    </div>
  );
}

interface IssueCardProps {
  issue: DetectedIssue;
  onApplyRepair: (issueType: string, columnName: string) => void;
}

function IssueCard({ issue, onApplyRepair }: IssueCardProps) {
  const styles = SEVERITY_STYLES[issue.severity];
  const repairOptions = issue.repair_options ?? [];
  const primaryColumn = issue.affected_columns?.[0] || "";

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

      {issue.ai_explanation && (
        <div className="mt-4 rounded-lg border border-indigo-800/40 bg-indigo-950/20 px-4 py-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-indigo-300">
            AI explanation
          </p>
          <p className="mt-2 text-sm leading-relaxed text-indigo-100/90">{issue.ai_explanation}</p>
        </div>
      )}

      {issue.model_impact && (
        <div className="mt-3 rounded-lg border border-slate-800 bg-slate-950/70 px-4 py-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
            Model impact
          </p>
          <p className="mt-2 text-sm text-slate-300">{issue.model_impact}</p>
        </div>
      )}

      {repairOptions.length > 0 ? (
        <div className="mt-4 space-y-3">
          <p className="text-sm font-medium text-slate-300">Repair options</p>
          {repairOptions.map((option, index) => (
            <RepairOptionCard 
              key={option.id} 
              option={option} 
              rank={index + 1} 
              issueType={issue.type}
              targetColumn={primaryColumn}
              onApply={(type, config) => onApplyRepair(type, config.column || "")}
            />
          ))}
        </div>
      ) : (
        <div className="mt-4 flex items-center justify-between rounded-lg bg-slate-950/70 px-3 py-2 text-sm">
          <p className="text-slate-400">
            <span className="font-medium text-slate-300">Recommendation: </span>
            {issue.recommendation}
          </p>
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              onApplyRepair(issue.type, primaryColumn);
            }}
            className="ml-4 rounded bg-indigo-600 px-2.5 py-1 text-xs font-medium text-white transition-colors hover:bg-indigo-500 active:bg-indigo-700 shrink-0"
          >
            Apply Default Fix
          </button>
        </div>
      )}
    </article>
  );
}

interface HealthDashboardProps {
  datasetId: string;
  healthScore: number;
  summary: string;
  issuesBySeverity: Record<IssueSeverity, number>;
  issues: DetectedIssue[];
  aiEnabled?: boolean;
  aiSummary?: string | null;
  manifest: VersionManifest | null;
  currentVersionId: string;
  onSelectVersion: (versionId: string) => void;
  onApplyFix: (issueType: string, columnName: string) => void;
}

export function HealthDashboard({
  healthScore,
  summary,
  issuesBySeverity,
  issues,
  aiEnabled,
  aiSummary,
  manifest,
  currentVersionId,
  onSelectVersion,
  onApplyFix
}: HealthDashboardProps) {

  return (
    <div className="flex w-full bg-slate-950 text-white min-h-[calc(100vh-4rem)]">
      <section className="flex-1 p-6 space-y-6 overflow-y-auto">
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

        {aiSummary && (
          <div className={`rounded-xl border px-5 py-4 ${aiEnabled ? "border-indigo-700/50 bg-indigo-950/25" : "border-slate-700 bg-slate-900/50"}`}>
            <div className="flex flex-wrap items-center gap-2">
              <p className="text-sm font-semibold text-white">AI insights</p>
              <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide ${aiEnabled ? "bg-indigo-600/80 text-indigo-100" : "bg-slate-700 text-slate-300"}`}>
                {aiEnabled ? "OpenAI" : "Rule-based fallback"}
              </span>
            </div>
            <p className="mt-2 text-sm leading-relaxed text-slate-300">{aiSummary}</p>
          </div>
        )}

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {(["critical", "high", "medium", "low"] as IssueSeverity[]).map((severity) => (
            <div key={severity} className="rounded-xl border border-slate-800 bg-slate-900/60 px-4 py-3">
              <p className="text-xs uppercase tracking-wide text-slate-500">{severity}</p>
              <p className="mt-1 text-xl font-semibold text-white">{issuesBySeverity[severity] ?? 0}</p>
            </div>
          ))}
        </div>

        {issues.length === 0 ? (
          <div className="rounded-xl border border-emerald-900/50 bg-emerald-950/20 p-6 text-sm text-emerald-300">
            No significant issues detected. Your dataset looks ready for modeling.
          </div>
        ) : (
          <div className="space-y-4">
            <h4 className="text-base font-semibold text-white">Detected issues ({issues.length})</h4>
            {issues.map((issue) => (
              <IssueCard key={issue.id} issue={issue} onApplyRepair={onApplyFix} />
            ))}
          </div>
        )}
      </section>

      <VersionTimeline 
        manifest={manifest} 
        currentVersionId={currentVersionId}
        onSelectVersion={onSelectVersion}
      />
    </div>
  );
}