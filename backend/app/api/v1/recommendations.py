from typing import List
from fastapi import APIRouter, Depends, status
from app.core.security import AuthenticatedUser
from app.core.dependencies import get_current_user
from app.schemas.recommendation import Recommendation
from app.repositories.saved_repository import saved_repository
from app.repositories.recommendation_repository import recommendation_repository
from app.repositories.plan_repository import plan_repository
from app.core.exceptions import NotFoundError, AuthorizationError

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])

@router.get("/saved", response_model=List[str])
async def get_saved_recommendations(user: AuthenticatedUser = Depends(get_current_user)):
    return await saved_repository.get_saved_ids(user.id)

@router.get("/{plan_id}", response_model=List[Recommendation])
async def list_recommendations_for_plan(plan_id: str, user: AuthenticatedUser = Depends(get_current_user)):
    # Verify plan existence and ownership
    plan = await plan_repository.get_plan_by_id(plan_id)
    if not plan:
        raise NotFoundError("Plan not found")
    if str(plan.get("user_id")) != str(user.id):
        raise AuthorizationError("Access denied: You do not have permission to view recommendations for this plan")

    return await recommendation_repository.get_by_plan_id(plan_id)

@router.post("/{recommendation_id}/save", status_code=status.HTTP_200_OK)
async def save_recommendation(recommendation_id: str, user: AuthenticatedUser = Depends(get_current_user)):
    await saved_repository.save_recommendation(user.id, recommendation_id)
    return {"status": "success", "message": "Recommendation bookmarked"}

@router.delete("/{recommendation_id}/save", status_code=status.HTTP_200_OK)
async def unsave_recommendation(recommendation_id: str, user: AuthenticatedUser = Depends(get_current_user)):
    await saved_repository.unsave_recommendation(user.id, recommendation_id)
    return {"status": "success", "message": "Recommendation removed from bookmarks"}
