"""The one feature builder. Training and serving both call this: no train/serve skew."""

import numpy as np
import pandas as pd

FEATS = ["rain_1", "rain_3", "rain_7", "rain_14", "soil_idx", "avail_1", "avail_7",
         "bd_30", "blast_14", "opencast", "doy_sin", "doy_cos", "monsoon"]
LABELS = {
    "rain_1": "Rainfall today", "rain_3": "3-day rainfall", "rain_7": "7-day rainfall",
    "rain_14": "14-day rainfall", "soil_idx": "Soil wetness (SMAP proxy)",
    "avail_1": "Equipment availability (last day)", "avail_7": "Equipment availability (7 d)",
    "bd_30": "Breakdowns (30 d)", "blast_14": "Blast delays (14 d)",
    "opencast": "Open-cast exposure", "doy_sin": "Season", "doy_cos": "Season",
    "monsoon": "Monsoon phase",
}


def build_features(d: pd.DataFrame, opencast: bool) -> pd.DataFrame:
    """d needs: date, rain, avail, breakdown, blast_delay, planned, actual.
    Future (forecast) rows have NaN ops columns; they are filled by persistence."""
    d = d.sort_values("date").reset_index(drop=True).copy()
    d["rain"] = d["rain"].fillna(0.0)
    d["avail"] = d["avail"].ffill().fillna(0.9)
    for c in ("breakdown", "blast_delay"):
        d[c] = d[c].fillna(0.0)
    d["rain_1"] = d.rain
    for w in (3, 7, 14):
        d[f"rain_{w}"] = d.rain.rolling(w, min_periods=1).sum()
    d["soil_idx"] = d.rain.ewm(alpha=0.15, adjust=False).mean()
    d["avail_1"] = d.avail.shift(1)
    d["avail_7"] = d.avail.shift(1).rolling(7, min_periods=1).mean()
    d["bd_30"] = d.breakdown.shift(1).rolling(30, min_periods=1).sum()
    d["blast_14"] = d.blast_delay.shift(1).rolling(14, min_periods=1).sum()
    d["opencast"] = int(opencast)
    doy = d.date.dt.dayofyear
    d["doy_sin"] = np.sin(2 * np.pi * doy / 365.25)
    d["doy_cos"] = np.cos(2 * np.pi * doy / 365.25)
    d["monsoon"] = np.exp(-((doy - 215) / 40) ** 2)
    return d
