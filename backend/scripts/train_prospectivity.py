"""Module A training: prospectivity classifier with SPATIAL BLOCK CV.

Random CV leaks across neighbouring pixels and gives fake 0.99 AUCs. Always
block by a coarse lon/lat grid. This is positive-unlabeled learning (negatives
are pseudo-absences drawn outside a buffer around known deposits), so report
AUC-PR and "% of known deposits captured in the top 10% of area", not accuracy.

Input: data/train_points.parquet with columns lon, lat, label, <features...>
Output: backend/artifacts/prospectivity.joblib (consumed by scripts/predict_raster.py)
"""

from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import GroupKFold

from app.core.config import settings

POINTS = Path("/data/train_points.parquet")
BLOCK_DEG = 0.1        # ~11 km blocks


def main(points: Path = POINTS):
    df = pd.read_parquet(points)                      # lon, lat, label, <features>
    features = [c for c in df.columns if c not in ("lon", "lat", "label")]
    df["block"] = ((df.lon // BLOCK_DEG).astype(int).astype(str) + "_"
                   + (df.lat // BLOCK_DEG).astype(int).astype(str))

    oof = np.zeros(len(df))
    for tr, va in GroupKFold(5).split(df, df.label, df.block):
        m = lgb.LGBMClassifier(n_estimators=400, learning_rate=0.03, num_leaves=31,
                               subsample=0.8, colsample_bytree=0.8,
                               class_weight="balanced", verbose=-1)
        m.fit(df.loc[tr, features], df.label.iloc[tr])
        oof[va] = m.predict_proba(df.loc[va, features])[:, 1]

    print("AUC", roc_auc_score(df.label, oof), "AP", average_precision_score(df.label, oof))
    top = oof >= np.quantile(oof, 0.9)                # jury metric: capture in top 10% of area
    print("deposits captured in top 10% of area:", float(df.label[top].sum() / max(df.label.sum(), 1)))

    final = lgb.LGBMClassifier(n_estimators=400, learning_rate=0.03, verbose=-1).fit(df[features], df.label)
    out = Path(settings.model_dir)
    out.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": final, "features": features}, out / "prospectivity.joblib")
    print("wrote", out / "prospectivity.joblib")


if __name__ == "__main__":
    main()
