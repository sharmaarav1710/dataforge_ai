import { VersionManifest } from '../types/dataset';


const API_BASE = "/api/v1";

export const datasetApi = {
    uploadDataset: async (file: File): Promise<any> => {
        const form = new FormData();
        form.append("file", file);

        const res = await fetch(`${API_BASE}/datasets/upload`, {
            method: "POST",
            body: form,
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(typeof err.detail === "string" ? err.detail : "Upload failed");
        }

        return res.json();
    },

    repairDataset: async (
        datasetId: string,
        issueType: string,
        config: Record<string, any>
    ): Promise<{ new_version_id: number; affected_rows: number }> => {
        const res = await fetch(`${API_BASE}/datasets/${datasetId}/repair`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                issue_type: issueType,
                config: config,
            }),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(typeof err.detail === "string" ? err.detail : "Repair failed");
        }

        return res.json();
    },

    getVersionHistory: async (datasetId: string): Promise<VersionManifest> => {
        const res = await fetch(`${API_BASE}/datasets/${datasetId}/versions`);

        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(typeof err.detail === "string" ? err.detail : "Failed to fetch versions");
        }

        return res.json();
    },

    getDatasetVersionData: async (
        datasetId: string, 
        versionId: string
    ): Promise<any> => {
        const res = await fetch(`${API_BASE}/datasets/${datasetId}/versions/${versionId}`);

        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(typeof err.detail === "string" ? err.detail : "Failed to fetch version data");
        }

        return res.json();
    },

    exportDatasetVersion: async (datasetId: string, versionId: string, filename: string): Promise<void> => {
        const res = await fetch(`${API_BASE}/datasets/${datasetId}/versions/${versionId}/download`);

        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(typeof err.detail === "string" ? err.detail : "Export failed");
        }

        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = filename || `dataset_${versionId}.csv`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
    },

    
    queryDatasetWithAI: async (datasetId: string, query: string, versionId: string): Promise<any> => {
        const res = await fetch(`${API_BASE}/datasets/${datasetId}/ai-query`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                query: query,
                version_id: versionId,
            }),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(typeof err.detail === "string" ? err.detail : "AI query failed");
        }

        return res.json();
    }
};