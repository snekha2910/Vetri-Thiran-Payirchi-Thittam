from typing import List, Optional, Any, Dict
from pydantic import Field, field_validator
from app.schemas.common import BaseSchema

class RoomItem(BaseSchema):
    name: str = "Living Room"
    quantity: int = 1
    notes: Optional[str] = None

class RequirementItem(BaseSchema):
    category: str = "Furniture"
    quantity: int = 1
    priority: str = "medium"
    preferred_style: Optional[str] = None
    preferredStyle: Optional[str] = None

class HomePlannerRequest(BaseSchema):
    title: Optional[str] = None
    total_budget: float = Field(..., gt=0, alias="totalBudget")
    currency: str = "INR"
    flexibility: str = "flexible"
    budget_flexibility: Optional[str] = None
    rooms: List[RoomItem] = Field(default_factory=list)
    requirements: List[RequirementItem] = Field(default_factory=list)
    room_type: Optional[str] = None
    roomType: Optional[str] = None
    room_size_sqft: Optional[float] = None
    roomSizeSqft: Optional[float] = None
    style: Optional[str] = "Modern"
    color_preference: Optional[str] = Field(None, alias="colorPreference")
    color_preferences: List[str] = Field(default_factory=list)
    quality_preference: Optional[str] = Field(None, alias="qualityPreference")
    brand_preference: Optional[str] = Field(None, alias="brandPreference")
    other_requirements: Optional[str] = Field(None, alias="otherRequirements")
    special_requirements: Optional[str] = None
    key_priorities: List[str] = Field(default_factory=list)

    def __init__(self, **data):
        # Handle field aliases before initialization
        if "totalBudget" in data and "total_budget" not in data:
            data["total_budget"] = data["totalBudget"]
        if "flexibility" in data and "budget_flexibility" not in data:
            data["budget_flexibility"] = data["flexibility"]
        if "budget_flexibility" in data and "flexibility" not in data:
            data["flexibility"] = data["budget_flexibility"]
        if "room_type" not in data and "rooms" in data and len(data["rooms"]) > 0:
            first_room = data["rooms"][0]
            data["room_type"] = first_room.get("name") if isinstance(first_room, dict) else getattr(first_room, "name", "living_room")
        if "room_type" not in data:
            data["room_type"] = "living_room"
        if not data.get("title"):
            room_count = len(data.get("rooms", []))
            data["title"] = f"Home setup plan · {room_count or 1} room{'s' if room_count != 1 else ''}"
        super().__init__(**data)
