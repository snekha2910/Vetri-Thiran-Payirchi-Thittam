# PocketSmart AI — API Contract Specification

**Base URL**: `http://localhost:8000/api/v1` (Production: configurable via `VITE_API_BASE_URL` / `API_BASE_URL`)  
**Auth Header**: `Authorization: Bearer <token>` (Supabase JWT or mock dev token)  
**Content-Type**: `application/json` (except image uploads which use `multipart/form-data`)

---

## Standard Response Envelopes

### Success Response
```json
{
  "status": "success",
  "data": { ... },
  "message": "Optional message"
}
```

### Error Response
```json
{
  "status": "error",
  "code": "VALIDATION_ERROR",
  "message": "Human-readable error explanation",
  "details": []
}
```

---

## 1. Authentication & User Profile

### `POST /auth/register`
Create a new user account via Supabase Auth.

- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "StrongPassword123!",
    "full_name": "Jane Doe"
  }
  ```
- **Response** `201 Created`:
  ```json
  {
    "id": "uuid-v4",
    "email": "user@example.com",
    "full_name": "Jane Doe",
    "token": "supabase.jwt.token",
    "avatar_url": null,
    "created_at": "2026-09-23T12:00:00Z"
  }
  ```

### `POST /auth/login`
Authenticate user with email and password.

- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "StrongPassword123!"
  }
  ```
- **Response** `200 OK`:
  ```json
  {
    "id": "uuid-v4",
    "email": "user@example.com",
    "full_name": "Jane Doe",
    "token": "supabase.jwt.token",
    "avatar_url": null,
    "created_at": "2026-09-23T12:00:00Z"
  }
  ```

### `GET /auth/me`
Retrieve currently authenticated user.

- **Headers**: `Authorization: Bearer <token>`
- **Response** `200 OK`: User object.

### `GET /profile`
Get user profile details.

- **Headers**: `Authorization: Bearer <token>`
- **Response** `200 OK`:
  ```json
  {
    "id": "uuid-v4",
    "email": "user@example.com",
    "full_name": "Jane Doe",
    "avatar_url": "https://...",
    "created_at": "2026-09-23T12:00:00Z",
    "updated_at": "2026-09-23T12:00:00Z"
  }
  ```

### `PUT /profile`
Update user profile fields (`full_name`, `avatar_url`).

---

## 2. Planner Endpoints

### `POST /planner/home`
Generate an AI-powered Home & Room Renovation / Interior plan.

- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "title": "Living Room Redesign",
    "room_type": "living_room",
    "room_size_sqft": 350.0,
    "style": "Modern Minimalist",
    "total_budget": 75000.0,
    "currency": "INR",
    "budget_flexibility": "flexible",
    "key_priorities": ["Sofa", "Ambient Lighting", "Coffee Table"],
    "color_preferences": ["Warm Grey", "Oak Wood", "Matte Black"],
    "existing_items": "Existing 55-inch TV mounted on wall",
    "special_requirements": "Pet-friendly fabric"
  }
  ```
- **Response** `200 OK`: Full `PlanDetailResponse` containing calculated allocations, warnings, summary, and scored recommendations.

### `POST /planner/party`
Generate an AI-powered Party & Event plan.

- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "title": "25th Birthday Bash",
    "party_type": "birthday",
    "guest_count": 30,
    "theme": "Retro Neon 90s",
    "total_budget": 50000.0,
    "currency": "INR",
    "budget_flexibility": "moderate",
    "venue_type": "indoor",
    "catering_preference": "Appetizers & Mocktails",
    "key_priorities": ["Sound & DJ", "Custom Cake", "Theme Lighting"],
    "special_requirements": "Vegetarian catering options"
  }
  ```
- **Response** `200 OK`: Full `PlanDetailResponse`.

### `POST /planner/jewelry`
Generate an AI-powered Jewelry & Fashion Styling plan with optional multimodal outfit visual analysis.

- **Headers**: `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "title": "Wedding Sangeet Jewelry Set",
    "occasion": "wedding",
    "jewelry_type": "set",
    "metal_preference": "gold",
    "style": "Traditional Heritage Kundan",
    "total_budget": 150000.0,
    "currency": "INR",
    "budget_flexibility": "strict",
    "outfit_image_url": "https://storage.supabase.co/...",
    "outfit_storage_path": "user_id/outfits/outfit_abc.jpg",
    "outfit_description": "Emerald green silk lehenga with gold zardozi embroidery",
    "skin_tone": "warm",
    "special_requirements": "Hypoallergenic backings"
  }
  ```
- **Response** `200 OK`: Full `PlanDetailResponse`.

---

## 3. Plans & History Management

### `GET /plans`
List all plans created by the authenticated user.
- **Query Params**: `planner_type` (optional), `limit` (default 50), `offset` (default 0)
- **Response** `200 OK`: `list[PlanSummaryResponse]`

### `GET /plans/{plan_id}`
Retrieve a complete plan by ID including budget allocations, warnings, and recommendations.

### `DELETE /plans/{plan_id}`
Soft-delete or purge a plan owned by the user.

### `GET /history`
Paginated history endpoint with metadata and quick summaries.

---

## 4. Bookmarking & Recommendations

### `POST /recommendations/{recommendation_id}/save`
Bookmark a recommendation.

### `DELETE /recommendations/{recommendation_id}/save`
Unbookmark a recommendation.

### `GET /recommendations/saved`
Retrieve all bookmarked items for the active user.

---

## 5. Storage & Image Uploads

### `POST /images/upload`
Upload an image to Supabase Storage.
- **Headers**: `Authorization: Bearer <token>`
- **Content-Type**: `multipart/form-data`
- **Form Fields**: `file` (Binary JPEG/PNG/WebP, max 10MB), `plan_id` (optional), `image_type` (`outfit` | `avatar` | `inspiration`)
- **Response** `201 Created`:
  ```json
  {
    "file_url": "https://supabase-url/storage/v1/object/public/outfits/uuid.jpg",
    "storage_path": "uuid/outfits/uuid.jpg",
    "file_name": "uuid.jpg",
    "content_type": "image/jpeg",
    "size_bytes": 1048576
  }
  ```
