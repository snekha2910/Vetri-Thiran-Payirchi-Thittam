from typing import Optional
from pydantic import Field
from app.schemas.common import BaseSchema

class JewelryPlannerRequest(BaseSchema):
    title: Optional[str] = None
    total_budget: float = Field(..., gt=0, alias="totalBudget")
    currency: str = "INR"
    occasion: str = "party"
    jewelry_type: str = Field("set", alias="jewelryType")
    style: str = "Contemporary"
    metal_preference: Optional[str] = Field("gold", alias="metalPreference")
    color_preference: Optional[str] = Field(None, alias="colorPreference")
    additional_requirements: Optional[str] = Field(None, alias="additionalRequirements")
    special_requirements: Optional[str] = None
    outfit_image_name: Optional[str] = Field(None, alias="outfitImageName")
    outfit_image_url: Optional[str] = Field(None, alias="outfitImageUrl")
    outfit_storage_path: Optional[str] = Field(None, alias="outfitStoragePath")
    outfit_description: Optional[str] = Field(None, alias="outfitDescription")
    skin_tone: Optional[str] = Field(None, alias="skinTone")
    flexibility: str = "flexible"
    budget_flexibility: Optional[str] = None

    def __init__(self, **data):
        if "totalBudget" in data and "total_budget" not in data:
            data["total_budget"] = data["totalBudget"]
        if "jewelryType" in data and "jewelry_type" not in data:
            data["jewelry_type"] = data["jewelryType"]
        if "metalPreference" in data and "metal_preference" not in data:
            data["metal_preference"] = data["metalPreference"]
        if "flexibility" in data and "budget_flexibility" not in data:
            data["budget_flexibility"] = data["flexibility"]
        if "budget_flexibility" in data and "flexibility" not in data:
            data["flexibility"] = data["budget_flexibility"]
        if not data.get("title"):
            data["title"] = f"{str(data.get('occasion', 'Styling')).capitalize()} · {str(data.get('jewelry_type', 'Jewelry')).capitalize()}"
        super().__init__(**data)
