import re

# 1. models.py
with open("backend/app/models.py", "r") as f: text = f.read()
text = re.sub(r'from geoalchemy2 import Geometry', '', text)
text = re.sub(r'boundary = mapped_column\(Geometry\("POLYGON", srid=4326\), nullable=True\)', '', text)
text = re.sub(r'collar = mapped_column\(Geometry\("POINT", srid=4326\)\)', 'collar_lat: Mapped[float] = mapped_column(Float)\n    collar_lon: Mapped[float] = mapped_column(Float)', text)
with open("backend/app/models.py", "w") as f: f.write(text)

# 2. main.py
with open("backend/app/main.py", "r") as f: text = f.read()
text = re.sub(r'    with engine\.begin\(\) as c:\n        c\.execute\(text\("CREATE EXTENSION IF NOT EXISTS postgis"\)\)\n', '', text)
with open("backend/app/main.py", "w") as f: f.write(text)

# 3. config.py
with open("backend/app/core/config.py", "r") as f: text = f.read()
text = re.sub(r'postgresql\+psycopg://moil:moil@db:5432/moil', 'sqlite:///./moil.db', text)
with open("backend/app/core/config.py", "w") as f: f.write(text)

# 4. seed_synthetic.py
with open("backend/scripts/seed_synthetic.py", "r") as f: text = f.read()
seed_rep = """def seed_drillholes(db, mine, rng):
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
                               mn_pct=float(np.clip(g + rng.normal(0, 1.5), 0.5, 55))))"""
text = re.sub(r'def seed_drillholes\(db, mine, rng\):.*?mn_pct=float\(np\.clip\(g \+ rng\.normal\(0, 1\.5\), 0\.5, 55\)\)\)\)', seed_rep, text, flags=re.DOTALL)
text = re.sub(r'    with engine\.begin\(\) as c:\n        c\.execute\(text\("CREATE EXTENSION IF NOT EXISTS postgis"\)\)\n', '', text)
with open("backend/scripts/seed_synthetic.py", "w") as f: f.write(text)

# 5. reserve_service.py
with open("backend/app/services/reserve_service.py", "r") as f: text = f.read()
sql_rep = """SQL = text(\"\"\"
SELECT h.collar_lon * 111000 AS x, h.collar_lat * 111000 AS y,
       h.collar_z - (a.from_m + a.to_m) / 2 AS z, a.mn_pct AS g
FROM assays a JOIN drillholes h ON h.id = a.hole_id WHERE h.mine_id = :m
\"\"\")"""
text = re.sub(r'SQL = text\(""\".*?\"""\)', sql_rep, text, flags=re.DOTALL)
text = re.sub(r'# EPSG:32644 = UTM 44N, covers the Nagpur-Bhandara-Balaghat belt', '', text)
with open("backend/app/services/reserve_service.py", "w") as f: f.write(text)

# 6. ingest.py spatial points removal
with open("backend/app/api/v1/ingest.py", "r") as f: text = f.read()
ingest_rep = """            if not h:
                h = M.DrillHole(id=hash(hole_code) % (2**31), mine_id=mine_id, collar_z=cz,
                                collar_lat=lat, collar_lon=lon)"""
text = re.sub(r'            if not h:\n                h = M\.DrillHole\(id=hash\(hole_code\).*?collar=func\.ST_SetSRID\(func\.ST_MakePoint\(lon, lat\), 4326\)\)', ingest_rep, text, flags=re.DOTALL)
with open("backend/app/api/v1/ingest.py", "w") as f: f.write(text)
