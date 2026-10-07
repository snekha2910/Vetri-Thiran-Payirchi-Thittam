# PocketSmart AI — Security Architecture & Guidelines

## Security Controls Overview

PocketSmart AI is architected according to industry security best practices to protect user financial data, credentials, and image uploads.

---

## 1. Authentication & JWT Verification

* **Supabase JWT Validation**: FastAPI endpoints decode and verify JWT signatures with Supabase public keys and check expiration timestamps.
* **Multi-Tenant Data Isolation**: Every resource (plans, recommendations, profile) is strictly scoped to `user_id`. Cross-user access returns HTTP 403 / 404.
* **Row-Level Security (RLS)**: PostgreSQL policies prevent direct data leaks even if database queries are executed outside the application scope.

---

## 2. Input Validation & Defense in Depth

* **Pydantic v2**: All input payloads are strictly validated against strongly-typed schemas with range bounds (e.g. positive budgets, valid enum choices).
* **MIME & Magic Byte Verification**: File uploads undergo binary inspection (`validate_image`) to ensure only authentic JPEG, PNG, and WebP images are accepted. Executable extensions and oversized payloads (> 10MB) are immediately rejected.
* **UUID Path Sanitization**: Uploaded files are assigned UUID names to prevent path traversal or overwriting attacks.

---

## 3. Network & CORS

* **Configurable CORS**: Cross-Origin Resource Sharing is locked down via `CORS_ORIGINS` environment variables. Wildcard `*` is disallowed in production.
* **Rate Limiting & Abuse Prevention**: Critical endpoints (Auth, Image uploads, and AI Generation) are structured for rate limiting.

---

## 4. Secret Management

* All secret keys (`GEMINI_API_KEY`, `SUPABASE_SERVICE_ROLE_KEY`) are kept exclusively on the server side and never bundled into frontend assets.
