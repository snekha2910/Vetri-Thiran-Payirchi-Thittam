import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.services.budget_service import BudgetService
from app.services.gemini_service import GeminiService
from app.repositories.plan_repository import plan_repository
from app.repositories.recommendation_repository import recommendation_repository
from app.prompts.home_prompt import build_home_prompt
from app.prompts.party_prompt import build_party_prompt
from app.prompts.jewelry_prompt import build_jewelry_prompt
from app.schemas.plan import (
    PlanDetailResponse,
    BudgetSummary,
    PlanSummaryResponse,
    OutfitAnalysis,
    VenueSuggestion
)
from app.schemas.recommendation import Recommendation, ShoppingLink
from app.schemas.common import CategoryAllocation
from app.core.exceptions import NotFoundError, AuthorizationError

def _build_shopping_links(raw_links: list, item_name: str) -> List[ShoppingLink]:
    if raw_links and isinstance(raw_links, list):
        results = []
        for link in raw_links:
            if isinstance(link, dict):
                results.append(ShoppingLink(name=link.get("name", "Store"), url=link.get("url", "#")))
            elif isinstance(link, str):
                results.append(ShoppingLink(name=link, url="#"))
        if results:
            return results

    # Defaults by item name
    return [
        ShoppingLink(name="Amazon", url="https://www.amazon.in"),
        ShoppingLink(name="Flipkart", url="https://www.flipkart.com"),
        ShoppingLink(name="Ikea", url="https://www.ikea.com/in/en"),
        ShoppingLink(name="Myntra", url="https://www.myntra.com"),
        ShoppingLink(name="Ajio", url="https://www.ajio.com"),
    ]

class PlanService:
    @staticmethod
    async def create_and_execute_plan(
        user_id: str,
        planner_type: str,
        title: str,
        total_budget: float,
        currency: str,
        flexibility: str,
        input_data: Dict[str, Any],
        guest_count: Optional[int] = None
    ) -> PlanDetailResponse:
        plan_id = str(uuid.uuid4())

        # 1. Build prompt and invoke Google Gemini AI
        if planner_type == "home":
            prompt = build_home_prompt(input_data)
        elif planner_type == "party":
            prompt = build_party_prompt(input_data)
        elif planner_type == "jewelry":
            prompt = build_jewelry_prompt(input_data)
        else:
            prompt = build_home_prompt(input_data)

        ai_result = await GeminiService.generate_plan_ai(prompt, planner_type=planner_type)

        # 2. Extract recommendations from AI response
        raw_recs = ai_result.get("recommendations", [])
        recommendations: List[Recommendation] = []

        for r in raw_recs:
            if not isinstance(r, dict) or not r.get("name"):
                continue
            item_name = r.get("name", "Recommended Item")
            price = float(r.get("price", total_budget * 0.15))
            quantity = int(r.get("quantity", 1))
            shopping_links = _build_shopping_links(r.get("shopping_links", []), item_name)

            rec = Recommendation(
                id=str(uuid.uuid4()),
                plan_id=plan_id,
                planId=plan_id,
                name=item_name,
                category=r.get("category", "General"),
                price=price,
                currency=currency,
                quantity=quantity,
                style=r.get("style"),
                description=r.get("description", f"Tailored recommendation matching your {planner_type} goals."),
                why_recommended=r.get("why_recommended", r.get("description", "")),
                whyRecommended=r.get("why_recommended", r.get("description", "")),
                match_score=float(r.get("match_score", 95.0)),
                budget_impact=r.get("budget_impact", "medium"),
                shopping_links=shopping_links,
                shoppingLinks=shopping_links,
                metadata={}
            )
            recommendations.append(rec)

        # If AI returned 0 items due to parsing/empty response, dynamically synthesize real-time items based on input parameters
        if not recommendations:
            allocations_for_items = BudgetService.allocate(total_budget, planner_type)
            for alloc in allocations_for_items:
                unit_price = round(alloc.amount * 0.9, 2)
                item_name = f"Curated {alloc.category} Selection"
                shopping_links = _build_shopping_links([], item_name)
                rec = Recommendation(
                    id=str(uuid.uuid4()),
                    plan_id=plan_id,
                    planId=plan_id,
                    name=item_name,
                    category=alloc.category,
                    price=unit_price,
                    currency=currency,
                    quantity=1,
                    description=f"Tailored {alloc.category.lower()} matching your style and {currency} {total_budget:,.2f} budget allocation.",
                    why_recommended=f"Selected to fit within the {alloc.percentage:.0f}% category budget allocation.",
                    whyRecommended=f"Selected to fit within the {alloc.percentage:.0f}% category budget allocation.",
                    match_score=95.0,
                    budget_impact="medium",
                    shopping_links=shopping_links,
                    shoppingLinks=shopping_links,
                    metadata={}
                )
                recommendations.append(rec)

        # 3. Allocations
        raw_allocs = ai_result.get("allocations", [])
        allocations: List[CategoryAllocation] = []
        if raw_allocs and isinstance(raw_allocs, list):
            for a in raw_allocs:
                if isinstance(a, dict) and a.get("category"):
                    allocations.append(CategoryAllocation(
                        category=a["category"],
                        amount=float(a.get("allocated_amount", a.get("amount", 0.0))),
                        allocated_amount=float(a.get("allocated_amount", a.get("amount", 0.0))),
                        percentage=float(a.get("percentage", 0.0)),
                        description=a.get("description")
                    ))
        if not allocations:
            allocations = BudgetService.allocate(total_budget, planner_type)

        # 4. Financial Calculations
        estimated_cost = sum(r.price * getattr(r, "quantity", 1) for r in recommendations)
        if estimated_cost == 0:
            estimated_cost = total_budget * 0.85

        budget_calc = BudgetService.calculate(total_budget, estimated_cost, currency)
        warnings = BudgetService.generate_warnings(total_budget, estimated_cost, flexibility)
        if ai_result.get("warnings"):
            warnings.extend(ai_result["warnings"])

        ai_summary = ai_result.get("ai_summary", ai_result.get("summary", f"Personalized AI plan designed for your {currency} {total_budget:,.2f} budget."))

        # 5. Suggestions, Styling Tips, Outfit Analysis, Venue Suggestions
        additional_suggestions = ai_result.get("additional_suggestions") or [
            "Consider purchasing key foundation items first to lock in main costs.",
            "Compare discounts and seasonal sales across major marketplaces.",
            "Prioritize multi-functional pieces to optimize value."
        ]

        styling_tips = ai_result.get("styling_tips") or (
            [
                "Keep jewelry minimal to match the outfit silhouette.",
                "Choose a statement piece as the focal center.",
                "Ensure metal tones complement your embroidery."
            ] if planner_type == "jewelry" else []
        )

        outfit_analysis = None
        if planner_type == "jewelry":
            oa_data = ai_result.get("outfit_analysis") or {}
            outfit_analysis = OutfitAnalysis(
                colors=oa_data.get("colors", ["blue", "white"]),
                style=oa_data.get("style", input_data.get("style", "casual")),
                formality=oa_data.get("formality", "informal" if input_data.get("occasion") in ("casual", "party") else "formal")
            )

        venue_suggestions = []
        if planner_type == "party":
            vs_data = ai_result.get("venue_suggestions") or []
            if vs_data and isinstance(vs_data, list):
                venue_suggestions = [VenueSuggestion(**v) if isinstance(v, dict) else v for v in vs_data]
            else:
                venue_suggestions = [
                    VenueSuggestion(
                        name="Home",
                        type="Residential",
                        location=input_data.get("location") or "Local area",
                        cost=0.0,
                        website="https://google.com",
                        map_url="https://maps.google.com",
                        mapUrl="https://maps.google.com"
                    )
                ]

        # 6. Persist to database
        now_iso = datetime.now(timezone.utc).isoformat()
        plan_record = {
            "id": plan_id,
            "user_id": user_id,
            "planner_type": planner_type,
            "title": title or f"My {planner_type.capitalize()} Plan",
            "budget": total_budget,
            "estimated_cost": estimated_cost,
            "remaining_budget": budget_calc.remaining_budget,
            "currency": currency,
            "ai_summary": ai_summary,
            "warnings": warnings,
            "allocations": [a.model_dump() for a in allocations],
            "input_data": input_data,
            "additional_suggestions": additional_suggestions,
            "styling_tips": styling_tips,
            "outfit_analysis": outfit_analysis.model_dump() if outfit_analysis else None,
            "venue_suggestions": [v.model_dump() for v in venue_suggestions],
            "status": "completed",
            "created_at": now_iso
        }
        await plan_repository.save_plan(plan_record)
        await recommendation_repository.save_recommendations(plan_id, recommendations)

        budget_summary = BudgetSummary(
            budget=total_budget,
            total_budget=total_budget,
            totalBudget=total_budget,
            estimated_cost=estimated_cost,
            estimatedCost=estimated_cost,
            remaining_budget=budget_calc.remaining_budget,
            remaining=budget_calc.remaining_budget,
            savings=max(budget_calc.remaining_budget, 0.0),
            percentage_used=budget_calc.percentage_used,
            utilization=round(budget_calc.percentage_used),
            currency=currency,
            is_over_budget=budget_calc.is_over_budget
        )

        return PlanDetailResponse(
            id=plan_id,
            plan_id=plan_id,
            user_id=user_id,
            planner_type=planner_type,
            title=plan_record["title"],
            budget=budget_summary,
            budget_summary=budget_summary,
            allocations=allocations,
            ai_summary=ai_summary,
            aiSummary=ai_summary,
            warnings=warnings,
            recommendations=recommendations,
            additional_suggestions=additional_suggestions,
            additionalSuggestions=additional_suggestions,
            styling_tips=styling_tips,
            stylingTips=styling_tips,
            outfit_analysis=outfit_analysis,
            outfitAnalysis=outfit_analysis,
            venue_suggestions=venue_suggestions,
            venueSuggestions=venue_suggestions,
            input_data=input_data,
            status="completed",
            created_at=now_iso,
            createdAt=now_iso
        )

    @staticmethod
    async def get_plan(plan_id: str, user_id: str) -> PlanDetailResponse:
        plan = await plan_repository.get_plan_by_id(plan_id)
        if not plan:
            raise NotFoundError("Plan not found")
        if plan["user_id"] != user_id:
            raise AuthorizationError("Access denied to this plan")

        recs = await recommendation_repository.get_by_plan_id(plan_id)
        total_budget = float(plan["budget"])
        estimated_cost = float(plan["estimated_cost"])
        budget_calc = BudgetService.calculate(total_budget, estimated_cost, plan.get("currency", "INR"))

        budget_summary = BudgetSummary(
            budget=total_budget,
            total_budget=total_budget,
            totalBudget=total_budget,
            estimated_cost=estimated_cost,
            estimatedCost=estimated_cost,
            remaining_budget=budget_calc.remaining_budget,
            remaining=budget_calc.remaining_budget,
            savings=max(budget_calc.remaining_budget, 0.0),
            percentage_used=budget_calc.percentage_used,
            utilization=round(budget_calc.percentage_used),
            currency=plan.get("currency", "INR"),
            is_over_budget=budget_calc.is_over_budget
        )

        add_sugg = plan.get("additional_suggestions") or []
        styling_tips = plan.get("styling_tips") or []
        
        oa = plan.get("outfit_analysis")
        outfit_analysis = OutfitAnalysis(**oa) if oa else None

        vs = plan.get("venue_suggestions") or []
        venue_suggestions = [VenueSuggestion(**v) for v in vs]

        return PlanDetailResponse(
            id=plan["id"],
            plan_id=plan["id"],
            user_id=plan["user_id"],
            planner_type=plan["planner_type"],
            title=plan["title"],
            budget=budget_summary,
            budget_summary=budget_summary,
            allocations=plan.get("allocations", []),
            ai_summary=plan.get("ai_summary", ""),
            aiSummary=plan.get("ai_summary", ""),
            warnings=plan.get("warnings", []),
            recommendations=recs,
            additional_suggestions=add_sugg,
            additionalSuggestions=add_sugg,
            styling_tips=styling_tips,
            stylingTips=styling_tips,
            outfit_analysis=outfit_analysis,
            outfitAnalysis=outfit_analysis,
            venue_suggestions=venue_suggestions,
            venueSuggestions=venue_suggestions,
            input_data=plan.get("input_data", {}),
            status=plan.get("status", "completed"),
            created_at=plan.get("created_at"),
            createdAt=plan.get("created_at")
        )

    @staticmethod
    async def list_user_plans(
        user_id: str,
        planner_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[PlanSummaryResponse]:
        plans = await plan_repository.list_plans_for_user(user_id, planner_type, limit=limit, offset=offset)
        results = []
        for p in plans:
            results.append(PlanSummaryResponse(
                id=p["id"],
                user_id=p["user_id"],
                planner_type=p["planner_type"],
                title=p["title"],
                budget=float(p["budget"]),
                estimated_cost=float(p["estimated_cost"]),
                remaining_budget=float(p["remaining_budget"]),
                currency=p.get("currency", "INR"),
                status=p.get("status", "completed"),
                created_at=p.get("created_at", "")
            ))
        return results

    @staticmethod
    async def delete_plan(plan_id: str, user_id: str) -> bool:
        plan = await plan_repository.get_plan_by_id(plan_id)
        if not plan:
            raise NotFoundError("Plan not found")
        if plan["user_id"] != user_id:
            raise AuthorizationError("Access denied to this plan")
        return await plan_repository.delete_plan(plan_id)
