# tests/test_flights.py
import os
from app.db import init_db, DB_PATH
from app.main import app
from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))


client = TestClient(app)


def setup_module(module):
    # ensure DB is initialized fresh for tests
    if DB_PATH.exists():
        os.remove(DB_PATH)
    init_db()


def test_create_and_get_flight():
    payload = {
        "flight_number": "TST100",
        "origin": "AAA",
        "destination": "BBB",
        "seats_total": 100,
        "seats_available": 100
    }
    r = client.post("/flights/", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["flight_number"] == "TST100"
    fid = data["flight_id"]

    r2 = client.get(f"/flights/{fid}")
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2["origin"] == "AAA"
