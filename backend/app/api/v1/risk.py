from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.v1.deps import get_mine
from app.core.db import get_db
from app.models import Mine
from app.schemas import RiskOut
from app.services.risk_service import compute_risk

router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("/{code}", response_model=RiskOut)
def get_risk(horizon: int = Query(7, ge=1, le=14), mine: Mine = Depends(get_mine),
             db: Session = Depends(get_db)):
    return compute_risk(db, mine, horizon)
