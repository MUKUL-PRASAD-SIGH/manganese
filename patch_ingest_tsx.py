import re

with open("web/src/pages/Ingest.tsx", "r") as f: text = f.read()

if 'drillholes:' not in text:
    text = text.replace('equipment: "mine_code,unit_code,date,available_hours,scheduled_hours,breakdown",',
                        'equipment: "mine_code,unit_code,date,available_hours,scheduled_hours,breakdown",\n  drillholes: "mine_code,hole_code,lat,lon,collar_z,from_m,to_m,mn_pct,fe_pct",')
    with open("web/src/pages/Ingest.tsx", "w") as f: f.write(text)

