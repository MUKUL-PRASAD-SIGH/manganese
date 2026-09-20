#!/bin/bash
source venv/bin/activate
export PYTHONPATH=backend
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1
