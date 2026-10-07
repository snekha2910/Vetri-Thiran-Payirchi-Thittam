import uuid
import logging
from typing import List, Dict, Any, Set
from app.integrations.supabase_client import supabase_manager

logger = logging.getLogger("pocketsmart.saved_repository")

_MEMORY_SAVED: Dict[str, Set[str]] = {}

class SavedRepository:
    async def save_recommendation(self, user_id: str, recommendation_id: str) -> None:
        if user_id not in _MEMORY_SAVED:
            _MEMORY_SAVED[user_id] = set()
        _MEMORY_SAVED[user_id].add(recommendation_id)

        if supabase_manager.is_connected:
            try:
                supabase_manager.client.table("saved_recommendations").upsert({
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "recommendation_id": recommendation_id
                }).execute()
            except Exception as e:
                logger.error(f"Supabase PostgreSQL save_recommendation error: {e}")

    async def unsave_recommendation(self, user_id: str, recommendation_id: str) -> None:
        if user_id in _MEMORY_SAVED:
            _MEMORY_SAVED[user_id].discard(recommendation_id)

        if supabase_manager.is_connected:
            try:
                supabase_manager.client.table("saved_recommendations").delete().eq("user_id", user_id).eq("recommendation_id", recommendation_id).execute()
            except Exception as e:
                logger.error(f"Supabase PostgreSQL unsave_recommendation error: {e}")

    async def get_saved_ids(self, user_id: str) -> List[str]:
        if supabase_manager.is_connected:
            try:
                res = supabase_manager.client.table("saved_recommendations").select("recommendation_id").eq("user_id", user_id).execute()
                if res.data and len(res.data) > 0:
                    return [r["recommendation_id"] for r in res.data]
            except Exception as e:
                logger.error(f"Supabase PostgreSQL get_saved_ids error: {e}")
        return list(_MEMORY_SAVED.get(user_id, set()))

saved_repository = SavedRepository()
