from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.schemas.plan import PlanSummaryResponse
from app.core.security import AuthenticatedUser
from app.core.dependencies import get_current_user
from app.services.plan_service import PlanService

router = APIRouter(prefix="/history", tags=["History"])

@router.get("", response_model=List[PlanSummaryResponse], summary="User plan history (alias to /plans)")
async def get_history(
    planner_type: Optional[str] = Query(None, description="Filter by planner type (home, party, jewelry)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    user: AuthenticatedUser = Depends(get_current_user)
):
    """Retrieve user plan history with pagination support."""
    return await PlanService.list_user_plans(user.id, planner_type, limit=limit, offset=offset)
