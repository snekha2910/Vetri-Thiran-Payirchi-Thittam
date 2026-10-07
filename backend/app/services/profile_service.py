from datetime import datetime, timezone
from typing import Optional, Dict, Any
from app.repositories.profile_repository import profile_repository
from app.schemas.auth import UserResponse

class ProfileService:
    @staticmethod
    async def get_profile(user_id: str, email: str = "") -> UserResponse:
        profile = await profile_repository.get_profile(user_id)
        now_iso = datetime.now(timezone.utc).isoformat()
        if not profile:
            return UserResponse(
                id=user_id,
                email=email or f"{user_id}@example.com",
                full_name="PocketSmart User",
                fullName="PocketSmart User",
                avatar_url=None,
                created_at=now_iso,
                createdAt=now_iso
            )
        return UserResponse(
            id=user_id,
            email=profile.get("email", email),
            full_name=profile.get("full_name") or "PocketSmart User",
            fullName=profile.get("full_name") or "PocketSmart User",
            avatar_url=profile.get("avatar_url"),
            created_at=profile.get("created_at") or now_iso,
            createdAt=profile.get("created_at") or now_iso
        )

    @staticmethod
    async def update_profile(user_id: str, full_name: Optional[str] = None, avatar_url: Optional[str] = None) -> UserResponse:
        now_iso = datetime.now(timezone.utc).isoformat()
        updated = await profile_repository.update_profile(user_id, full_name, avatar_url)
        return UserResponse(
            id=user_id,
            email=updated.get("email", ""),
            full_name=updated.get("full_name", full_name or "PocketSmart User"),
            fullName=updated.get("full_name", full_name or "PocketSmart User"),
            avatar_url=updated.get("avatar_url", avatar_url),
            created_at=updated.get("created_at") or now_iso,
            createdAt=updated.get("created_at") or now_iso
        )
