import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models as M
from app.core.db import get_db
from app.core.security import require_key
from app.services import risk_service
from app.services.db_utils import set_provenance, upsert

router = APIRouter(prefix="/ingest", tags=["ingest"], dependencies=[Depends(require_key)])

SPECS = {   # kind: (Model, required CSV columns, conflict keys)
    "production": (M.ProductionDaily, ["mine_code", "date", "planned_t", "actual_t"], ["mine_id", "date"]),
    "weather":    (M.WeatherDaily, ["mine_code", "date", "rain_mm"], ["mine_id", "date"]),
    "blasts":     (M.BlastLog, ["mine_code", "date", "delayed"], ["mine_id", "date"]),
    "equipment":  (M.EquipmentDaily, ["mine_code", "unit_code", "date", "available_hours",
                                      "scheduled_hours", "breakdown"], ["mine_id", "unit_code", "date"]),
}


@router.post("/{kind}")
def ingest(kind: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    
    if kind == "drillholes":
        df = pd.read_csv(file.file)
        required = ["mine_code", "hole_code", "lat", "lon", "collar_z", "from_m", "to_m", "mn_pct"]
        missing = [c for c in required if c not in df.columns]
        if missing: raise HTTPException(422, f"missing columns: {missing}")
        
        ids = {m.code: m.id for m in db.scalars(select(M.Mine))}
        df["mine_id"] = df["mine_code"].map(ids)
        if df["mine_id"].isna().any(): raise HTTPException(422, "unknown mine_code")
        
        from sqlalchemy import func
        holes_inserted = 0
        assays_inserted = 0
        # group by hole
        for _, obj in df.groupby(["mine_id", "hole_code", "lat", "lon", "collar_z"]):
            mine_id, hole_code, lat, lon, cz = obj.name
            h = db.scalars(select(M.DrillHole).where(M.DrillHole.mine_id == mine_id, M.DrillHole.id == hash(hole_code) % (2**31))).first()
            if not h:
                h = M.DrillHole(id=hash(hole_code) % (2**31), mine_id=mine_id, collar_z=cz,
                                collar_lat=lat, collar_lon=lon)
                db.add(h)
                holes_inserted += 1
            
            db.flush()
            for row in obj.itertuples():
                db.add(M.Assay(hole_id=h.id, from_m=row.from_m, to_m=row.to_m, mn_pct=row.mn_pct,
                               fe_pct=getattr(row, "fe_pct", None)))
                assays_inserted += 1
        db.commit()
        return {"kind": "drillholes", "rows_holes": holes_inserted, "rows_assays": assays_inserted}

    if kind not in SPECS:
        raise HTTPException(404, f"kind must be one of {list(SPECS)}")
    Model, required, keys = SPECS[kind]
    df = pd.read_csv(file.file)
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise HTTPException(422, f"missing columns: {missing}")
    ids = {m.code: m.id for m in db.scalars(select(M.Mine))}
    bad = sorted(set(df.mine_code) - set(ids))
    if bad:
        raise HTTPException(422, f"unknown mine_code: {bad}")
    df["mine_id"] = df.pop("mine_code").map(ids)
    df["date"] = pd.to_datetime(df["date"]).dt.date
    for c in ("breakdown", "delayed", "is_forecast"):
        if c in df:
            df[c] = df[c].astype(bool)
    cols = {c.name for c in Model.__table__.columns} - {"id"}
    df = df[[c for c in df.columns if c in cols]]
    rows = df.astype(object).where(df.notna(), None).to_dict("records")
    upsert(db, Model, rows, keys)
    set_provenance(db, kind, "uploaded",
                   f"{len(rows)} rows from {file.filename or 'CSV'} ({df['date'].min()} to {df['date'].max()})")
    risk_service.cache.clear()
    return {"kind": kind, "rows": len(rows),
            "date_min": str(df["date"].min()), "date_max": str(df["date"].max())}
