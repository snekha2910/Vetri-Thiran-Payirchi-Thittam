import logging
from typing import Dict, Any, Optional
from app.integrations.supabase_client import supabase_manager

logger = logging.getLogger("pocketsmart.profile_repository")

_MEMORY_PROFILES: Dict[str, Dict[str, Any]] = {}


class ProfileRepository:
    async def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        if supabase_manager.is_connected:
            try:
                res = supabase_manager.client.table("profiles").select("*").eq("id", user_id).execute()
                if res.data and len(res.data) > 0:
                    return res.data[0]
            except Exception as e:
                logger.error(f"Supabase PostgreSQL get_profile error: {e}")
        return _MEMORY_PROFILES.get(user_id)

    async def update_profile(self, user_id: str, full_name: Optional[str], avatar_url: Optional[str]) -> Dict[str, Any]:
        """Attempt to upsert profile in Supabase. Falls back to memory store on any error."""
        data = {"id": user_id}
        if full_name is not None:
            data["full_name"] = full_name
        if avatar_url is not None:
            data["avatar_url"] = avatar_url

        # Always update memory store
        current = _MEMORY_PROFILES.get(user_id, {"id": user_id})
        current.update(data)
        _MEMORY_PROFILES[user_id] = current

        if supabase_manager.is_connected:
            try:
                res = supabase_manager.client.table("profiles").upsert(data).execute()
                if res.data and len(res.data) > 0:
                    return res.data[0]
            except Exception as e:
                err_str = str(e)
                # FK violation means the user doesn't exist in auth.users yet
                # (e.g., signup failed in Supabase but we have a local fallback UUID)
                # This is expected in degraded/dev mode — don't log as error
                if "23503" in err_str or "foreign key constraint" in err_str.lower():
                    logger.debug(f"Profile upsert skipped: user {user_id} not yet in auth.users (FK constraint)")
                else:
                    logger.error(f"Supabase PostgreSQL update_profile error: {e}")
        return current

    async def update_profile_memory(self, user_id: str, full_name: Optional[str] = None) -> Dict[str, Any]:
        """Update only the in-memory profile store (used when Supabase is unavailable)."""
        current = _MEMORY_PROFILES.get(user_id, {"id": user_id})
        if full_name is not None:
            current["full_name"] = full_name
        _MEMORY_PROFILES[user_id] = current
        return current


profile_repository = ProfileRepository()
