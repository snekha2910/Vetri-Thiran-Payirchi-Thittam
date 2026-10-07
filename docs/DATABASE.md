# PocketSmart AI — Database Schema & Architecture

The database runs on **Supabase PostgreSQL 15** with Row-Level Security (RLS) enabled across all public tables.

---

## Entity Relationship Diagram

```mermaid
erDiagram
    AUTH_USERS ||--|| PROFILES : "1:1 profile"
    AUTH_USERS ||--o{ PLANS : "1:N plans"
    PLANS ||--o{ RECOMMENDATIONS : "1:N recommendations"
    AUTH_USERS ||--o{ SAVED_RECOMMENDATIONS : "1:N bookmarks"
    RECOMMENDATIONS ||--o{ SAVED_RECOMMENDATIONS : "1:N saved_by"

    PROFILES {
        UUID id PK "FK auth.users.id"
        TEXT full_name
        TEXT avatar_url
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }

    PLANS {
        UUID id PK
        UUID user_id FK "auth.users.id"
        TEXT planner_type "home | party | jewelry"
        TEXT title
        NUMERIC budget
        NUMERIC estimated_cost
        NUMERIC remaining_budget
        TEXT currency "INR, USD, etc."
        TEXT ai_summary
        JSONB warnings
        JSONB allocations
        JSONB input_data
        TEXT status "pending | completed | failed"
        BOOLEAN partial
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }

    RECOMMENDATIONS {
        UUID id PK
        UUID plan_id FK "plans.id"
        TEXT name
        TEXT category
        TEXT source
        TEXT source_url
        NUMERIC price
        TEXT currency
        TEXT image_url
        TEXT description
        TEXT why_recommended
        NUMERIC match_score
        TEXT budget_impact "low | medium | high"
        JSONB metadata
        TIMESTAMPTZ created_at
    }

    SAVED_RECOMMENDATIONS {
        UUID id PK
        UUID user_id FK "auth.users.id"
        UUID recommendation_id FK "recommendations.id"
        TIMESTAMPTZ created_at
    }
```

---

## Table Definitions

### 1. `profiles`
Stores supplementary user profile metadata linked to Supabase's `auth.users` system table.
* **Auto Trigger**: Creates a profile row upon new user registration (`on_auth_user_created`).
* **Auto Timestamp**: Updates `updated_at` on modification.

### 2. `plans`
Represents an individual budget plan.
* **Columns**:
  * `id`: Primary UUID.
  * `user_id`: Owning user ID (enforced via foreign key and RLS).
  * `planner_type`: Enum string (`home`, `party`, `jewelry`).
  * `budget`, `estimated_cost`, `remaining_budget`: High precision numeric fields.
  * `allocations`: JSONB array of category allocations with allotted amounts and percentages.
  * `warnings`: JSONB list of budget alerts and advice.
  * `input_data`: JSONB representation of raw user form input for plan reproducibility.

### 3. `recommendations`
Stores individual item recommendations produced for a specific plan.
* **Columns**:
  * `plan_id`: Foreign key referencing parent `plans.id` (Cascading delete).
  * `match_score`: Float between 0 and 100 indicating alignment with aesthetic & constraints.
  * `budget_impact`: Qualitative impact badge (`low`, `medium`, `high`).
  * `metadata`: Dynamic JSONB storing attributes (dimensions, materials, color matching, etc.).

### 4. `saved_recommendations`
Bookmark join table enabling users to curate and save specific recommendations across plans.

---

## Row-Level Security (RLS) Policies

All tables have RLS enabled:
* Users can only `SELECT`, `INSERT`, `UPDATE`, and `DELETE` their own rows (`auth.uid() = user_id`).
* `recommendations` can be accessed if the user owns the parent plan (`EXISTS (SELECT 1 FROM plans WHERE plans.id = recommendations.plan_id AND plans.user_id = auth.uid())`).
* Service role tokens bypass RLS for administrative tasks.
