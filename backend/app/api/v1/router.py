from fastapi import APIRouter

from app.api.v1 import actions, health, ingest, mines, prospectivity, reserves, risk

api_router = APIRouter()
for r in (health.router, mines.router, risk.router, reserves.router,
          actions.router, prospectivity.router, ingest.router):
    api_router.include_router(r)
