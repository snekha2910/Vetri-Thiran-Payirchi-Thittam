from typing import Optional, Dict, Any, List
from pydantic import Field
from app.schemas.common import BaseSchema

class ShoppingLink(BaseSchema):
    name: str
    url: str = "#"
    icon: Optional[str] = None

class Recommendation(BaseSchema):
    id: Optional[str] = None
    plan_id: Optional[str] = None
    planId: Optional[str] = None
    name: str
    category: str = ""
    source: Optional[str] = None
    source_url: Optional[str] = None
    sourceUrl: Optional[str] = None
    price: float = 0.0
    currency: str = "INR"
    quantity: int = 1
    image_url: Optional[str] = None
    imageUrl: Optional[str] = None
    description: str = ""
    style: Optional[str] = None
    why_recommended: str = ""
    whyRecommended: Optional[str] = ""
    match_score: float = Field(0.0, ge=0.0, le=100.0)
    matchScore: Optional[float] = None
    budget_impact: str = "medium"  # low | medium | high
    budgetImpact: Optional[str] = "medium"
    shopping_links: List[ShoppingLink] = Field(default_factory=list)
    shoppingLinks: Optional[List[ShoppingLink]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    saved: bool = False
    is_saved: bool = False
    created_at: Optional[str] = None
    createdAt: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        self.planId = self.plan_id or data.get("planId")
        self.sourceUrl = self.source_url or data.get("sourceUrl")
        self.imageUrl = self.image_url or data.get("imageUrl")
        self.whyRecommended = self.why_recommended or data.get("whyRecommended", "")
        self.matchScore = self.match_score if self.matchScore is None else self.matchScore
        self.budgetImpact = self.budget_impact or data.get("budgetImpact", "medium")
        self.saved = self.is_saved or data.get("saved", False)
        self.is_saved = self.saved
        self.createdAt = self.created_at or data.get("createdAt")
        self.shoppingLinks = self.shopping_links if self.shopping_links else data.get("shoppingLinks", [])
        self.shopping_links = self.shoppingLinks
        self.quantity = data.get("quantity", 1)
        self.style = data.get("style", self.style)
