import { useEffect, useState } from "react";
import { datasetApi } from "./api/dataset";
import { HealthDashboard } from "./components/HealthDashboard";
import { DataGrid } from "./components/DataGrid";
import type { DatasetProfile, VersionManifest } from "../types/dataset";
import type { AnalysisResult } from "../types/issues";
import { AIQueryPanel } from "./components/AIQueryPanel";

function StatCard({ label, value, highlight = false }: { label: string; value: string | number; highlight?: boolean }) {
  return (
    <div className={`relative group overflow-hidden rounded-2xl border p-5 backdrop-blur-xl transition-all duration-300 ${highlight ? 'border-indigo-500/40 bg-gradient-to-br from-indigo-950/30 to-slate-900/40 shadow-xl shadow-indigo-500/5' : 'border-slate-800/80 bg-slate-900/40 hover:border-slate-700'}`}>
      <div className="absolute -right-6 -top-6 h-20 w-20 rounded-full bg-indigo-500/10 blur-2xl group-hover:bg-indigo-500/20 transition-all"></div>
      <p className="text-[11px] font-semibold text-slate-400 tracking-wider uppercase">{label}</p>
      <p className="mt-2 text-2xl font-bold tracking-tight text-white">{value}</p>
    </div>
  );
}

export default function App() {
  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [profile, setProfile] = useState<DatasetProfile | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [currentVersion, setCurrentVersion] = useState<string>("v0");
  const [manifest, setManifest] = useState<VersionManifest | null>(null);
  const [rows, setRows] = useState<Record<string, any>[]>([]);
  const [activeTab, setActiveTab] = useState<"workspace" | "health">("workspace");

  useEffect(() => {
    fetch("/datasets/health")
      .then((res) => setBackendOk(res.ok))
      .catch(() => setBackendOk(false));
  }, []);

  useEffect(() => {
    if (!profile?.dataset_id || currentVersion === "v0") return;

    async function reloadVersionProfile() {
      try {
        const data = await datasetApi.getDatasetVersionData(profile!.dataset_id, currentVersion);
        if (data?.profile) setProfile(data.profile);
        if (data?.analysis) setAnalysis(data.analysis);
        if (data?.rows) setRows(data.rows);
      } catch (err) {
        console.error("Reload error:", err);
        setError(err instanceof Error ? err.message : "Failed to load dataset version slice");
      }
    }
    reloadVersionProfile();
  }, [currentVersion]);

  async function onFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const result = await datasetApi.uploadDataset(file);
      setProfile(result.profile);
      setAnalysis(result.analysis);
      if (result.rows) setRows(result.rows);
      setCurrentVersion("v0");

      if (result.dataset_id) {
        const history = await datasetApi.getVersionHistory(result.dataset_id);
        setManifest(history);
      }
      setError(null);
    } catch (err) {
      console.error("Upload error:", err);
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  async function handleApplyFix(issueType: string, columnName: string) {
    if (!profile?.dataset_id) return;

    try {
      const result = await datasetApi.repairDataset(profile.dataset_id, issueType, { column: columnName });
      if (!result?.new_version_id) return;

      const updatedHistory = await datasetApi.getVersionHistory(profile.dataset_id);
      setManifest(updatedHistory);
      setCurrentVersion(String(result.new_version_id));
    } catch (err) {
      console.error("Repair error:", err);
    }
  }

  return (
    <div className="min-h-screen text-slate-100 bg-[#07090e] bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(99,102,241,0.12),rgba(255,255,255,0))] selection:bg-indigo-500 selection:text-white">
      {/* Top Glass Navigation Header */}
      <header className="sticky top-0 z-50 border-b border-slate-800/60 bg-[#07090e]/80 backdrop-blur-2xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-2xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-violet-400 flex items-center justify-center shadow-lg shadow-indigo-500/25 ring-1 ring-white/20">
              <span className="text-white font-black text-lg">Δ</span>
            </div>
            <div>
              <h1 className="text-sm font-bold tracking-tight text-white flex items-center gap-2">
                DataForge AI 
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-semibold uppercase tracking-wider">Studio</span>
              </h1>
              <p className="text-[11px] text-slate-400">Autonomous Dataset Engineering IDE</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            {profile?.dataset_id && (
              <button
                onClick={async () => {
                  try {
                    await datasetApi.exportDatasetVersion(profile.dataset_id, currentVersion, profile.filename || `dataset_${currentVersion}.csv`);
                  } catch (err) {
                    console.error("Export error:", err);
                  }
                }}
                className="inline-flex items-center gap-2 rounded-xl bg-slate-900/80 border border-slate-800 px-4 py-2 text-xs font-semibold text-slate-200 hover:bg-slate-800 hover:border-slate-700 transition shadow-sm active:scale-95"
              >
                <span>⬇</span> Export {currentVersion}
              </button>
            )}

            <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium border ${backendOk === null ? "bg-slate-900 border-slate-800 text-slate-400" : backendOk ? "bg-emerald-950/40 border-emerald-500/30 text-emerald-300" : "bg-rose-950/40 border-rose-500/30 text-rose-300"}`}>
              <span className={`h-1.5 w-1.5 rounded-full ${backendOk ? "bg-emerald-400 animate-pulse" : "bg-rose-400"}`}></span>
              {backendOk === null ? "Connecting…" : backendOk ? "Engine Online" : "Engine Offline"}
            </span>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-10 space-y-8">
        {!profile ? (
          <div className="min-h-[65vh] flex flex-col items-center justify-center">
            <div className="relative group w-full max-w-xl rounded-3xl p-[1px] bg-gradient-to-b from-indigo-500/40 via-slate-800/80 to-slate-900/50 shadow-2xl">
              <div className="rounded-[23px] bg-slate-950/90 backdrop-blur-3xl p-12 text-center space-y-6 relative overflow-hidden">
                <div className="absolute -right-20 -top-20 h-40 w-40 rounded-full bg-indigo-500/10 blur-3xl pointer-events-none"></div>
                <div className="mx-auto w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 text-2xl shadow-inner">
                  ✨
                </div>
                <div className="space-y-2">
                  <h2 className="text-xl font-bold tracking-tight text-white">Drop your dataset to begin</h2>
                  <p className="text-xs text-slate-400 max-w-sm mx-auto leading-relaxed">Experience next-gen data transformation with live AI validation, version controls, and instant code edits.</p>
                </div>
                <div>
                  <label className="inline-flex cursor-pointer items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-violet-600 px-6 py-3 text-xs font-semibold text-white shadow-lg shadow-indigo-600/30 hover:from-indigo-500 hover:to-violet-500 transition-all duration-200 active:scale-95">
                    {uploading ? "Analyzing Schema & Matrix…" : "Browse Dataset File"}
                    <input type="file" accept=".csv,.parquet,.pq,.xlsx" className="hidden" disabled={uploading} onChange={onFileChange} />
                  </label>
                </div>
                {error && <p className="text-xs font-medium text-rose-400">{error}</p>}
              </div>
            </div>
          </div>
        ) : (
          
          <div className="space-y-6 animate-in fade-in duration-500">
            
            {/* Quick Metrics Bar */}
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <StatCard label="Total Records" value={profile.row_count?.toLocaleString() ?? "0"} />
              <StatCard label="Matrix Columns" value={profile.column_count ?? 0} />
              <StatCard label="Dataset ID" value={profile.dataset_id?.slice(0, 8) ?? "—"} />
              <StatCard label="Active Version" value={currentVersion} highlight={true} />
            </div>

            {/* Segmented View Switcher */}
            <div className="flex items-center gap-2 border-b border-slate-800/80 pb-3">
              <button
                onClick={() => setActiveTab("workspace")}
                className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${activeTab === "workspace" ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/25" : "text-slate-400 hover:text-white hover:bg-slate-900/60"}`}
              >
                ⚡ Copilot & Data Grid
              </button>
              <button
                onClick={() => setActiveTab("health")}
                className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${activeTab === "health" ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/25" : "text-slate-400 hover:text-white hover:bg-slate-900/60"}`}
              >
                🛡️ Health & Pipeline Version Tree
              </button>
            </div>

            {/* Tab 1: Workspace Split Screen */}
            {activeTab === "workspace" && (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-1">
                  <div className="sticky top-24">
                    <AIQueryPanel datasetId={profile.dataset_id} currentVersionId={currentVersion} />
                  </div>
                </div>

                <div className="lg:col-span-2">
                  <DataGrid rows={rows} columns={profile.columns || []} />
                </div>
              </div>
            )}

            {/* Tab 2: Health & Pipeline View */}
            {activeTab === "health" && analysis && (
              <div className="animate-in fade-in duration-300">
                <HealthDashboard
                  healthScore={analysis.health_score ?? 0}
                  summary={analysis.summary ?? "No summary available"}
                  issuesBySeverity={analysis.issues_by_severity ?? { critical: 0, high: 0, medium: 0, low: 0 }}
                  issues={analysis.issues ?? []}
                  aiEnabled={analysis.ai_enabled ?? false}
                  aiSummary={analysis.ai_summary ?? null}
                  datasetId={profile.dataset_id ?? ""}
                  manifest={manifest}
                  currentVersionId={currentVersion}
                  onSelectVersion={(versionId) => setCurrentVersion(String(versionId))}
                  onApplyFix={handleApplyFix}
                />
              </div>
            )}

          </div>
        )}
      </main>
    </div>
  );
}