from fastapi import APIRouter, Depends
from app.schemas.jewelry import JewelryPlannerRequest
from app.schemas.plan import PlanDetailResponse
from app.core.security import AuthenticatedUser
from app.core.dependencies import get_current_user
from app.core.rate_limiter import rate_limit
from app.services.plan_service import PlanService

router = APIRouter(tags=["Planner - Jewelry"])

@router.post("/planner/jewelry", response_model=PlanDetailResponse, dependencies=[Depends(rate_limit(max_requests=15, window_seconds=60))])
@router.post("/planners/jewelry", response_model=PlanDetailResponse, dependencies=[Depends(rate_limit(max_requests=15, window_seconds=60))])
@router.post("/planner/jewelry/generate", response_model=PlanDetailResponse, dependencies=[Depends(rate_limit(max_requests=15, window_seconds=60))])
@router.post("/planners/jewelry/generate", response_model=PlanDetailResponse, dependencies=[Depends(rate_limit(max_requests=15, window_seconds=60))])
async def generate_jewelry_plan(payload: JewelryPlannerRequest, user: AuthenticatedUser = Depends(get_current_user)):
    return await PlanService.create_and_execute_plan(
        user_id=user.id,
        planner_type="jewelry",
        title=payload.title or "Jewelry Styling Plan",
        total_budget=payload.total_budget,
        currency=payload.currency,
        flexibility=payload.budget_flexibility,
        input_data=payload.model_dump()
    )
