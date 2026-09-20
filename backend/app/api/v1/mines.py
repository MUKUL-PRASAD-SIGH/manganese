from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Mine
from app.schemas import MineSummary
from app.services.reserve_service import latest_reserve
from app.services.risk_service import compute_risk

router = APIRouter(prefix="/mines", tags=["mines"])


@router.get("", response_model=list[MineSummary])
def list_mines(db: Session = Depends(get_db)):
    out = []
    for m in db.scalars(select(Mine).order_by(Mine.code)):
        r, rv = compute_risk(db, m, 7), latest_reserve(db, m)
        out.append(MineSummary(code=m.code, name=m.name, method=m.method, lat=m.lat, lon=m.lon,
                               level=r.level, expected_shortfall_pct=r.expected_shortfall_pct,
                               reserve_p50_t=rv.p50_t if rv else None))
    return out
