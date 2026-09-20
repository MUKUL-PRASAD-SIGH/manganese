import pandas as pd
from sqlalchemy import text

SQL = text("""
SELECT w.date, w.rain_mm AS rain, w.is_forecast,
       p.planned_t AS planned, p.actual_t AS actual,
       e.avail, e.breakdown, b.blast_delay
FROM weather_daily w
LEFT JOIN production_daily p ON p.mine_id = w.mine_id AND p.date = w.date
LEFT JOIN (SELECT mine_id, date,
                  AVG(available_hours / NULLIF(scheduled_hours, 0)) AS avail,
                  SUM(CAST(breakdown AS INTEGER)) AS breakdown
           FROM equipment_daily GROUP BY mine_id, date) e
       ON e.mine_id = w.mine_id AND e.date = w.date
LEFT JOIN (SELECT mine_id, date, MAX(CAST(delayed AS INTEGER)) AS blast_delay
           FROM blast_log GROUP BY mine_id, date) b
       ON b.mine_id = w.mine_id AND b.date = w.date
WHERE w.mine_id = :mid AND w.date >= :start
ORDER BY w.date
""")


def load_frame(engine, mine_id: int, start="2000-01-01") -> pd.DataFrame:
    with engine.connect() as c:
        return pd.read_sql(SQL, c, params={"mid": mine_id, "start": start}, parse_dates=["date"])
