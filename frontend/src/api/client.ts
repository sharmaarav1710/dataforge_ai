import type { DatasetUploadResponse, HealthResponse } from "../types/dataset";
import type { AnalysisResult } from "../types/issues";

const API_BASE = "";

export async function fetchHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error("Backend unreachable");
  return res.json();
}

export async function uploadDataset(file: File): Promise<DatasetUploadResponse> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_BASE}/api/v1/datasets/upload`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(typeof err.detail === "string" ? err.detail : "Upload failed");
  }

  return res.json();
}

export async function analyzeDataset(
  datasetId: string,
  filename: string,
): Promise<AnalysisResult> {
  const params = new URLSearchParams({ filename });
  const res = await fetch(`${API_BASE}/api/v1/datasets/${datasetId}/analyze?${params}`, {
    method: "POST",
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(typeof err.detail === "string" ? err.detail : "Analysis failed");
  }

  return res.json();
}
