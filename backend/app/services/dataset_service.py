import os
import json
import uuid
from pathlib import Path
from typing import Dict, Any, List, Tuple
import pandas as pd



class VersionManager:
    def __init__(self, manifest_dir: str = "data/manifests"):
        self.manifest_dir = Path(manifest_dir)
        self.manifest_dir.mkdir(parents=True, exist_ok=True)

    def _get_manifest_path(self, dataset_id: str) -> Path:
        return self.manifest_dir / f"{dataset_id}.json"

    def initialize_manifest(self, dataset_id: str, initial_path: str) -> None:
        """Initializes the tracking tree lineage layout for a newly uploaded dataset (v0)."""
        manifest_path = self._get_manifest_path(dataset_id)
        manifest_data = {
            "dataset_id": dataset_id,
            "current_version": "v0",
            "versions": {
                "v0": {
                    "path": initial_path,
                    "parent": None,
                    "changes": "Initial dataset upload verification snapshot."
                }
            }
        }
        with open(manifest_path, "w") as f:
            json.dump(manifest_data, f, indent=4)

    def get_manifest(self, dataset_id: str) -> Dict[str, Any]:
        """Fetches the state mapping dictionary tree for data version controls."""
        manifest_path = self._get_manifest_path(dataset_id)
        if not manifest_path.exists():
            raise FileNotFoundError(f"Dataset tracking registry profile '{dataset_id}' does not exist.")
        with open(manifest_path, "r") as f:
            return json.load(f)

    def update_manifest(self, dataset_id: str, version_id: str, path: str, parent: str, changes: str) -> None:
        """Appends a newly verified state transformation jump entry onto the version manifest file."""
        manifest = self.get_manifest(dataset_id)
        manifest["current_version"] = version_id
        manifest["versions"][version_id] = {
            "path": path,
            "parent": parent,
            "changes": changes
        }
        manifest_path = self._get_manifest_path(dataset_id)
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=4)


class DatasetService:
    def __init__(self, version_manager: VersionManager):
        self.version_manager = version_manager

   
    def apply_dataset_repair(self, dataset_id: str, issue_type: str, config: Dict[str, Any]) -> Tuple[str, int]:
        """
        Locates the current active file version, processes cleaning operations, 
        saves the output fork, and logs it sequentially in the management manifest.
        """
        import traceback
        
        try:
            manifest = self.version_manager.get_manifest(dataset_id)
            current_version = manifest["current_version"]
            current_path = manifest["versions"][current_version]["path"]

            if not os.path.exists(current_path):
                raise FileNotFoundError(f"Target system processing path sequence missing: {current_path}")

            base_path = Path(current_path)
            new_version_id = f"v{len(manifest['versions'])}"
            new_path = base_path.parent / f"{dataset_id}_{new_version_id}{base_path.suffix}"

          
            if base_path.suffix == '.csv':
                df = pd.read_csv(base_path)
            else:
                df = pd.read_excel(base_path)

            affected_rows = 0 
            
            
            if issue_type == "missing_values":
                target_col = config.get("column")
                if target_col in df.columns:
                    affected_rows = int(df[target_col].isnull().sum())
                    
                    if pd.api.types.is_numeric_dtype(df[target_col]):
                        fill_value = df[target_col].median()
                    else:
                        fill_value = df[target_col].mode()[0] if not df[target_col].mode().empty else "Missing"
                        
                    df[target_col] = df[target_col].fillna(fill_value)

            
            if base_path.suffix == '.csv':
                df.to_csv(new_path, index=False)
            else:
                df.to_excel(new_path, index=False)

            self.version_manager.update_manifest(
                dataset_id=dataset_id,
                version_id=new_version_id,
                path=str(new_path),
                parent=current_version,
                changes=f"Imputed missing properties inside target attribute column: '{config.get('column')}'"
            )

            return new_version_id, affected_rows

        except Exception as e:
            print("\n" + "="*50 + "\nBACKEND REPAIR CRASH TRACEBACK:\n" + "="*50)
            traceback.print_exc()
            print("="*50 + "\n")
            raise e




def save_upload(file_bytes: bytes, filename: str) -> Tuple[str, Path]:
    """Saves raw byte strings securely onto the designated file system folder tree."""
    dataset_id = str(uuid.uuid4())
    upload_dir = Path("data/uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)

    dest_path = upload_dir / f"{dataset_id}_{filename}"
    with open(dest_path, "wb") as f:
        f.write(file_bytes)

    return dataset_id, dest_path


def load_dataframe(dataset_id: str, filename: str) -> pd.DataFrame:
    """Reads specific tracking files relative to their unique file extensions into a Pandas Frame."""
    upload_dir = Path("data/uploads")
    target_path = upload_dir / f"{dataset_id}_{filename}"
    
    if not target_path.exists():
        return pd.DataFrame()

    if target_path.suffix == '.csv':
        return pd.read_csv(target_path)
    elif target_path.suffix in ['.xlsx', '.xls']:
        return pd.read_excel(target_path)
        
    return pd.DataFrame()

def profile_dataframe(df: pd.DataFrame, dataset_id: str, filename: str) -> Dict[str, Any]:
    """Assembles the exact diagnostic metadata structure required by the frontend schema."""
    import json
    
    
    memory_usage_mb = round(df.memory_usage(deep=True).sum() / (1024 * 1024), 2) if not df.empty else 0.0

    columns_list = []
    if not df.empty:
        for col_name in df.columns:
            null_c = int(df[col_name].isnull().sum())
            null_p = round((null_c / len(df)) * 100, 2)
            
            
            samples = df[col_name].dropna().head(3).astype(str).tolist()
            
            columns_list.append({
                "name": str(col_name),
                "dtype": str(df[col_name].dtype),
                "null_count": null_c,
                "null_pct": null_p,
                "unique_count": int(df[col_name].nunique()),
                "sample_values": samples
            })

    return {
        "dataset_id": dataset_id,
        "filename": filename,
        "row_count": len(df),
        "column_count": len(df.columns),
        "memory_mb": memory_usage_mb,
        "columns": columns_list
    }