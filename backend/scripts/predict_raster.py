"""Prospectivity model -> probability GeoTIFF -> COG for TiTiler and MapView."""

from pathlib import Path
import joblib
import numpy as np
import rasterio
from rio_cogeo.cogeo import cog_translate
from rio_cogeo.profiles import cog_profiles

ROOT_DIR = Path(__file__).resolve().parents[2]
ARTIFACT = ROOT_DIR / "artifacts/prospectivity.joblib"
FEATURE_DIR = ROOT_DIR / "data/features"
RAW_OUT = ROOT_DIR / "data/interim/prosp_raw.tif"
COG_OUT = ROOT_DIR / "data/cogs/prospectivity.tif"


def main():
    if not ARTIFACT.exists():
        raise SystemExit(f"Model artifact not found at {ARTIFACT}. Run pipelines/train_prospectivity.py first.")
    
    bundle = joblib.load(ARTIFACT)
    model = bundle["model"] if isinstance(bundle, dict) else bundle
    expected_features = bundle.get("features", None) if isinstance(bundle, dict) else None

    paths = sorted(FEATURE_DIR.glob("*.tif"))
    if not paths:
        raise SystemExit(f"no feature rasters in {FEATURE_DIR}")

    print(f"Loading {len(paths)} feature rasters from {FEATURE_DIR}...")
    arrs = [rasterio.open(p).read(1).astype("float32") for p in paths]
    prof = rasterio.open(paths[0]).profile.copy()
    
    # Flatten and stack features
    X = np.stack([a.ravel() for a in arrs], axis=1)
    
    print(f"Running raster inference on {X.shape[0]} grid cells...")
    prob = model.predict_proba(X)[:, 1].reshape(arrs[0].shape).astype("float32")
    
    # Mask out invalid cells
    invalid_mask = np.isnan(arrs[0]) | (arrs[0] == -9999.0)
    prob[invalid_mask] = -1.0
    
    prof.update(count=1, dtype="float32", nodata=-1.0, driver="GTiff")
    
    RAW_OUT.parent.mkdir(parents=True, exist_ok=True)
    COG_OUT.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Writing raw raster to {RAW_OUT}...")
    with rasterio.open(RAW_OUT, "w", **prof) as dst:
        dst.write(prob, 1)

    print(f"Converting to Cloud-Optimized GeoTIFF (COG) at {COG_OUT}...")
    cog_translate(RAW_OUT, COG_OUT, cog_profiles.get("deflate"), in_memory=True, quiet=False)
    print("Successfully generated COG:", COG_OUT)
    print(f"Probability statistics: min={prob[prob >= 0].min():.4f}, mean={prob[prob >= 0].mean():.4f}, max={prob[prob >= 0].max():.4f}")


if __name__ == "__main__":
    main()
