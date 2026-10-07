import logging
from typing import Dict, Any, List, Optional
from app.integrations.supabase_client import supabase_manager

logger = logging.getLogger("pocketsmart.plan_repository")

_MEMORY_STORE: Dict[str, Dict[str, Any]] = {}

class PlanRepository:
    def _prepare_db_record(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format and nest extra fields inside input_data to guarantee compatibility with PostgreSQL schema."""
        record = {
            "id": plan_data.get("id"),
            "user_id": plan_data.get("user_id"),
            "planner_type": plan_data.get("planner_type"),
            "title": plan_data.get("title", ""),
            "budget": float(plan_data.get("budget", 0)),
            "estimated_cost": float(plan_data.get("estimated_cost", 0)),
            "remaining_budget": float(plan_data.get("remaining_budget", 0)),
            "currency": plan_data.get("currency", "INR"),
            "ai_summary": plan_data.get("ai_summary", ""),
            "warnings": plan_data.get("warnings", []),
            "allocations": plan_data.get("allocations", []),
            "status": plan_data.get("status", "completed"),
        }
        if plan_data.get("created_at"):
            record["created_at"] = plan_data["created_at"]
        
        # Merge additional metadata into input_data jsonb
        input_data = dict(plan_data.get("input_data") or {})
        if "additional_suggestions" in plan_data:
            input_data["additional_suggestions"] = plan_data["additional_suggestions"]
        if "styling_tips" in plan_data:
            input_data["styling_tips"] = plan_data["styling_tips"]
        if "outfit_analysis" in plan_data:
            input_data["outfit_analysis"] = plan_data["outfit_analysis"]
        if "venue_suggestions" in plan_data:
            input_data["venue_suggestions"] = plan_data["venue_suggestions"]
        
        record["input_data"] = input_data
        return record

    def _hydrate_plan_record(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Hydrate extra fields from input_data back to root record."""
        data = dict(row)
        input_data = data.get("input_data") or {}
        if isinstance(input_data, dict):
            if "additional_suggestions" in input_data and "additional_suggestions" not in data:
                data["additional_suggestions"] = input_data["additional_suggestions"]
            if "styling_tips" in input_data and "styling_tips" not in data:
                data["styling_tips"] = input_data["styling_tips"]
            if "outfit_analysis" in input_data and "outfit_analysis" not in data:
                data["outfit_analysis"] = input_data["outfit_analysis"]
            if "venue_suggestions" in input_data and "venue_suggestions" not in data:
                data["venue_suggestions"] = input_data["venue_suggestions"]
        return data

    async def save_plan(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        _MEMORY_STORE[plan_data["id"]] = plan_data
        if supabase_manager.is_connected:
            try:
                db_record = self._prepare_db_record(plan_data)
                res = supabase_manager.client.table("plans").upsert(db_record).execute()
                if res.data:
                    hydrated = self._hydrate_plan_record(res.data[0])
                    _MEMORY_STORE[plan_data["id"]] = hydrated
                    return hydrated
            except Exception as e:
                err_str = str(e)
                # FK violation: user_id not in auth.users — fallback mode, not a crash
                if "23503" in err_str or "foreign key constraint" in err_str.lower():
                    logger.debug(f"Plan save skipped DB: user not in auth.users (FK). Plan cached in memory only.")
                else:
                    logger.error(f"Supabase PostgreSQL save_plan error: {e}")
        return plan_data


    async def get_plan_by_id(self, plan_id: str) -> Optional[Dict[str, Any]]:
        if supabase_manager.is_connected:
            try:
                res = supabase_manager.client.table("plans").select("*").eq("id", plan_id).execute()
                if res.data:
                    return self._hydrate_plan_record(res.data[0])
            except Exception as e:
                logger.error(f"Supabase PostgreSQL get_plan_by_id error: {e}")
        return _MEMORY_STORE.get(plan_id)

    async def list_plans_for_user(
        self,
        user_id: str,
        planner_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        if supabase_manager.is_connected:
            try:
                q = supabase_manager.client.table("plans").select("*").eq("user_id", user_id)
                if planner_type:
                    q = q.eq("planner_type", planner_type)
                res = q.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
                if res.data and len(res.data) > 0:
                    return [self._hydrate_plan_record(r) for r in res.data]
            except Exception as e:
                logger.error(f"Supabase PostgreSQL list_plans_for_user error: {e}")
        
        filtered = [
            p for p in _MEMORY_STORE.values()
            if str(p.get("user_id")) == str(user_id) and (planner_type is None or p.get("planner_type") == planner_type)
        ]
        return filtered[offset:offset + limit]

    async def delete_plan(self, plan_id: str) -> bool:
        _MEMORY_STORE.pop(plan_id, None)
        if supabase_manager.is_connected:
            try:
                supabase_manager.client.table("plans").delete().eq("id", plan_id).execute()
                return True
            except Exception as e:
                logger.error(f"Supabase PostgreSQL delete_plan error: {e}")
        return True

plan_repository = PlanRepository()
