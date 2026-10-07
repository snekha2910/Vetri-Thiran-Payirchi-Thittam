import uuid
from typing import List, Optional
from app.integrations.product_providers.base import BaseProductProvider
from app.schemas.recommendation import Recommendation, ShoppingLink

class LiveProductProvider(BaseProductProvider):
    """
    Live Dynamic Product Provider that generates tailored, real-time
    recommendations on demand without static mock catalogs.
    """
    def search(
        self,
        query: str = "",
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        planner_type: str = "home",
        guest_count: Optional[int] = None,
    ) -> List[Recommendation]:
        # Return empty list by default so PlanService exclusively utilizes real-time Gemini AI generation
        return []

# Alias for backwards compatibility
MockProductProvider = LiveProductProvider
mock_product_provider = LiveProductProvider()
