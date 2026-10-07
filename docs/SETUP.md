# PocketSmart AI — Local Development & Setup Guide

## Prerequisites

- **Python**: 3.11 or 3.12 installed
- **Node.js**: 18+ or 20+ (with npm or bun)
- **Supabase**: Active Supabase project (or local Supabase CLI)
- **Gemini API Key**: From Google AI Studio (optional for dev with mock providers)

---

## 1. Backend Setup

1. **Navigate to Backend Directory**:
   ```bash
   cd backend
   ```

2. **Create and Activate Virtual Environment**:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Fill in your configuration:
   ```ini
   ENVIRONMENT=development
   PORT=8000
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-supabase-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
   GEMINI_API_KEY=your-gemini-api-key
   GEMINI_MODEL=gemini-2.5-flash
   CORS_ORIGINS=http://localhost:5173,http://localhost:3000
   ```

5. **Run Database Migrations**:
   Open Supabase SQL Editor and execute the contents of:
   `supabase/migrations/001_initial_schema.sql`

6. **Start Backend Server**:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   * Swagger Documentation: `http://localhost:8000/docs`
   * Health Check: `http://localhost:8000/api/v1/health`

---

## 2. Frontend Setup

1. **Navigate to Frontend Directory**:
   ```bash
   cd frontend
   ```

2. **Install Node Dependencies**:
   ```bash
   npm install
   ```

3. **Configure Environment Variables**:
   Create or verify `.env`:
   ```ini
   VITE_API_BASE_URL=http://localhost:8000/api/v1
   VITE_SUPABASE_URL=https://your-project.supabase.co
   VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
   ```

4. **Start Frontend Dev Server**:
   ```bash
   npm run dev
   ```
   The application will be accessible at `http://localhost:5173`.

---

## 3. Running Automated Tests

Run backend unit and integration test suite:
```bash
cd backend
python -m pytest tests/ -v
```
All 57 tests should pass cleanly.
