import { useEffect, useState } from "react";
import type { DatasetProfile } from "../types/dataset";
import { fetchHealth, uploadDataset } from "../api/client";

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
      <p className="text-sm text-slate-400">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-white">{value}</p>
    </div>
  );
}

export default function App() {
  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [profile, setProfile] = useState<DatasetProfile | null>(null);

  useEffect(() => {
    fetchHealth()
      .then(() => setBackendOk(true))
      .catch(() => setBackendOk(false));
  }, []);

  async function onFileChange(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);

    try {
      const result = await uploadDataset(file);
      setProfile(result.profile);
    } catch (err) {
      setProfile(null);
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-xl font-bold tracking-tight">DataForge AI</h1>
            <p className="text-sm text-slate-400">Dataset Engineering IDE</p>
          </div>
          <span
            className={`rounded-full px-3 py-1 text-xs font-medium ${
              backendOk === null
                ? "bg-slate-800 text-slate-400"
                : backendOk
                  ? "bg-emerald-900/50 text-emerald-300"
                  : "bg-rose-900/50 text-rose-300"
            }`}
          >
            {backendOk === null ? "Checking API…" : backendOk ? "API online" : "API offline"}
          </span>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-8">
        <section className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/40 p-8 text-center">
          <h2 className="text-lg font-semibold">Upload a tabular dataset</h2>
          <p className="mt-2 text-sm text-slate-400">CSV or Parquet · up to 100 MB</p>
          <label className="mt-6 inline-flex cursor-pointer items-center rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium hover:bg-indigo-500">
            {uploading ? "Analyzing…" : "Choose file"}
            <input
              type="file"
              accept=".csv,.parquet,.pq"
              className="hidden"
              disabled={uploading}
              onChange={onFileChange}
            />
          </label>
          {error && <p className="mt-4 text-sm text-rose-400">{error}</p>}
        </section>

        {profile && (
          <section className="mt-8 space-y-6">
            <div>
              <h3 className="text-lg font-semibold">Dataset profile</h3>
              <p className="text-sm text-slate-400">{profile.filename}</p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <StatCard label="Rows" value={profile.row_count.toLocaleString()} />
              <StatCard label="Columns" value={profile.column_count} />
              <StatCard label="Memory" value={`${profile.memory_mb} MB`} />
              <StatCard label="Dataset ID" value={profile.dataset_id.slice(0, 8) + "…"} />
            </div>

            <div className="overflow-x-auto rounded-xl border border-slate-800">
              <table className="min-w-full text-left text-sm">
                <thead className="bg-slate-900 text-slate-400">
                  <tr>
                    <th className="px-4 py-3 font-medium">Column</th>
                    <th className="px-4 py-3 font-medium">Type</th>
                    <th className="px-4 py-3 font-medium">Nulls</th>
                    <th className="px-4 py-3 font-medium">Unique</th>
                    <th className="px-4 py-3 font-medium">Samples</th>
                  </tr>
                </thead>
                <tbody>
                  {profile.columns.map((col) => (
                    <tr key={col.name} className="border-t border-slate-800">
                      <td className="px-4 py-3 font-medium text-white">{col.name}</td>
                      <td className="px-4 py-3 text-slate-300">{col.dtype}</td>
                      <td className="px-4 py-3 text-slate-300">
                        {col.null_count} ({col.null_pct}%)
                      </td>
                      <td className="px-4 py-3 text-slate-300">{col.unique_count}</td>
                      <td className="px-4 py-3 text-slate-400">
                        {col.sample_values.join(", ") || "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <p className="text-sm text-slate-500">
              Next up: automated issue detection and AI-powered repair recommendations.
            </p>
          </section>
        )}
      </main>
    </div>
  );
}
