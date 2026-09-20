# MOIL Manganese Copilot

**SIH 2026 · PS 26009** — *Using AI/ML and Space Technology to Identify Manganese Reserves and Overcome Production Shortfalls* (MOIL Ltd., Ministry of Steel)

Satellites can't see manganese underground. They see **indirect indicators**. So the problem splits into three stages:

1. **Where to look** — satellite + geology → prospectivity map (LightGBM, spatial block CV)
2. **How much is there** — drill-hole assays → 3D kriging → tonnage with uncertainty (P10/P50/P90)
3. **Will we hit the plan** — weather + equipment + blasting → shortfall forecast → optimizer suggests fixes

Build plan and full design rationale: [`moil_manganese_mvp_plan.md`](moil_manganese_mvp_plan.md) and [`new_sections.md`](new_sections.md).

---

## Quick start (~30 min to a working demo)

```bash
cp .env.example .env
make up          # PostGIS
make seed        # synthetic history + 14-day forecast with a scripted storm + drill holes
make train       # trains shortfall.joblib, prints pinball loss + 10-90 coverage
make run         # api :8000, titiler :8001, web :5173
make reserves    # kriging for all 5 mines
make score       # generate corrective actions
# open http://localhost:5173
```

**Checks:** `/docs` loads · `GET /api/v1/mines` returns 5 mines · storm mines show amber/red · Kandri/Mansar/Dongri show a *blast advance* action · Balaghat shows a *redeploy* action (its broken unit is forced in the seed).

**Tuning to make the demo land:** if the redeploy action doesn't fire, lower `min_gain_t` or `transfer_loss` in `app/ml/optimizer.py`. If nothing is red, raise the storm rainfall in `scripts/seed_synthetic.py`.

The prospectivity raster layer is optional and needs real feature rasters: put co-registered GeoTIFFs in `data/features/`, run `scripts/train_prospectivity.py` then `make prosp`. Without it the map simply shows satellite + risk-coloured mine markers.

---

## Layout

```
├─ docker-compose.yml  .env.example  Makefile
├─ data/{raw,features,interim,cogs}/
├─ backend/
│  ├─ app/
│  │  ├─ core/{config,db,security}.py
│  │  ├─ models.py schemas.py           # ORM · Pydantic I/O contracts
│  │  ├─ api/v1/                        # thin routers
│  │  ├─ services/                      # fat services: risk, reserve, recommend, weather
│  │  ├─ ml/{features,dataset,registry,synth,optimizer}.py
│  │  └─ jobs/scheduler.py
│  ├─ scripts/{seed_synthetic,train_all,train_prospectivity,predict_raster}.py
│  ├─ artifacts/                        # shortfall.joblib, prospectivity.joblib
│  └─ tests/
├─ pipelines/gee_extract.py             # optional, runs outside the container
└─ web/                                 # React + Vite + MapLibre + ECharts + Tailwind
```

**Design rules:**

1. **One feature builder** (`app/ml/features.py`) is used by both training and serving. No train/serve skew.
2. **Thin routers, fat services.** Routers validate and delegate; ML lives in `app/ml/`.
3. **Models are artifacts** (`*.joblib`), not code paths. Retraining never touches the API.
4. **Stateless API + TTL cache.** Scale by adding containers; nightly jobs precompute actions.
5. **`DATA_MODE=demo|live`.** Demo uses the synthetic generator; live uses real feeds and CSV ingest. The UI shows a "SYNTHETIC DEMO DATA" badge in demo mode.

---

## API

Base `/api/v1`. Auto-docs at <http://localhost:8000/docs> double as a live API demo.

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Status, `data_mode`, model loaded |
| GET | `/mines` | Mine list with risk level, shortfall %, reserve P50 |
| GET | `/risk/{code}?horizon=7` | Daily fan band, drivers, weather-vs-equipment split |
| GET | `/reserves/{code}` | P10/P50/P90 tonnes, mean grade |
| POST | `/reserves/{code}/recompute` | Re-run kriging 🔑 |
| GET | `/actions?mine=` | Open recommendations, ranked by expected tonnes |
| POST | `/actions/{id}/simulate?horizon=7` | What-if forecast after applying the action |
| POST | `/actions/refresh` | Regenerate actions 🔑 |
| GET | `/prospectivity/meta` | Tile URL template + bounds for the map |
| POST | `/ingest/{production\|weather\|blasts\|equipment}` | CSV upload with validation and upsert 🔑 |

🔑 = requires `X-API-Key`.

### Data adapter (the "works on MOIL's real data" proof)

Real data drops into a fixed CSV schema, uploaded from the **Data adapter** page or `POST /ingest/{kind}`:

| kind | required columns |
|---|---|
| `production` | `mine_code,date,planned_t,actual_t` |
| `weather` | `mine_code,date,rain_mm` |
| `blasts` | `mine_code,date,delayed` |
| `equipment` | `mine_code,unit_code,date,available_hours,scheduled_hours,breakdown` |

---

## Models

| | Module | Method | Output |
|---|---|---|---|
| A | Prospectivity | LightGBM + **spatial block CV** + SHAP | probability COG → map layer |
| B | Reserve estimation | `OrdinaryKriging3D` on assays, 200 sims | P10/P50/P90 tonnes |
| C | Shortfall forecast | quantile LightGBM (0.1/0.5/0.9) on daily efficiency `actual/planned`, rolled over the weather forecast | fan chart, drivers, risk level |
| D | Recommender | rules + PuLP redeploy optimizer | ranked actions + what-if simulation |

Module C predicts *efficiency*, not tonnes, and rolls it forward over the forecast — that gives the fan chart directly. A counterfactual pass with `avail = 1.0` splits the predicted loss into **weather** vs **equipment**, which is what the "Why output drops" bar shows.

### Validation

| Module | Metric |
|---|---|
| Prospectivity | AUC-PR under spatial block CV; % of known deposits captured in top 10% of area |
| Reserves | Kriging cross-validation error; P10–P90 coverage on synthetic ground truth |
| Shortfall | Pinball loss; quantile coverage (q10–q90 should contain ≈ 80% of outcomes — printed by `make train`) |
| Recommender | Backtested tonnes recovered in the simulator vs a no-action baseline |

```bash
make test     # unit tests: optimizer + causal feature construction
```

---

## Honesty notes (say these out loud in the pitch)

- **Never** say "satellite finds manganese." Say "satellite-derived indicators rank prospective zones; drill data quantifies them."
- Prospectivity labels are **positive-unlabeled** — negatives are pseudo-absences drawn outside a buffer around known deposits.
- **Spatial leakage** is the fastest way to lose Q&A. Random CV gives fake 0.99 AUCs; `train_prospectivity.py` blocks by a 0.1° grid.
- Kriging errors are treated as independent per block, which gives a **narrower** range than a proper conditional simulation. The UI says "approximate P10–P90".
- Ops data is **synthetic** (`app/ml/synth.py`), disclosed by a badge in the UI. MOIL's real data drops straight into the CSV adapter above.
- `RECOVERABLE = 0.40` in `recommend_service.py` — the share of predicted loss an action wins back — is an **assumption to tune with MOIL**, not a measured figure.

---

## Demo script (2 minutes)

1. **Command center.** Point at the SYNTHETIC DEMO DATA badge; the adapter is ready for MOIL's real CSVs.
2. **Map:** toggle the prospectivity layer over satellite imagery ("space tech finds where to drill").
3. **Click a mine:** reserve P10/P50/P90 ("drill data says how much").
4. **Red banner:** storm in 3 days; the fan chart shows rain bars and a widening band; the loss-split bar shows the drop is weather-driven.
5. **"Simulate impact"** on *Advance blasting and pre-stock ore*: the green line lifts, header reads "+X t recovered". **This is the money shot.**
6. **Switch to Balaghat:** the redeploy action (broken unit, spare capacity elsewhere).
7. **Data adapter:** drop a CSV, forecasts refresh live.
8. **Export brief** — the one-page PDF a shift manager would actually use.
# manganese
