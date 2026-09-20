import re

# 1. Update models.py
with open("backend/app/models.py", "r") as f: text = f.read()
if "grade_hist_x" not in text:
    text = text.replace('cutoff: Mapped[float] = mapped_column(Float)',
                        'cutoff: Mapped[float] = mapped_column(Float)\n    grade_hist_x: Mapped[list[float]] = mapped_column(JSON, default=list)\n    grade_hist_y: Mapped[list[float]] = mapped_column(JSON, default=list)')
    with open("backend/app/models.py", "w") as f: f.write(text)

# 2. Update schemas.py
with open("backend/app/schemas.py", "r") as f: text = f.read()
if "grade_hist_x" not in text:
    text = text.replace('cutoff: float',
                        'cutoff: float\n    grade_hist_x: list[float]\n    grade_hist_y: list[float]')
    with open("backend/app/schemas.py", "w") as f: f.write(text)

# 3. Update reserve_service.py to populate it
with open("backend/app/services/reserve_service.py", "r") as f: text = f.read()
if "grade_hist_x=hist_x," not in text:
    replacement = """    p10, p50, p90 = np.percentile(sims, [10, 50, 90])
    ore = gk[gk >= cutoff]
    
    hist_y, hist_edges = np.histogram(ore, bins=10, range=(cutoff, max(cutoff + 10, ore.max() if ore.size else cutoff + 10)))
    hist_x = [float((hist_edges[i] + hist_edges[i+1])/2) for i in range(len(hist_y))]
    hist_y = [float(y * vol * density) for y in hist_y]
    
    est = ReserveEstimate(mine_id=mine.id, computed_on=dt.date.today(), p10_t=float(p10), p50_t=float(p50),
                          p90_t=float(p90), mean_grade=float(ore.mean()) if ore.size else 0.0, cutoff=cutoff,
                          grade_hist_x=hist_x, grade_hist_y=hist_y)
"""
    text = re.sub(r'    p10, p50, p90 = np\.percentile.*?est = ReserveEstimate.*?cutoff=cutoff\)', replacement, text, flags=re.DOTALL)
    with open("backend/app/services/reserve_service.py", "w") as f: f.write(text)
