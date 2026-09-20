from pathlib import Path

import rasterio
from fastapi import APIRouter, HTTPException
from rasterio.warp import transform_bounds

from app.core.config import settings

router = APIRouter(prefix="/prospectivity", tags=["prospectivity"])


@router.get("/meta")
def meta():
    if not Path(settings.cog_path).exists():
        raise HTTPException(404, "prospectivity COG not built yet (run scripts/predict_raster.py)")
    with rasterio.open(settings.cog_path) as src:
        b = transform_bounds(src.crs, "EPSG:4326", *src.bounds)
    # TiTiler route differs slightly across versions; check http://localhost:8001/docs
    tiles = (f"{settings.titiler_public_url}/cog/tiles/WebMercatorQuad/{{z}}/{{x}}/{{y}}.png"
             f"?url={settings.cog_path}&rescale=0,1&colormap_name=inferno")
    return {"tiles": tiles, "bounds": list(b)}
