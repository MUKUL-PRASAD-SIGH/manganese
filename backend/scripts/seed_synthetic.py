"""Demo seed: synthetic history + 14-day forecast, a scripted storm, and drill holes.

Storm rain is added to *future* rows only, so it moves the forecast and the demo
but leaves the training history clean.
"""

import argparse
import datetime as dt

import numpy as np
import pandas as pd
from sqlalchemy import func, text

from app import models as M
from app.core.db import Base, SessionLocal, engine
from app.ml.synth import simulate
from app.services.db_utils import set_provenance

# The scripted storm hits only the Nagpur-Bhandara cluster, not Balaghat ~100 km
# east. A localised storm is both more realistic than a region-wide one and the
# thing that makes the demo work: it opens a weather gap between the storm-hit
# mines and Balaghat, which is what drives the redeploy optimiser to move a
# healthy unit into the slot left by Balaghat's broken dumper.
STORM_MINES = {"KDR", "MNS", "DBZ"}

MINES = [("KDR", "Kandri", "underground", 21.416, 79.266, 300),
         ("MNS", "Mansar", "underground", 21.383, 79.250, 333),
         ("DBZ", "Dongri Buzurg", "opencast", 21.548, 79.682, 1000),
         ("BLG", "Balaghat", "underground", 21.966, 80.233, 1200),
         ("CHK", "Chikla", "underground", 21.516, 79.750, 566)]


def seed_drillholes(db, mine, rng):
    cx, cy = mine.lon * 111000, mine.lat * 111000  # rough meters
    amp, top = rng.uniform(38, 50), 350.0
    for ix in range(-4, 4):
        for iy in range(-4, 4):
            x, y = cx + ix * 100, cy + iy * 100
            h = M.DrillHole(mine_id=mine.id, collar_z=top, collar_lon=x/111000, collar_lat=y/111000)
            db.add(h)
            db.flush()
            for d0 in range(0, 120, 5):
                z = top - d0 - 2.5
                g = amp * np.exp(-((x - cx) / 350) ** 2 - ((y - cy) / 250) ** 2 - ((z - (top - 60)) / 18) ** 2)
                db.add(M.Assay(hole_id=h.id, from_m=d0, to_m=d0 + 5,
                               mn_pct=float(np.clip(g + rng.normal(0, 1.5), 0.5, 55))))


def main(storm: bool):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)         # demo reset
    today = dt.date.today()
    days = pd.date_range("2022-04-01", today + dt.timedelta(days=14))
    rng = np.random.default_rng(7)
    with SessionLocal() as db:
        for i, (code, name, method, lat, lon, plan) in enumerate(MINES):
            mine = M.Mine(code=code, name=name, method=method, lat=lat, lon=lon, plan_tpd=plan)
            db.add(mine)
            db.commit()      # commit before the to_sql writes below: they use a separate connection
            d = simulate(days, plan, method == "opencast", seed=i)
            if storm and code in STORM_MINES:                        # scripted demo storm: D+3..D+5
                for k, mm in zip((3, 4, 5), (30, 55, 40)):
                    d.loc[d.date == pd.Timestamp(today + dt.timedelta(days=k)), "rain"] += mm
            hist = d[d.date <= pd.Timestamp(today)].reset_index(drop=True)
            pd.DataFrame({"mine_id": mine.id, "date": d.date.dt.date, "rain_mm": d.rain,
                          "is_forecast": d.date > pd.Timestamp(today)}).to_sql(
                "weather_daily", engine, if_exists="append", index=False, method="multi", chunksize=5000)
            pd.DataFrame({"mine_id": mine.id, "date": hist.date.dt.date,
                          "planned_t": hist.planned, "actual_t": hist.actual}).to_sql(
                "production_daily", engine, if_exists="append", index=False, method="multi", chunksize=5000)
            blast = hist[(hist.blast_delay == 1) | (rng.random(len(hist)) < 0.3)]
            pd.DataFrame({"mine_id": mine.id, "date": blast.date.dt.date,
                          "delayed": blast.blast_delay.astype(bool)}).to_sql(
                "blast_log", engine, if_exists="append", index=False, method="multi", chunksize=5000)
            for k in range(4):
                u = M.EquipmentUnit(code=f"{code}-D{k + 1}", type="dumper", home_mine_id=mine.id, tpd=plan / 4)
                db.add(u)
                db.commit()
                av = np.clip(hist.avail + rng.normal(0, 0.03, len(hist)), 0.2, 1.0)
                if code == "BLG" and k == 1:
                    av.iloc[-1] = 0.3                              # force a broken unit today (redeploy demo)
                pd.DataFrame({"mine_id": mine.id, "unit_code": u.code, "date": hist.date.dt.date,
                              "available_hours": 20 * av, "scheduled_hours": 20.0,
                              "breakdown": av < 0.7}).to_sql(
                    "equipment_daily", engine, if_exists="append", index=False, method="multi", chunksize=5000)
            seed_drillholes(db, mine, rng)
            db.commit()

        # Everything above came out of the synthetic generator: say so, so the
        # UI badge cannot silently claim this is real MOIL data.
        note = "app/ml/synth.py" + (" (+ scripted storm D+3..D+5)" if storm else "")
        for src in ("weather", "production", "equipment", "blasts"):
            set_provenance(db, src, "synthetic", note)
    print("seeded. next: python -m scripts.train_all")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--storm", action="store_true")
    main(ap.parse_args().storm)
