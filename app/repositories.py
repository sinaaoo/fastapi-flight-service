# app/repositories.py

import sqlite3
import json
import logging
from typing import List, Dict, Any, Tuple, Optional
from .db import get_connection

# setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Allowed columns for sorting to prevent SQL injection
ALLOWED_SORT_COLUMNS = {
    "flight_id", "flight_number", "origin", "destination",
    "departure_time", "arrival_time", "duration_minutes",
    "aircraft_type", "seats_total", "seats_available",
    "status", "created_at", "updated_at", "process_id"
}

# Allowed fields for dynamic SELECT
ALLOWED_SELECT_COLUMNS = ALLOWED_SORT_COLUMNS.copy()


def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return dict(row)


# -----------------------
#       CRUD OPERATIONS
# -----------------------

def create_flight(data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        con = get_connection()
        cur = con.cursor()

        cols = ", ".join(data.keys())
        placeholders = ", ".join("?" for _ in data)
        values = list(data.values())

        sql = f"INSERT INTO flights ({cols}) VALUES ({placeholders})"
        logger.debug(f"Executing SQL: {sql} with values: {values}")

        cur.execute(sql, values)
        con.commit()

        flight_id = cur.lastrowid
        cur.execute("SELECT * FROM flights WHERE flight_id = ?", (flight_id,))
        row = cur.fetchone()

        return _row_to_dict(row)

    except Exception as e:
        logger.exception("Error in create_flight")
        raise RuntimeError(f"Database error: {e}")

    finally:
        con.close()


def get_flight(flight_id: int) -> Optional[Dict[str, Any]]:
    try:
        con = get_connection()
        cur = con.cursor()

        cur.execute("SELECT * FROM flights WHERE flight_id = ?", (flight_id,))
        row = cur.fetchone()

        return _row_to_dict(row) if row else None

    except Exception as e:
        logger.exception("Error in get_flight")
        raise RuntimeError(f"Database error: {e}")

    finally:
        con.close()


def delete_flight(flight_id: int) -> bool:
    try:
        con = get_connection()
        cur = con.cursor()

        cur.execute("DELETE FROM flights WHERE flight_id = ?", (flight_id,))
        con.commit()

        return cur.rowcount > 0

    except Exception as e:
        logger.exception("Error in delete_flight")
        raise RuntimeError(f"Database error: {e}")

    finally:
        con.close()


def update_flight(flight_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    try:
        con = get_connection()
        cur = con.cursor()

        set_clause = ", ".join(f"{k}=?" for k in updates.keys())
        values = list(updates.values()) + [flight_id]

        sql = f"""
            UPDATE flights
            SET {set_clause}, updated_at = datetime('now')
            WHERE flight_id = ?
        """

        logger.debug(f"Executing SQL: {sql} with {values}")

        cur.execute(sql, values)
        con.commit()

        cur.execute("SELECT * FROM flights WHERE flight_id = ?", (flight_id,))
        row = cur.fetchone()

        return _row_to_dict(row) if row else None

    except Exception as e:
        logger.exception("Error in update_flight")
        raise RuntimeError(f"Database error: {e}")

    finally:
        con.close()


# -----------------------
#       LIST / FILTER
# -----------------------

def list_flights(
    page: int = 1,
    size: int = 20,
    filters: Dict[str, Any] = None,
    sort_by: str = "flight_id",
    sort_order: str = "asc",
    fields: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], int]:

    filters = filters or {}

    # ---------------------
    # FIELD PROJECTION
    # ---------------------
    if fields:
        field_list = [f.strip() for f in fields.split(",") if f.strip()]
        for f in field_list:
            if f not in ALLOWED_SELECT_COLUMNS:
                raise ValueError(f"Invalid field name: {f}")
        select_clause = ", ".join(field_list)
    else:
        select_clause = "*"

    # ---------------------
    # SORT VALIDATION
    # ---------------------
    if sort_by not in ALLOWED_SORT_COLUMNS:
        raise ValueError("Invalid sort column")
    if sort_order.lower() not in ("asc", "desc"):
        raise ValueError("Invalid sort order")

    # ---------------------
    # WHERE
    # ---------------------
    where_clauses = []
    params = []

    for k, v in filters.items():
        if k in {"origin", "destination", "status", "flight_number"}:
            where_clauses.append(f"{k} = ?")
            params.append(v)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    # ---------------------
    # COUNT
    # ---------------------
    try:
        con = get_connection()
        cur = con.cursor()

        count_sql = f"SELECT COUNT(*) AS cnt FROM flights {where_sql}"
        logger.debug(f"COUNT SQL: {count_sql} with params {params}")

        cur.execute(count_sql, params)
        total = cur.fetchone()["cnt"]

        # ---------------------
        # PAGINATION + MAIN QUERY
        # ---------------------
        offset = (page - 1) * size

        sql = f"""
            SELECT {select_clause}
            FROM flights
            {where_sql}
            ORDER BY {sort_by} {sort_order.upper()}
            LIMIT ? OFFSET ?
        """

        logger.debug(f"QUERY SQL: {sql} with params {params + [size, offset]}")

        cur.execute(sql, params + [size, offset])
        rows = cur.fetchall()

        return [_row_to_dict(r) for r in rows], total

    except sqlite3.Error as e:
        logger.exception("SQLite error in list_flights")
        raise RuntimeError(f"Database error: {e}")

    except Exception as e:
        logger.exception("Unexpected error in list_flights")
        raise RuntimeError(f"Unexpected error: {e}")

    finally:
        con.close()


# -----------------------
#      LOGGING
# -----------------------

def insert_flight_log(
    flight_id: int,
    changed_by: str,
    change_summary: str,
    old_data: Optional[Dict],
    new_data: Optional[Dict]
) -> int:

    try:
        con = get_connection()
        cur = con.cursor()

        cur.execute(
            """
            INSERT INTO flight_logs
            (flight_id, changed_by, change_summary, old_data, new_data)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                flight_id,
                changed_by,
                change_summary,
                json.dumps(old_data, default=str) if old_data else None,
                json.dumps(new_data, default=str) if new_data else None,
            ),
        )

        con.commit()
        return cur.lastrowid

    except Exception as e:
        logger.exception("Error in insert_flight_log")
        raise RuntimeError(f"Database error: {e}")

    finally:
        con.close()
