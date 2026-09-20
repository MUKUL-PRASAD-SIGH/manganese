import re

# 1. Update recommend_service.py
with open("backend/app/services/recommend_service.py", "r") as f: text = f.read()

replacement1 = """
    units = [dict(id=u.code, home=by_id[u.home_mine_id].code, tpd=u.tpd, type=u.type)
             for u in units_db if not latest.get(u.code, False)]
    slots = {m.code: sum(1 for u in units_db if u.home_mine_id == m.id) for m in mines}
"""
text = re.sub(r'    units = \[dict.*?slots = \{.*?\}', replacement1, text, flags=re.DOTALL)
with open("backend/app/services/recommend_service.py", "w") as f: f.write(text)

# 2. Update optimizer.py to enforce types
with open("backend/app/ml/optimizer.py", "r") as f: opt_text = f.read()

if 'prob += pl.lpSum(x[u["id"], m] for u in units if u.get("type") == "dumper") >=' not in opt_text:
    opt_replacement = """
    for m in mines:
        prob += pl.lpSum(x[u["id"], m] for u in units) <= slots[m]
        # Transport constraint: dumpers >= excavators * 3
        dumper_expr = pl.lpSum(x[u["id"], m] for u in units if u.get("type", "dumper") == "dumper")
        excavator_expr = pl.lpSum(x[u["id"], m] for u in units if u.get("type", "") == "excavator")
        prob += dumper_expr >= excavator_expr * 3
"""
    opt_text = opt_text.replace('    for m in mines:\n        prob += pl.lpSum(x[u["id"], m] for u in units) <= slots[m]', opt_replacement)
    with open("backend/app/ml/optimizer.py", "w") as f: f.write(opt_text)

