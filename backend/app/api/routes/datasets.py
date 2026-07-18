from fastapi import APIRouter, File, HTTPException, Query, UploadFile

from app.schemas.dataset import DatasetUploadResponse
from app.schemas.issues import AnalysisResult
from app.services.analysis_service import analyze_dataframe
from app.services.dataset_service import (
    load_dataframe,
    profile_dataframe,
    resolve_filename,
    save_upload,
)

router = APIRouter(prefix="/datasets", tags=["datasets"])

ALLOWED_EXTENSIONS = {".csv", ".parquet", ".pq"}
MAX_UPLOAD_BYTES = 100 * 1024 * 1024  # 100 MB for MVP


@router.post("/upload", response_model=DatasetUploadResponse)
async def upload_dataset(file: UploadFile = File(...)) -> DatasetUploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    suffix = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File exceeds 100 MB limit")
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        dataset_id, _ = save_upload(content, file.filename)
        df = load_dataframe(dataset_id, file.filename)
        profile = profile_dataframe(df, dataset_id, file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to parse dataset: {exc}") from exc

    return DatasetUploadResponse(
        dataset_id=dataset_id,
        filename=file.filename,
        message="Dataset uploaded and profiled successfully",
        profile=profile,
    )


@router.get("/{dataset_id}/profile")
async def get_dataset_profile(
    dataset_id: str,
    filename: str | None = Query(default=None),
) -> dict:
    try:
        resolved = resolve_filename(dataset_id, filename)
        df = load_dataframe(dataset_id, resolved)
        profile = profile_dataframe(df, dataset_id, resolved)
        return profile.model_dump()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{dataset_id}/analyze", response_model=AnalysisResult)
async def analyze_dataset(
    dataset_id: str,
    filename: str | None = Query(default=None),
) -> AnalysisResult:
    try:
        resolved = resolve_filename(dataset_id, filename)
        df = load_dataframe(dataset_id, resolved)
        return analyze_dataframe(df, dataset_id, resolved)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
