from typing import List, Optional, Dict, Any
from pydantic import Field
from app.schemas.common import BaseSchema, CategoryAllocation, BudgetCalculation
from app.schemas.recommendation import Recommendation

class BudgetSummary(BudgetCalculation):
    pass

class OutfitAnalysis(BaseSchema):
    colors: List[str] = Field(default_factory=lambda: ["blue", "white"])
    style: str = "casual"
    formality: str = "informal"

class VenueSuggestion(BaseSchema):
    name: str = "Home"
    type: str = "Residential"
    location: Optional[str] = None
    cost: float = 0.0
    website: Optional[str] = "#"
    map_url: Optional[str] = "#"
    mapUrl: Optional[str] = "#"

class PlanSummaryResponse(BaseSchema):
    id: str
    user_id: Optional[str] = None
    userId: Optional[str] = None
    planner_type: str = "home"
    plannerType: Optional[str] = "home"
    title: str = ""
    budget: float = 0.0
    total_budget: Optional[float] = 0.0
    totalBudget: Optional[float] = 0.0
    estimated_cost: float = 0.0
    estimatedCost: Optional[float] = 0.0
    remaining_budget: float = 0.0
    remaining: Optional[float] = 0.0
    currency: str = "INR"
    status: str = "completed"
    created_at: Optional[str] = None
    createdAt: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        b = data.get("budget", data.get("total_budget", data.get("totalBudget", 0.0)))
        e = data.get("estimated_cost", data.get("estimatedCost", 0.0))
        r = data.get("remaining_budget", data.get("remaining", float(b) - float(e)))
        pt = data.get("planner_type", data.get("plannerType", "home"))
        uid = data.get("user_id", data.get("userId", ""))
        ca = data.get("created_at", data.get("createdAt", ""))

        self.user_id = uid
        self.userId = uid
        self.planner_type = pt
        self.plannerType = pt
        self.budget = float(b)
        self.total_budget = float(b)
        self.totalBudget = float(b)
        self.estimated_cost = float(e)
        self.estimatedCost = float(e)
        self.remaining_budget = float(r)
        self.remaining = float(r)
        self.created_at = ca
        self.createdAt = ca

class PlanDetailResponse(BaseSchema):
    id: str
    plan_id: Optional[str] = None
    user_id: Optional[str] = None
    userId: Optional[str] = None
    planner_type: str = "home"
    plannerType: Optional[str] = "home"
    title: str = ""
    budget: BudgetSummary
    budget_summary: Optional[BudgetSummary] = None
    allocations: List[CategoryAllocation] = Field(default_factory=list)
    ai_summary: str = ""
    aiSummary: Optional[str] = ""
    warnings: List[str] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)
    additional_suggestions: List[str] = Field(default_factory=list)
    additionalSuggestions: Optional[List[str]] = None
    styling_tips: List[str] = Field(default_factory=list)
    stylingTips: Optional[List[str]] = None
    outfit_analysis: Optional[OutfitAnalysis] = None
    outfitAnalysis: Optional[OutfitAnalysis] = None
    venue_suggestions: List[VenueSuggestion] = Field(default_factory=list)
    venueSuggestions: Optional[List[VenueSuggestion]] = None
    input_data: Dict[str, Any] = Field(default_factory=dict)
    inputData: Optional[Dict[str, Any]] = None
    status: str = "completed"
    partial: bool = False
    created_at: Optional[str] = None
    createdAt: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        pid = data.get("id", data.get("plan_id", ""))
        self.id = pid
        self.plan_id = pid
        self.budget_summary = self.budget
        self.aiSummary = self.ai_summary or data.get("aiSummary", "")
        self.ai_summary = self.aiSummary
        self.plannerType = self.planner_type or data.get("plannerType", "home")
        self.planner_type = self.plannerType
        self.userId = self.user_id or data.get("userId", "")
        self.inputData = self.input_data
        self.createdAt = self.created_at or data.get("createdAt", "")
        self.created_at = self.createdAt
        
        # Additional suggestions & styling tips
        add_sugg = data.get("additional_suggestions", data.get("additionalSuggestions", []))
        self.additional_suggestions = add_sugg
        self.additionalSuggestions = add_sugg
        
        tips = data.get("styling_tips", data.get("stylingTips", []))
        self.styling_tips = tips
        self.stylingTips = tips

        # Outfit analysis
        oa = data.get("outfit_analysis", data.get("outfitAnalysis"))
        if oa:
            self.outfit_analysis = OutfitAnalysis(**oa) if isinstance(oa, dict) else oa
            self.outfitAnalysis = self.outfit_analysis

        # Venue suggestions
        vs = data.get("venue_suggestions", data.get("venueSuggestions", []))
        self.venue_suggestions = [VenueSuggestion(**v) if isinstance(v, dict) else v for v in vs]
        self.venueSuggestions = self.venue_suggestions
