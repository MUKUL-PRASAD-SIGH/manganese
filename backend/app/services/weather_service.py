import datetime as dt

import httpx
from sqlalchemy import select

from app.core.config import settings
from app.core.db import SessionLocal
from app.models import Mine, WeatherDaily
from app.services import risk_service
from app.services.db_utils import upsert


def refresh_weather():
    today = dt.date.today()
    with SessionLocal() as db:
        for m in db.scalars(select(Mine)):
            r = httpx.get(settings.open_meteo_url, timeout=20, params={
                "latitude": m.lat, "longitude": m.lon, "daily": "precipitation_sum",
                "past_days": 7, "forecast_days": 14, "timezone": "Asia/Kolkata"}).json()["daily"]
            rows = [dict(mine_id=m.id, date=dt.date.fromisoformat(d), rain_mm=v or 0.0,
                         is_forecast=dt.date.fromisoformat(d) > today)
                    for d, v in zip(r["time"], r["precipitation_sum"])]
            upsert(db, WeatherDaily, rows, ["mine_id", "date"])
    risk_service.cache.clear()
