from abc import ABC, abstractmethod
from typing import List, Optional
from app.schemas.recommendation import Recommendation

class BaseProductProvider(ABC):
    @abstractmethod
    def search(
        self,
        query: str = "",
        category: Optional[str] = None,
        max_price: Optional[float] = None,
        planner_type: str = "home",
        guest_count: Optional[int] = None,
    ) -> List[Recommendation]:
        pass
