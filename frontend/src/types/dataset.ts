export interface ColumnProfile {
  name: string;
  dtype: string;
  non_null_count: number;
  null_count: number;
  null_pct: number;
  unique_count: number;
  sample_values: string[];
}

export interface DatasetProfile {
  dataset_id: string;
  filename: string;
  row_count: number;
  column_count: number;
  columns: ColumnProfile[];
  memory_mb: number;
}

export interface DatasetUploadResponse {
  dataset_id: string;
  filename: string;
  message: string;
  profile: DatasetProfile;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  timestamp: string;
}
