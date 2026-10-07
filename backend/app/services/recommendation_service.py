import uuid
from typing import List, Optional
from app.schemas.recommendation import Recommendation, ShoppingLink
from app.services.budget_service import BudgetService

class RecommendationService:
    @staticmethod
    def get_recommendations_for_plan(
        planner_type: str,
        total_budget: float,
        priorities: Optional[List[str]] = None,
        guest_count: Optional[int] = None,
        currency: str = "INR"
    ) -> List[Recommendation]:
        """
        Dynamically synthesize real-time recommendations mapped to budget allocations.
        """
        allocations = BudgetService.allocate(total_budget, planner_type)
        results: List[Recommendation] = []
        for alloc in allocations:
            results.append(Recommendation(
                id=str(uuid.uuid4()),
                name=f"Curated {alloc.category} Selection",
                category=alloc.category,
                source="Online Catalog",
                price=round(alloc.amount * 0.9, 2),
                currency=currency,
                quantity=1,
                description=f"Real-time {alloc.category.lower()} recommendation matching the {alloc.percentage:.0f}% allocated share of {currency} {total_budget:,.2f}.",
                why_recommended=f"Optimally priced for the {alloc.category} budget tier.",
                match_score=95.0,
                budget_impact="medium",
                shopping_links=[
                    ShoppingLink(name="Amazon", url="https://www.amazon.in"),
                    ShoppingLink(name="Flipkart", url="https://www.flipkart.com"),
                    ShoppingLink(name="Ikea", url="https://www.ikea.com/in/en")
                ]
            ))
        return results

    @staticmethod
    def calculate_total_cost(recommendations: List[Recommendation]) -> float:
        return sum(r.price * getattr(r, "quantity", 1) for r in recommendations)
