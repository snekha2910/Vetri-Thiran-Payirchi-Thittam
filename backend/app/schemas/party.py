from typing import List, Optional
from pydantic import Field
from app.schemas.common import BaseSchema

class PartyPlannerRequest(BaseSchema):
    title: Optional[str] = None
    total_budget: float = Field(..., gt=0, alias="totalBudget")
    currency: str = "INR"
    guest_count: int = Field(..., gt=0, alias="guestCount")
    event_type: Optional[str] = Field(None, alias="eventType")
    party_type: Optional[str] = None
    venue_type: Optional[str] = Field("indoor", alias="venueType")
    event_date: Optional[str] = Field(None, alias="eventDate")
    food_preference: Optional[str] = Field(None, alias="foodPreference")
    catering_preference: Optional[str] = None
    decoration_preference: Optional[str] = Field(None, alias="decorationPreference")
    entertainment_preference: Optional[str] = Field(None, alias="entertainmentPreference")
    location: Optional[str] = None
    additional_requirements: Optional[str] = Field(None, alias="additionalRequirements")
    special_requirements: Optional[str] = None
    flexibility: str = "flexible"
    budget_flexibility: Optional[str] = None
    key_priorities: List[str] = Field(default_factory=list)

    def __init__(self, **data):
        if "totalBudget" in data and "total_budget" not in data:
            data["total_budget"] = data["totalBudget"]
        if "guestCount" in data and "guest_count" not in data:
            data["guest_count"] = data["guestCount"]
        if "eventType" in data and "party_type" not in data:
            data["party_type"] = data["eventType"]
        if "event_type" in data and "party_type" not in data:
            data["party_type"] = data["event_type"]
        if "party_type" not in data:
            data["party_type"] = "birthday"
        if "foodPreference" in data and "catering_preference" not in data:
            data["catering_preference"] = data["foodPreference"]
        if "flexibility" in data and "budget_flexibility" not in data:
            data["budget_flexibility"] = data["flexibility"]
        if "budget_flexibility" in data and "flexibility" not in data:
            data["flexibility"] = data["budget_flexibility"]
        if not data.get("title"):
            data["title"] = f"{str(data.get('party_type', 'Party')).capitalize()} · {data.get('guest_count', 0)} guests"
        super().__init__(**data)
