# app/db.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "flights.db"

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS flights (
    flight_id INTEGER PRIMARY KEY,
    flight_number TEXT NOT NULL,
    origin TEXT NOT NULL,
    destination TEXT NOT NULL,
    departure_time TEXT,
    arrival_time TEXT,
    duration_minutes INTEGER,
    aircraft_type TEXT,
    seats_total INTEGER,
    seats_available INTEGER,
    status TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    process_id TEXT
);

CREATE TABLE IF NOT EXISTS flight_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flight_id INTEGER,
    changed_at TEXT DEFAULT (datetime('now')),
    changed_by TEXT,
    change_summary TEXT,
    old_data TEXT,
    new_data TEXT,
    FOREIGN KEY (flight_id) REFERENCES flights(flight_id) ON DELETE CASCADE
);
"""


def init_db():
    con = sqlite3.connect(str(DB_PATH), check_same_thread=False, timeout=10)
    con.executescript(SCHEMA_SQL)
    con.commit()
    con.close()


def get_connection() -> sqlite3.Connection:
    con = sqlite3.connect(str(DB_PATH), check_same_thread=False, timeout=10)
    con.row_factory = sqlite3.Row  # مهم‌ترین بخش برای جلوگیری از خطای 500 هنگام SELECT ستون‌های خاص
    return con