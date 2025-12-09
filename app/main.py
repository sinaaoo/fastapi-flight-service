# app/main.py
from fastapi import FastAPI
from .routers import router as flights_router
from .db import init_db
from .sample_data_loader import load_sample
from pathlib import Path

app = FastAPI(title="Flights API (raw SQL, layered)")

app.include_router(flights_router)


@app.on_event("startup")
def startup():
    # initialize DB and optionally load sample data if DB empty
    init_db()
    db_file = Path(__file__).resolve().parent.parent / "flights.db"
    # If empty, try load sample (safe check)
    from .db import get_connection
    con = get_connection()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM flights")
    cnt = cur.fetchone()["cnt"]
    con.close()
    if cnt == 0:
        sample_path = Path(__file__).resolve(
        ).parent.parent / "flights_sample.json"
        if sample_path.exists():
            load_sample(sample_path)
