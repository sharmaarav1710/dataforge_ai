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

export interface PipelineStep{
  step_id:string;
  issue_type: string;
  target_column?: string;
  action_taken: string;
  timestamp: string;
  affected_rows_count: number;
  parameters_used: Record<string, any>;
}

export interface DatasetVersionNode{
  version_id: number;
  parent_version_id: number | null;
  file_path: string;
  created_at: string;
  applied_step: PipelineStep | null;
}

export interface VersionManifest {
  dataset_id: string;
  current_version: number;
  versions: DatasetVersionNode[];
}

