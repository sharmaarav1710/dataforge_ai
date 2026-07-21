import type { DatasetUploadResponse } from "../types/dataset";
import type { AnalysisResult } from "../types/issues";

export interface HealthStatus {
  status: string;
  [key: string]: unknown;
}

const API_BASE =
  import.meta.env.VITE_API_URL ||
  "https://dataforgecheck.onrender.com";

const API_PREFIX = `${API_BASE}/api/v1`;

// Optional: remove after debugging
console.log("Backend API:", API_BASE);

export const checkHealth = async (): Promise<HealthStatus> => {
  const response = await fetch(`${API_BASE}/health`);

  if (!response.ok) {
    throw new Error("Backend is unavailable");
  }

  return response.json();
};

export async function uploadDataset(
  file: File
): Promise<DatasetUploadResponse> {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${API_PREFIX}/datasets/upload`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({
      detail: res.statusText,
    }));

    throw new Error(
      typeof err.detail === "string"
        ? err.detail
        : "Upload failed"
    );
  }

  return res.json();
}

export async function analyzeDataset(
  datasetId: string,
  filename: string
): Promise<AnalysisResult> {
  const params = new URLSearchParams({ filename });

  const res = await fetch(
    `${API_PREFIX}/datasets/${datasetId}/analyze?${params}`,
    {
      method: "POST",
    }
  );

  if (!res.ok) {
    const err = await res.json().catch(() => ({
      detail: res.statusText,
    }));

    throw new Error(
      typeof err.detail === "string"
        ? err.detail
        : "Analysis failed"
    );
  }

  return res.json();
}