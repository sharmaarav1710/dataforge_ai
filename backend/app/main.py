from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.datasets import router as datasets_router
from app.core.config import settings
from app.core.storage import ensure_data_dirs
from app.schemas.dataset import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_data_dirs()
    yield


app = FastAPI(
    title="DataForge AI",
    description="AI-powered Dataset Engineering IDE",
    version="0.1.0",
    lifespan=lifespan,
)

print("CORS ORIGINS:", settings.cors_origin_list)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list, # This keeps your current env variables working
    allow_origin_regex=r"https://dataforge-.*\.vercel\.app", # This tells it to accept ANY Vercel preview URL!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(datasets_router, prefix="/api/v1")

@app.get("/health", response_model=HealthResponse)
async def health():
    return {
        "status": "ok",
        "cors": settings.cors_origin_list
    }