"""Module C training: daily efficiency (actual/planned) quantile models + shortfall classifier."""

from pathlib import Path

import joblib
import lightgbm as lgb
import numpy as np
import pandas as pd
from sqlalchemy import select

from app.core.config import settings
from app.core.db import SessionLocal, engine
from app.ml.dataset import load_frame
from app.ml.features import FEATS, build_features
from app.models import Mine


def pinball(y, q, a):
    return float(np.mean(np.maximum(a * (y - q), (a - 1) * (y - q))))


def main():
    frames = []
    with SessionLocal() as db:
        for m in db.scalars(select(Mine)):
            df = load_frame(engine, m.id)
            df["planned"] = df.planned.fillna(m.plan_tpd)
            f = build_features(df, m.method == "opencast")
            f["eff"] = f.actual / f.planned
            frames.append(f.dropna(subset=["eff"]))
    data = pd.concat(frames).sort_values("date")
    cut = data.date.iloc[int(len(data) * 0.8)]                  # time-based split
    tr, va = data[data.date < cut], data[data.date >= cut]

    q = {a: lgb.LGBMRegressor(objective="quantile", alpha=a, n_estimators=500, learning_rate=0.03,
                              num_leaves=31, verbose=-1).fit(tr[FEATS], tr.eff) for a in (0.1, 0.5, 0.9)}
    clf = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.03, verbose=-1).fit(
        tr[FEATS], (tr.eff < 0.9).astype(int))

    p10, p50, p90 = (q[a].predict(va[FEATS]) for a in (0.1, 0.5, 0.9))
    print("pinball q50:", pinball(va.eff.values, p50, 0.5))
    print("coverage 10-90:", float(((va.eff >= p10) & (va.eff <= p90)).mean()), "(target ≈ 0.80)")
    Path(settings.model_dir).mkdir(parents=True, exist_ok=True)
    joblib.dump({"q": q, "clf": clf, "feats": FEATS}, Path(settings.model_dir) / "shortfall.joblib")


if __name__ == "__main__":
    main()
