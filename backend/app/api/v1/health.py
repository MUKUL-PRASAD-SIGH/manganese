from pathlib import Path

from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health():
    return {"status": "ok", "data_mode": settings.data_mode,
            "model_loaded": (Path(settings.model_dir) / "shortfall.joblib").exists()}
