from pathlib import Path

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.models import DataProvenance

router = APIRouter(tags=["health"])

# Sources the UI expects to know the provenance of. Anything missing from the
# data_provenance table is reported as "unknown", never as live.
TRACKED = ("weather", "production", "equipment", "blasts")


@router.get("/health")
def health(db: Session = Depends(get_db)):
    rows = {r.source: r for r in db.scalars(select(DataProvenance))}
    provenance = [
        {"source": s,
         "mode": rows[s].mode if s in rows else "unknown",
         "detail": rows[s].detail if s in rows else "",
         "updated_at": rows[s].updated_at.isoformat() if s in rows else None}
        for s in TRACKED
    ]
    return {
        "status": "ok",
        "data_mode": settings.data_mode,
        "model_loaded": (Path(settings.model_dir) / "shortfall.joblib").exists(),
        "provenance": provenance,
        # convenience for the badge: which sources are not real data
        "synthetic_sources": [p["source"] for p in provenance if p["mode"] in ("synthetic", "unknown")],
    }
