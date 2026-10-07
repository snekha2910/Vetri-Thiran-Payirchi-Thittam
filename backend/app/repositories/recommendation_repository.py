import logging
from typing import List, Dict, Any
from app.integrations.supabase_client import supabase_manager
from app.schemas.recommendation import Recommendation, ShoppingLink

logger = logging.getLogger("pocketsmart.recommendation_repository")

_MEMORY_RECS: Dict[str, List[Recommendation]] = {}

class RecommendationRepository:
    def _prepare_db_record(self, r: Recommendation, plan_id: str) -> Dict[str, Any]:
        links = [l.model_dump() if hasattr(l, "model_dump") else l for l in (r.shopping_links or r.shoppingLinks or [])]
        meta = dict(r.metadata or {})
        meta["shopping_links"] = links
        meta["quantity"] = getattr(r, "quantity", 1)
        if getattr(r, "style", None):
            meta["style"] = r.style

        return {
            "id": r.id,
            "plan_id": plan_id,
            "name": r.name,
            "category": r.category or "General",
            "source": r.source or "Online Store",
            "source_url": r.source_url or r.sourceUrl,
            "price": float(r.price),
            "currency": r.currency or "INR",
            "image_url": r.image_url or r.imageUrl,
            "description": r.description or "",
            "why_recommended": r.why_recommended or r.whyRecommended or "",
            "match_score": float(r.match_score or r.matchScore or 90.0),
            "budget_impact": r.budget_impact or r.budgetImpact or "medium",
            "metadata": meta,
        }

    def _hydrate_recommendation(self, row: Dict[str, Any]) -> Recommendation:
        meta = row.get("metadata") or {}
        raw_links = meta.get("shopping_links") or []
        shopping_links = [ShoppingLink(**l) if isinstance(l, dict) else ShoppingLink(name=str(l), url="#") for l in raw_links]
        
        return Recommendation(
            id=str(row.get("id")),
            plan_id=str(row.get("plan_id")),
            planId=str(row.get("plan_id")),
            name=row.get("name", "Recommended Item"),
            category=row.get("category", "General"),
            source=row.get("source", "Store"),
            source_url=row.get("source_url"),
            sourceUrl=row.get("source_url"),
            price=float(row.get("price", 0.0)),
            currency=row.get("currency", "INR"),
            quantity=int(meta.get("quantity", 1)),
            style=meta.get("style"),
            image_url=row.get("image_url"),
            imageUrl=row.get("image_url"),
            description=row.get("description", ""),
            why_recommended=row.get("why_recommended", ""),
            whyRecommended=row.get("why_recommended", ""),
            match_score=float(row.get("match_score", 90.0)),
            matchScore=float(row.get("match_score", 90.0)),
            budget_impact=row.get("budget_impact", "medium"),
            budgetImpact=row.get("budget_impact", "medium"),
            shopping_links=shopping_links,
            shoppingLinks=shopping_links,
            metadata=meta
        )

    async def save_recommendations(self, plan_id: str, recs: List[Recommendation]) -> None:
        _MEMORY_RECS[plan_id] = recs
        if supabase_manager.is_connected and recs:
            try:
                records = [self._prepare_db_record(r, plan_id) for r in recs]
                supabase_manager.client.table("recommendations").upsert(records).execute()
            except Exception as e:
                err_str = str(e)
                if "23503" in err_str or "foreign key constraint" in err_str.lower():
                    logger.debug(f"Recommendations save skipped DB: plan {plan_id} not in DB (FK). Cached in memory.")
                else:
                    logger.error(f"Supabase PostgreSQL save_recommendations error: {e}")

    async def get_by_plan_id(self, plan_id: str) -> List[Recommendation]:
        if supabase_manager.is_connected:
            try:
                res = supabase_manager.client.table("recommendations").select("*").eq("plan_id", plan_id).execute()
                if res.data and len(res.data) > 0:
                    return [self._hydrate_recommendation(r) for r in res.data]
            except Exception as e:
                logger.error(f"Supabase PostgreSQL get_by_plan_id error: {e}")
        return _MEMORY_RECS.get(plan_id, [])

recommendation_repository = RecommendationRepository()
