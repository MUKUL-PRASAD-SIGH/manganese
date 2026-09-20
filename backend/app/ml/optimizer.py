import pulp as pl


def _solve(units, slots, value, allow_move):
    prob = pl.LpProblem("redeploy", pl.LpMaximize)
    mines = list(slots)
    x = {(u["id"], m): pl.LpVariable(f"x_{u['id']}_{m}", cat="Binary") for u in units for m in mines}
    prob += pl.lpSum(x[u["id"], m] * value(u, m) for u in units for m in mines)
    for u in units:
        prob += pl.lpSum(x[u["id"], m] for m in mines) <= 1
        if not allow_move:
            for m in mines:
                if m != u["home"]:
                    prob += x[u["id"], m] == 0

    for m in mines:
        prob += pl.lpSum(x[u["id"], m] for u in units) <= slots[m]
        # Transport constraint: dumpers >= excavators * 3
        dumper_expr = pl.lpSum(x[u["id"], m] for u in units if u.get("type", "dumper") == "dumper")
        excavator_expr = pl.lpSum(x[u["id"], m] for u in units if u.get("type", "") == "excavator")
        prob += dumper_expr >= excavator_expr * 3

    prob.solve(pl.PULP_CBC_CMD(msg=0))
    assign = {u["id"]: next((m for m in mines if (x[u["id"], m].value() or 0) > 0.5), None) for u in units}
    return assign, float(pl.value(prob.objective) or 0.0)


def redeploy(units, slots, weather_loss, horizon=7, transfer_loss=0.10, min_gain_t=100):
    """units: [{id, home, tpd}] healthy only. slots: {mine: n units it needs}.
    weather_loss: {mine: 0..1} weather-only loss (equipment-neutral)."""
    def value(u, m):
        return u["tpd"] * horizon * (1 - weather_loss[m]) * (1 - (transfer_loss if m != u["home"] else 0.0))

    _, base_obj = _solve(units, slots, value, allow_move=False)
    best, best_obj = _solve(units, slots, value, allow_move=True)
    gain = best_obj - base_obj
    if gain < min_gain_t:
        return {"moves": [], "expected_tonnes": 0.0}
    moves = [{"unit": u["id"], "from": u["home"], "to": best[u["id"]]}
             for u in units if best[u["id"]] not in (None, u["home"])]
    return {"moves": moves, "expected_tonnes": gain}
