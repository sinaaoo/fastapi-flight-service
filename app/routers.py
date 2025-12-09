# app/routers.py

from fastapi import APIRouter, HTTPException, Query, status
from typing import Optional, List
from pydantic import BaseModel
from .models import FlightCreate, FlightOut, FlightUpdate
from .services import FlightService, AuditService
from typing import Optional
import logging

router = APIRouter(prefix="/flights", tags=["flights"])
logger = logging.getLogger(__name__)


# -----------------------------
# Helper: validate sort column
# -----------------------------
def _validate_sort_by(sort_by: str):
    from .repositories import ALLOWED_SORT_COLUMNS
    if sort_by not in ALLOWED_SORT_COLUMNS:
        raise HTTPException(
            status_code=400, detail=f"invalid sort column: {sort_by}"
        )


# -----------------------------
# Create Flight
# -----------------------------
@router.post("/", response_model=FlightOut, status_code=status.HTTP_201_CREATED)
def create_flight(payload: FlightCreate):
    try:
        obj = FlightService.create_flight(payload.dict(exclude_none=True))
        return obj
    except Exception as e:
        logger.exception("Error in POST /flights")
        raise HTTPException(status_code=500, detail=str(e))


# -----------------------------
# List Flights (Dynamic Fields)
# -----------------------------
#     ❗ response_model را حذف می‌کنیم تا با fields=... سازگار شود
# -----------------------------
@router.get("/")
def list_flights(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = Query("flight_id"),
    sort_order: str = Query("asc"),
    fields: Optional[str] = Query(None)
):

    _validate_sort_by(sort_by)

    filters = {}
    if origin:
        filters["origin"] = origin
    if destination:
        filters["destination"] = destination
    if status:
        filters["status"] = status

    try:
        rows, total = FlightService.list_flights(
            page=page,
            size=size,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            fields=fields
        )

        return {
            "page": page,
            "size": size,
            "total": total,
            "items": rows
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.exception("Error in GET /flights")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# -----------------------------
# Paginated List
# -----------------------------
@router.get("/paginated")
def list_flights_with_meta(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=200),
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: str = Query("flight_id"),
    sort_order: str = Query("asc"),
    fields: Optional[str] = Query(None)
):

    _validate_sort_by(sort_by)

    filters = {}
    if origin:
        filters["origin"] = origin
    if destination:
        filters["destination"] = destination
    if status:
        filters["status"] = status

    try:
        rows, total = FlightService.list_flights(
            page=page,
            size=size,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            fields=fields
        )

        return {
            "page": page,
            "size": size,
            "total": total,
            "items": rows
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.exception("Error in GET /flights/paginated")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# -----------------------------
# Get Single Flight
# -----------------------------
@router.get("/{flight_id}", response_model=FlightOut)
def get_flight(flight_id: int):
    try:
        row = FlightService.get_flight(flight_id)
        if not row:
            raise HTTPException(status_code=404, detail="flight not found")
        return row
    except Exception as e:
        logger.exception("Error in GET /flights/{flight_id}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# -----------------------------
# PUT - Full update
# -----------------------------
@router.put("/{flight_id}", response_model=FlightOut)
def replace_flight(flight_id: int, payload: FlightCreate):
    existing = FlightService.get_flight(flight_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="flight not found")

    try:
        updated = FlightService.update_flight(
            flight_id, payload.dict(exclude_none=True)
        )
        AuditService.register_change(
            flight_id,
            changed_by="system",
            change_summary="replace",
            old_data=existing,
            new_data=updated
        )
        return updated

    except Exception as e:
        logger.exception("Error in PUT /flights/{flight_id}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# -----------------------------
# PATCH - Partial update
# -----------------------------
@router.patch("/{flight_id}", response_model=FlightOut)
def patch_flight(flight_id: int, payload: FlightUpdate):
    existing = FlightService.get_flight(flight_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="flight not found")

    try:
        updated = FlightService.update_flight(
            flight_id, payload.dict(exclude_none=True)
        )
        AuditService.register_change(
            flight_id,
            changed_by="system",
            change_summary="patch",
            old_data=existing,
            new_data=updated
        )
        return updated

    except Exception as e:
        logger.exception("Error in PATCH /flights/{flight_id}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# -----------------------------
# DELETE
# -----------------------------
@router.delete("/{flight_id}", status_code=204)
def delete_flight(flight_id: int):
    try:
        ok = FlightService.delete_flight(flight_id)
        if not ok:
            raise HTTPException(status_code=404, detail="flight not found")
        return
    except Exception as e:
        logger.exception("Error in DELETE /flights/{flight_id}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# -----------------------------
# Register Flight Log Action
# -----------------------------
class RegisterPayload(BaseModel):
    changed_by: str
    new_status: Optional[str] = None
    seats_available_delta: Optional[int] = None
    note: Optional[str] = None


@router.post("/{flight_id}/register", response_model=FlightOut)
def register_flight_action(flight_id: int, payload: RegisterPayload):
    existing = FlightService.get_flight(flight_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="flight not found")

    updates = {}
    summary_parts = []

    if payload.new_status:
        updates["status"] = payload.new_status
        summary_parts.append(f"status -> {payload.new_status}")

    if payload.seats_available_delta is not None:
        new_seats = (existing.get("seats_available") or 0) + payload.seats_available_delta
        updates["seats_available"] = new_seats
        summary_parts.append(f"seats_available -> {new_seats}")

    if not updates:
        raise HTTPException(status_code=400, detail="nothing to update in register")

    try:
        updated = FlightService.update_flight(flight_id, updates)
        change_summary = f"register: {'; '.join(summary_parts)}"

        AuditService.register_change(
            flight_id,
            changed_by=payload.changed_by,
            change_summary=change_summary,
            old_data=existing,
            new_data=updated
        )

        return updated

    except Exception as e:
        logger.exception("Error in POST /flights/{flight_id}/register")
        raise HTTPException(status_code=500, detail="Internal Server Error")