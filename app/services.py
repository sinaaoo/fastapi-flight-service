# app/services.py
from typing import Dict, Any, Tuple, List, Optional
from . import repositories
from .repositories import ALLOWED_SORT_COLUMNS
from typing import Optional

class FlightService:
    @staticmethod
    def create_flight(payload: Dict[str, Any]) -> Dict[str, Any]:
        # set created/updated timestamps in DB with default values or use passed ones
        return repositories.create_flight(payload)

    @staticmethod
    def get_flight(flight_id: int) -> Optional[Dict[str, Any]]:
        return repositories.get_flight(flight_id)

    @staticmethod
    def delete_flight(flight_id: int) -> bool:
        return repositories.delete_flight(flight_id)

    @staticmethod
    def update_flight(flight_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return repositories.update_flight(flight_id, updates)

    @staticmethod
    def list_flights(page: int, size: int, filters: Dict[str, Any], sort_by: str, sort_order: str, fields: Optional[str]):
        return repositories.list_flights(
        page=page,
        size=size,
        filters=filters,
        sort_by=sort_by,
        sort_order=sort_order,
        fields=fields
    )



class AuditService:
    @staticmethod
    def register_change(flight_id: int, changed_by: str, change_summary: str, old_data: Dict = None, new_data: Dict = None) -> int:
        return repositories.insert_flight_log(flight_id, changed_by, change_summary, old_data, new_data)
