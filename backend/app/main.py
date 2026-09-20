from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app import models  # noqa: F401  (registers tables)
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.db import Base, engine
from app.jobs.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    sched = start_scheduler()
    yield
    sched.shutdown(wait=False)


app = FastAPI(title="MOIL Manganese Copilot API", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                   allow_methods=["*"], allow_headers=["*"])
app.include_router(api_router, prefix="/api/v1")
