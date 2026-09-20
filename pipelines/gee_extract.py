"""Optional: Google Earth Engine feature extraction (Module A/C inputs).

Runs *outside* the API container -- it needs `earthengine-api` + `geemap` and an
authenticated GCP project, neither of which belong in the serving image:

    pip install -r pipelines/requirements.txt
    earthengine authenticate

GEE collection IDs get renamed occasionally; check the catalog if a call 404s.
"""

import ee
import geemap

ee.Initialize(project="YOUR_GCP_PROJECT")

# Placeholder points: replace with real lease boundaries
mines = ee.FeatureCollection([
    ee.Feature(ee.Geometry.Point([79.30, 21.32]).buffer(3000), {"mine": "KDR"}),
    ee.Feature(ee.Geometry.Point([80.20, 21.80]).buffer(3000), {"mine": "BLG"}),
])

LAYERS = {   # name: (collection, band, scale_m, multiplier)
    "rain_mm":  ("UCSB-CHG/CHIRPS/DAILY", "precipitation", 5000, 1),
    "sm_surf":  ("NASA/SMAP/SPL4SMGP/007", "sm_surface", 11000, 1),
    "lst_day":  ("MODIS/061/MOD11A1", "LST_Day_1km", 1000, 0.02),    # Kelvin -> subtract 273.15
    "ndvi":     ("MODIS/061/MOD13Q1", "NDVI", 250, 0.0001),
}


def series(name, start, end):
    coll, band, scale, k = LAYERS[name]
    ic = ee.ImageCollection(coll).filterDate(start, end).select(band)
    fc = ic.map(lambda im: im.reduceRegions(mines, ee.Reducer.mean(), scale)
                .map(lambda f: f.set("date", im.date().format("YYYY-MM-dd")))).flatten()
    df = geemap.ee_to_df(fc).rename(columns={"mean": name})   # big pulls -> ee.batch.Export.table
    df[name] *= k
    return df[["mine", "date", name]]


if __name__ == "__main__":
    out = series("rain_mm", "2024-01-01", "2024-12-31")
    out.to_csv("data/raw/gee_rain_mm.csv", index=False)
    print(out.head())
