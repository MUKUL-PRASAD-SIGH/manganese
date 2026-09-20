MINES := KDR MNS DBZ BLG CHK
KEY   := change-me

up:       ; docker compose up -d db
seed:     ; docker compose run --rm api python -m scripts.seed_synthetic --storm
train:    ; docker compose run --rm api python -m scripts.train_all
run:      ; docker compose up -d api titiler web
reserves: ; $(foreach m,$(MINES),curl -fsS -X POST localhost:8000/api/v1/reserves/$(m)/recompute -H "X-API-Key: $(KEY)" >/dev/null && echo "kriged $(m)";)
score:    ; curl -X POST localhost:8000/api/v1/actions/refresh -H "X-API-Key: $(KEY)"
prosp:    ; docker compose run --rm api python -m scripts.predict_raster
test:     ; docker compose run --rm api pytest -q
down:     ; docker compose down
reset:    ; docker compose down -v

.PHONY: up seed train run reserves score prosp test down reset
