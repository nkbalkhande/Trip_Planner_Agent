# utils/types.py

from typing import List, Dict, TypedDict, Union


class AgentClass(TypedDict):
    sourse: str
    destination: str
    confirm_ticket: str
    return_ticket: str
    hotel: Dict[str, Union[str, int]]
    days: int
    itinerary: List[str]
    recommendation: str
    daily_budget: List[Dict[str, int]]
    total_budget: Dict[str, int]
    checkin_date: str   # ✅ Add this
    checkout_date: str  # ✅ Add this
