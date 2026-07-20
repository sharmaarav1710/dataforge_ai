from app.services.analysis_service import analyze_dataframe
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from typing import Dict, Any, List
from pathlib import Path 
import pandas as pd

from app.schemas.dataset import DatasetProfile


from app.services.dataset_service import (
    DatasetService,
    VersionManager,
    save_upload,
    profile_dataframe,
    load_dataframe
)

router = APIRouter(prefix="/datasets", tags=["datasets"])


def get_version_manager() -> VersionManager:
    return VersionManager()

def get_dataset_service(vm: VersionManager = Depends(get_version_manager)) -> DatasetService:
    return DatasetService(version_manager=vm)


class RepairRequest(BaseModel):
    issue_type: str
    config: Dict[str, Any]




@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    vm: VersionManager = Depends(get_version_manager)
):
    
    try:
        
        file_bytes = await file.read()
        
        dataset_id, dest_path = save_upload(file_bytes, file.filename)
        
        vm.initialize_manifest(dataset_id, str(dest_path))
        
        
        df = load_dataframe(dataset_id, file.filename)
        profile = profile_dataframe(df, dataset_id, file.filename)
        
        
        analysis = analyze_dataframe(df, dataset_id, file.filename)
        
        
        return {
            "status": "success",
            "dataset_id": dataset_id,
            "filename": file.filename,
            "profile": profile,
            "analysis": analysis.dict() 
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload processing failed: {str(e)}"
        )

@router.post("/{dataset_id}/repair", status_code=status.HTTP_200_OK)
async def repair_dataset(
    dataset_id: str,
    payload: RepairRequest,
    service: DatasetService = Depends(get_dataset_service)
):
    try:
        
        new_version_id, affected_rows = service.apply_dataset_repair(
            dataset_id=dataset_id,
            issue_type=payload.issue_type,
            config=payload.config
        )
        return {
            "status": "success",
            "message": f"Successfully applied repair for {payload.issue_type}.",
            "new_version_id": new_version_id,
            "affected_rows": affected_rows
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute transformation: {str(e)}")

@router.get("/{dataset_id}/versions", status_code=status.HTTP_200_OK)
async def get_dataset_versions(
    dataset_id: str,
    vm: VersionManager = Depends(get_version_manager)
):
    try:
        manifest = vm.get_manifest(dataset_id)
        return manifest
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.get("/{dataset_id}/versions/{version_id}", status_code=status.HTTP_200_OK)
async def get_dataset_version_data(
    dataset_id: str,
    version_id: str,
    vm: VersionManager = Depends(get_version_manager)
):
    
    try:
        manifest = vm.get_manifest(dataset_id)
        if version_id not in manifest.get("versions", {}):
            raise HTTPException(status_code=404, detail=f"Version {version_id} not found.")
            
        version_node = manifest["versions"][version_id]
        file_path = Path(version_node["path"])

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Data file for version {version_id} missing on disk.")

        if file_path.suffix == '.csv':
            df = pd.read_csv(file_path, on_bad_lines='skip')
        elif file_path.suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            df = pd.DataFrame()
        
        profile = profile_dataframe(df, dataset_id, file_path.name)
        analysis = analyze_dataframe(df, dataset_id, file_path.name)
        
        
        df_cleaned = df.where(pd.notnull(df), None)
        rows_data = df_cleaned.to_dict(orient="records")

        return {
            "status": "success",
            "dataset_id": dataset_id,
            "current_version": version_id,
            "profile": profile,
            "analysis": analysis.dict() if hasattr(analysis, 'dict') else analysis,
            "rows": rows_data
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load version data: {str(e)}")

from fastapi.responses import FileResponse

@router.get("/{dataset_id}/versions/{version_id}/download", status_code = status.HTTP_200_OK)
async def download_dataset_version(
    dataset_id:str,
    version_id: str,
    vm: VersionManager = Depends(get_version_manager)

):
    

    try:
        manifest = vm.get_manifest(dataset_id)
        if version_id not in manifest.get("versions", {}):
            raise HTTPException(status_code=404, detail = f"Version {version_id} not found.")
        
        version_node = manifest["versions"][version_id]
        file_path = Path(version_node["path"])

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Data file for version {version_id} missing on disk.")
        
        return FileResponse(
            path = file_path,
            filename = file_path.name,
            media_type = "application/octet-stream"
        )
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"Failed to download version: {str(e)}")

from pydantic import BaseModel

class AIQueryRequest(BaseModel):
    query: str
    version_id: str = "v0"

@router.post("/{dataset_id}/ai-query", status_code=status.HTTP_200_OK)
async def query_dataset_with_ai(
    dataset_id: str,
    payload: AIQueryRequest,
    vm: VersionManager = Depends(get_version_manager)
):
    """
    Processes open-ended natural language questions and executes dataset modifications if requested.
    """
    try:
        manifest = vm.get_manifest(dataset_id)
        version_id = payload.version_id
        if version_id not in manifest.get("versions", {}):
            raise HTTPException(status_code=404, detail=f"Version {version_id} not found.")
            
        version_node = manifest["versions"][version_id]
        file_path = Path(version_node["path"])

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"Data file for version {version_id} missing on disk.")

        if file_path.suffix == '.csv':
            df = pd.read_csv(file_path, on_bad_lines='skip')
        elif file_path.suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            df = pd.DataFrame()

        user_query = payload.query.lower()
        response_text = ""
        mutation_performed = False

        
        if "drop column" in user_query or "remove column" in user_query:
            
            words = user_query.split()
            for col in df.columns:
                if col.lower() in user_query:
                    df = df.drop(columns=[col])
                    mutation_performed = True
                    response_text = f"✅ Successfully dropped column `{col}` from the dataset."
                    break
            if not mutation_performed:
                response_text = "I couldn't identify which column you wanted to drop. Please specify the exact column name."

        elif "fill" in user_query and ("null" in user_query or "missing" in user_query):
            df = df.fillna(0)
            mutation_performed = True
            response_text = "✅ Successfully filled all missing/null values with `0` across the dataset."

        
        if mutation_performed:
            
            new_version_id = vm.commit_version(
                dataset_id=dataset_id,
                df=df,
                parent_version_id=version_id,
                message=f"Applied AI chat transformation: {payload.query}"
            )
            response_text += f"\n\n🚀 A new dataset version (**v{new_version_id}**) has been created automatically!"
            
        elif "null" in user_query or "missing" in user_query:
            null_counts = df.isnull().sum()
            total_nulls = null_counts.sum()
            if total_nulls == 0:
                response_text = f"✨ There are **0 null or missing values** across all {len(df.columns)} columns in version {version_id}."
            else:
                breakdown = ", ".join([f"'{col}': {count}" for col, count in null_counts.items() if count > 0])
                response_text = f"⚠️ Found **{total_nulls} missing value(s)**:\n{breakdown}"
                
        elif "problem" in user_query or "issue" in user_query or "health" in user_query:
            null_count = df.isnull().sum().sum()
            dup_count = df.duplicated().sum()
            response_text = f"🔍 Data Health Analysis (Version {version_id}):\n- Rows: {len(df)}\n- Columns: {len(df.columns)}\n- Missing Values: {null_count}\n- Duplicate Rows: {dup_count}"
            
        elif "row" in user_query or "count" in user_query:
            response_text = f"The dataset contains **{len(df)} rows** in version {version_id}."
            
        elif "column" in user_query or "field" in user_query:
            cols = ", ".join([f"`{col}` ({dtype})" for col, dtype in df.dtypes.items()])
            response_text = f"The dataset contains {len(df.columns)} columns:\n{cols}"
            
        elif "summary" in user_query or "describe" in user_query:
            desc = df.describe().to_string()
            response_text = f"Statistical Summary:\n{desc}"
            
        else:
            
            response_text = f"💬 Open Analysis for version {version_id}:\nYour dataset contains {len(df)} records and {len(df.columns)} columns (`{', '.join(df.columns)}`). You can ask me to inspect data quality, check summaries, or run mutations like 'drop column [name]' or 'fill missing values'."

        return {
            "status": "success",
            "query": payload.query,
            "version_id": version_id,
            "answer": response_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI query failed: {str(e)}")
