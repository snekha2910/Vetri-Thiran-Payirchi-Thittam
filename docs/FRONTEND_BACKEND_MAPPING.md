# PocketSmart AI — Frontend & Backend Mapping Guide

This document maps all frontend user interfaces, forms, and routes to their respective FastAPI endpoints and backend services.

---

## Route & API Mapping Table

| Frontend Route | UI Component / Page | Method & Endpoint | Backend Handler | Associated Service |
|---|---|---|---|---|
| `/login` | `routes/login.tsx` | `POST /api/v1/auth/login` | `app.api.v1.auth:login` | `SupabaseClient.auth` |
| `/register` | `routes/register.tsx` | `POST /api/v1/auth/register` | `app.api.v1.auth:register` | `SupabaseClient.auth` |
| `/profile` | `routes/profile.tsx` | `GET /api/v1/profile`<br>`PUT /api/v1/profile` | `app.api.v1.profile` | `ProfileService` |
| `/planner/home` | `routes/planner.home.tsx` | `POST /api/v1/planner/home` | `app.api.v1.home:generate_home_plan` | `PlanService`, `GeminiService`, `BudgetService` |
| `/planner/party` | `routes/planner.party.tsx` | `POST /api/v1/planner/party` | `app.api.v1.party:generate_party_plan` | `PlanService`, `GeminiService`, `BudgetService` |
| `/planner/jewelry` | `routes/planner.jewelry.tsx` | `POST /api/v1/planner/jewelry` | `app.api.v1.jewelry:generate_jewelry_plan` | `PlanService`, `GeminiService`, `ImageService` |
| `/planner/*/results/$planId` | `routes/planner.*.results.$planId.tsx` | `GET /api/v1/plans/{id}` | `app.api.v1.plans:get_plan` | `PlanService` |
| `/history` | `routes/history.tsx` | `GET /api/v1/plans` | `app.api.v1.plans:list_plans` | `PlanService` |
| `/history/$planId` | `routes/history.$planId.tsx` | `GET /api/v1/plans/{id}`<br>`DELETE /api/v1/plans/{id}` | `app.api.v1.plans` | `PlanService` |
| Image Upload Component | `components/planner/ImageUploader.tsx` | `POST /api/v1/images/upload` | `app.api.v1.images:upload_image` | `ImageService` |
| Bookmark Button | `components/planner/RecommendationCard.tsx` | `POST /api/v1/recommendations/{id}/save` | `app.api.v1.recommendations` | `RecommendationService` |

---

## Field Name Conventions & Serialization

* **Frontend**: Uses camelCase (`totalBudget`, `roomSizeSqft`, `outfitImageUrl`, `outfitStoragePath`).
* **Backend**: Uses snake_case (`total_budget`, `room_size_sqft`, `outfit_image_url`, `outfit_storage_path`).
* **Pydantic Serialization**: Pydantic models automatically accept and deserialize both snake_case and camelCase alias fields to maintain seamless bidirectional compatibility.
