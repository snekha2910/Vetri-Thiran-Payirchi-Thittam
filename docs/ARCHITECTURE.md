# PocketSmart AI — Architecture Documentation

## System Overview

PocketSmart AI is an intelligent financial planning and lifestyle budgeting engine designed for modern consumers. It couples AI recommendation capabilities (Google Gemini 2.5 Flash / 1.5 Pro) with strict mathematical budget enforcement and structured catalog sourcing.

```
┌────────────────────────────────────────────────────────┐
│             PocketSmart AI Frontend (Vite + React)      │
│  - TanStack Router & SSR                               │
│  - React Query for state management                    │
│  - Lucide Icons + Tailwind / Glassmorphic UI           │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP / REST + Bearer JWT
                            ▼
┌────────────────────────────────────────────────────────┐
│             PocketSmart AI FastAPI Backend             │
│  - Async ASGI Server (Uvicorn)                         │
│  - Modular Router: /auth, /profile, /planner, /plans   │
│  - Pydantic v2 validation & type safety                │
└───────┬───────────────────┬───────────────────┬────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│ Supabase Cloud │  │ Google Gemini  │  │ Product Catalog│
│ - PostgreSQL 15│  │ - 2.5 Flash /  │  │ - Mock Provider│
│ - Supabase Auth│  │   1.5 Pro      │  │ - Multi-source │
│ - Storage S3   │  │ - Multimodal   │  │   Pricing DB   │
└────────────────┘  └────────────────┘  └────────────────┘
```

---

## Layered Backend Architecture

The backend follows a strict clean architecture pattern:

```
backend/
├── app/
│   ├── api/             # HTTP endpoints and routing
│   │   ├── router.py    # Master router
│   │   └── v1/          # Versioned route modules (auth, home, party, jewelry, etc.)
│   ├── core/            # Configuration, security, logging, exceptions
│   ├── integrations/    # External clients (Supabase, Gemini, Product Providers)
│   ├── prompts/         # Domain-specific prompt engineering
│   ├── repositories/    # Data persistence and Supabase DB calls
│   ├── schemas/         # Pydantic models for inputs, outputs, and validation
│   └── services/        # Core business logic (BudgetService, RecommendationService)
```

### 1. Presentation Layer (`app/api/`)
* Handles incoming requests, validates headers and payload schemas.
* Injects security dependencies (`get_current_user`, `get_optional_user`).
* Returns uniform response schemas.

### 2. Service Layer (`app/services/`)
* **`BudgetService`**: Pure deterministic financial calculations. Computes allocations, remaining budgets, percentages, and alerts for overages or deficit risk.
* **`GeminiService`**: Communicates with Google Generative AI models using structured JSON schema prompts, fallback parsing, and automatic repair routines.
* **`RecommendationService`**: Merges AI semantic recommendations with real catalog data, computes match scores and budget feasibility.
* **`PlanService`**: Orchestrates the multi-step lifecycle of generating, storing, retrieving, and updating user plans.
* **`ImageService`**: Validates MIME types, byte headers (magic bytes), file sizes, and coordinates secure Supabase Storage uploads.

### 3. Data & Repository Layer (`app/repositories/`)
* Encapsulates all interactions with the database via Supabase Python SDK / PostgREST.
* Enforces Row Level Security (RLS) constraints and multi-tenancy isolation.

---

## Data Flow for a Planner Request

1. **Client Request**: User fills out the planner form on React frontend (e.g. Home, Party, or Jewelry) and hits submit.
2. **Authentication**: FastAPI security middleware extracts Bearer token, validates against Supabase Auth, and resolves `user_id`.
3. **Budget Partitioning**: `BudgetService` generates baseline category allocations according to room type, guest count, or jewelry occasion.
4. **AI Generation**: `GeminiService` executes domain prompt with strict JSON output format constraints (including multimodal analysis if image is attached).
5. **Catalog Matching**: `RecommendationService` queries product providers to attach real items, compute match scores, and verify pricing.
6. **Persistence**: `PlanRepository` and `RecommendationRepository` persist the plan and recommendations within a transaction.
7. **Response**: Comprehensive plan structure with budget metrics, warnings, and curated recommendations returned to frontend.
