from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")

class BaseSchema(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        extra="allow"
    )

class ApiResponse(BaseSchema, Generic[T]):
    status: str = "success"
    data: Optional[T] = None
    message: Optional[str] = None

class CategoryAllocation(BaseSchema):
    category: str
    amount: float = 0.0
    allocated_amount: Optional[float] = None
    percentage: float = 0.0
    description: Optional[str] = None

    def __init__(self, **data):
        if "allocated_amount" in data and "amount" not in data:
            data["amount"] = data["allocated_amount"]
        elif "amount" in data and "allocated_amount" not in data:
            data["allocated_amount"] = data["amount"]
        super().__init__(**data)

class BudgetCalculation(BaseSchema):
    budget: float = 0.0
    total_budget: Optional[float] = None
    totalBudget: Optional[float] = None
    estimated_cost: float = 0.0
    estimatedCost: Optional[float] = None
    remaining_budget: float = 0.0
    remaining: Optional[float] = None
    savings: Optional[float] = 0.0
    percentage_used: float = 0.0
    utilization: Optional[float] = None
    currency: str = "INR"
    is_over_budget: bool = False

    def __init__(self, **data):
        super().__init__(**data)
        b = data.get("budget", data.get("total_budget", data.get("totalBudget", 0.0)))
        e = data.get("estimated_cost", data.get("estimatedCost", 0.0))
        r = data.get("remaining_budget", data.get("remaining", b - e))
        u = data.get("percentage_used", data.get("utilization", (e / b * 100) if b > 0 else 0.0))

        self.budget = float(b)
        self.total_budget = float(b)
        self.totalBudget = float(b)
        self.estimated_cost = float(e)
        self.estimatedCost = float(e)
        self.remaining_budget = float(r)
        self.remaining = float(r)
        self.savings = max(float(r), 0.0)
        self.percentage_used = float(u)
        self.utilization = round(float(u))
        self.currency = data.get("currency", "INR")
        self.is_over_budget = float(r) < 0
