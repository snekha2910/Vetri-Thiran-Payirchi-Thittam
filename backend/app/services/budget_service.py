from typing import List
from app.schemas.common import BudgetCalculation, CategoryAllocation

ALLOCATION_RULES = {
    "home": [
        {"category": "Furniture", "percentage": 50.0, "description": "Core seating, tables, storage"},
        {"category": "Lighting", "percentage": 15.0, "description": "Ambient, task, and accent lighting"},
        {"category": "Decor & Textiles", "percentage": 20.0, "description": "Rugs, curtains, art, cushions"},
        {"category": "Hardware & Accents", "percentage": 15.0, "description": "Fixtures, planters, accessories"}
    ],
    "party": [
        {"category": "Catering & Drinks", "percentage": 45.0, "description": "Food, appetizers, beverages, cake"},
        {"category": "Decor & Theme", "percentage": 25.0, "description": "Balloons, lighting, tableware, signage"},
        {"category": "Entertainment & Music", "percentage": 20.0, "description": "DJ, games, sound system"},
        {"category": "Favors & Extras", "percentage": 10.0, "description": "Return gifts, disposable supplies"}
    ],
    "jewelry": [
        {"category": "Primary Statement Piece", "percentage": 55.0, "description": "Main necklace, choker, or bridal set"},
        {"category": "Earrings & Drops", "percentage": 25.0, "description": "Coordinated earrings"},
        {"category": "Bangles & Rings", "percentage": 20.0, "description": "Wrist and hand accessories"}
    ]
}

class BudgetService:
    @staticmethod
    def calculate(budget: float, estimated_cost: float, currency: str = "INR") -> BudgetCalculation:
        budget = float(budget)
        estimated_cost = round(float(estimated_cost), 2)
        remaining = round(budget - estimated_cost, 2)
        percentage_used = round((estimated_cost / budget * 100), 1) if budget > 0 else 0.0
        is_over = remaining < 0

        return BudgetCalculation(
            budget=budget,
            estimated_cost=estimated_cost,
            remaining_budget=remaining,
            percentage_used=percentage_used,
            currency=currency,
            is_over_budget=is_over
        )

    @staticmethod
    def allocate(budget: float, planner_type: str = "home") -> List[CategoryAllocation]:
        rules = ALLOCATION_RULES.get(planner_type, ALLOCATION_RULES["home"])
        allocations = []
        for rule in rules:
            allocated_amount = round(budget * (rule["percentage"] / 100.0), 2)
            allocations.append(CategoryAllocation(
                category=rule["category"],
                percentage=rule["percentage"],
                allocated_amount=allocated_amount,
                description=rule.get("description")
            ))
        return allocations

    @staticmethod
    def generate_warnings(budget: float, estimated_cost: float, flexibility: str = "flexible") -> List[str]:
        warnings = []
        overage = estimated_cost - budget
        overage_pct = (overage / budget * 100) if budget > 0 else 0

        if flexibility == "strict" and estimated_cost > budget:
            warnings.append(f"Strict Budget Alert: Total cost exceeds budget by {overage:,.2f}.")
        elif flexibility == "moderate" and overage_pct > 10.0:
            warnings.append(f"Moderate Budget Alert: Total cost exceeds budget by {overage_pct:.1f}%.")
        elif flexibility == "flexible" and overage_pct > 25.0:
            warnings.append(f"Budget Alert: Planned spending is {overage_pct:.1f}% above target.")

        return warnings
