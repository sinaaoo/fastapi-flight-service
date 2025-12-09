# app/sample_data_loader.py
import json
from .db import DB_PATH, init_db, get_connection
from pathlib import Path


def load_sample(path: Path):
    init_db()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    con = get_connection()
    cur = con.cursor()
    for item in data:
        cols = ", ".join(item.keys())
        placeholders = ", ".join("?" for _ in item)
        cur.execute(f"INSERT OR REPLACE INTO flights ({cols}) VALUES ({placeholders})", tuple(
            item.values()))
    con.commit()
    con.close()


if __name__ == "__main__":
    load_sample(Path(__file__).resolve().parent.parent / "flights_sample.json")
    print("sample data loaded")
