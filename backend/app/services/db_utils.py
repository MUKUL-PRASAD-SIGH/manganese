from sqlalchemy.dialects.postgresql import insert as pg_insert


def upsert(db, Model, rows: list[dict], keys: list[str], cols: list[str] | None = None):
    if not rows:
        return
    cols_ = cols or [c for c in rows[0] if c not in keys]
    for i in range(0, len(rows), 5000):
        stmt = pg_insert(Model).values(rows[i:i + 5000])
        upd = {c: stmt.excluded[c] for c in cols_}
        db.execute(stmt.on_conflict_do_update(index_elements=keys, set_=upd) if upd
                   else stmt.on_conflict_do_nothing())
    db.commit()
