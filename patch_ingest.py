import re

with open("backend/app/api/v1/ingest.py", "r") as f: text = f.read()

replacement = """
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
                                collar=func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326))
                db.add(h)
                holes_inserted += 1
            
            db.flush()
            for row in obj.itertuples():
                db.add(M.Assay(hole_id=h.id, from_m=row.from_m, to_m=row.to_m, mn_pct=row.mn_pct,
                               fe_pct=getattr(row, "fe_pct", None)))
                assays_inserted += 1
        db.commit()
        return {"kind": "drillholes", "rows_holes": holes_inserted, "rows_assays": assays_inserted}
"""

if 'if kind == "drillholes":' not in text:
    text = text.replace('if kind not in SPECS:', replacement + '\n    if kind not in SPECS:')
    with open("backend/app/api/v1/ingest.py", "w") as f: f.write(text)

