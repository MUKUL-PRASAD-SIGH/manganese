import datetime as dt

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.core.db import SessionLocal
from app.services.recommend_service import generate_all
from app.services.weather_service import refresh_weather


def score_job():
    try:
        with SessionLocal() as db:
            print("actions generated:", generate_all(db))
    except Exception as e:                                       # empty DB / no model yet
        print("score_job skipped:", e)


def start_scheduler() -> BackgroundScheduler:
    s = BackgroundScheduler(timezone="Asia/Kolkata")
    if settings.data_mode == "live":
        s.add_job(refresh_weather, "cron", hour=5, minute=30)
    s.add_job(score_job, "cron", hour=6)
    s.add_job(score_job, "date", run_date=dt.datetime.now() + dt.timedelta(seconds=10))   # warm start
    s.start()
    return s
