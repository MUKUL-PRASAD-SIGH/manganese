from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Mine


def get_mine(code: str, db: Session = Depends(get_db)) -> Mine:
    m = db.scalars(select(Mine).where(Mine.code == code)).first()
    if not m:
        raise HTTPException(404, f"unknown mine {code}")
    return m
