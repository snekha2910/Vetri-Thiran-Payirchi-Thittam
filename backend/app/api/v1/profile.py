from fastapi import APIRouter, Depends
from app.schemas.auth import UserResponse, ProfileUpdateRequest
from app.core.security import AuthenticatedUser
from app.core.dependencies import get_current_user
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("", response_model=UserResponse)
async def get_profile(user: AuthenticatedUser = Depends(get_current_user)):
    return await ProfileService.get_profile(user.id, user.email)

@router.put("", response_model=UserResponse)
async def update_profile(payload: ProfileUpdateRequest, user: AuthenticatedUser = Depends(get_current_user)):
    return await ProfileService.update_profile(user.id, payload.full_name, payload.avatar_url)
