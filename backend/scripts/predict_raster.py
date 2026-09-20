"""Prospectivity model -> probability GeoTIFF -> COG for TiTiler.

Export the feature rasters from GEE on one shared grid (same CRS, scale, extent)
so the stack aligns, and keep the file order identical to the training features.
"""

from pathlib import Path

import joblib
import numpy as np
import rasterio
from rio_cogeo.cogeo import cog_translate
from rio_cogeo.profiles import cog_profiles

ARTIFACT = Path("artifacts/prospectivity.joblib")
FEATURE_DIR = Path("/data/features")
RAW_OUT = Path("/data/interim/prosp_raw.tif")
COG_OUT = Path("/data/cogs/prospectivity.tif")


def main():
    bundle = joblib.load(ARTIFACT)                                  # trained in Module A
    model = bundle["model"] if isinstance(bundle, dict) else bundle
    paths = sorted(FEATURE_DIR.glob("*.tif"))       # co-registered, same grid, same order as FEATURES
    if not paths:
        raise SystemExit(f"no feature rasters in {FEATURE_DIR}")
    arrs = [rasterio.open(p).read(1).astype("float32") for p in paths]
    prof = rasterio.open(paths[0]).profile
    X = np.stack([a.ravel() for a in arrs], axis=1)
    prob = model.predict_proba(X)[:, 1].reshape(arrs[0].shape).astype("float32")
    prob[np.isnan(arrs[0])] = -1
    prof.update(count=1, dtype="float32", nodata=-1)
    RAW_OUT.parent.mkdir(parents=True, exist_ok=True)
    COG_OUT.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(RAW_OUT, "w", **prof) as dst:
        dst.write(prob, 1)
    cog_translate(RAW_OUT, COG_OUT, cog_profiles.get("deflate"))
    print("wrote", COG_OUT)


if __name__ == "__main__":
    main()
