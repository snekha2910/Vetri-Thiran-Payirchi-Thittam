# PocketSmart AI — Deployment Guide

## Production Topology

- **Frontend**: Cloudflare Pages / Vercel / Netlify (SSR with Nitro / Vite static build)
- **Backend**: Render / Railway / Fly.io / AWS ECS / Google Cloud Run (Containerized FastAPI with Uvicorn)
- **Database & Auth**: Supabase Managed Cloud (PostgreSQL 15 + GoTrue Auth + S3 Storage)

---

## 1. Containerized Backend Deployment (Docker)

The repository includes a production-ready `backend/Dockerfile`.

### Build & Run Container Locally:
```bash
cd backend
docker build -t pocketsmart-backend:latest .
docker run -d -p 8000:8000 --env-file .env pocketsmart-backend:latest
```

### Dockerfile Highlights:
- Multi-stage Python 3.12 slim base image.
- Non-root user execution (`appuser`) for least privilege security.
- Production Uvicorn workers configured with gunicorn/uvicorn ASGI process management.

---

## 2. Deploying Backend to Cloud Run / Render / Railway

1. **Set Environment Variables in Provider Dashboard**:
   ```ini
   ENVIRONMENT=production
   PORT=8000
   SUPABASE_URL=https://<your-project>.supabase.co
   SUPABASE_KEY=<anon-key>
   SUPABASE_SERVICE_ROLE_KEY=<service-role-key>
   GEMINI_API_KEY=<google-gemini-api-key>
   GEMINI_MODEL=gemini-2.5-flash
   CORS_ORIGINS=https://your-frontend-domain.pages.dev
   ```

2. **Health Check Configuration**:
   - HTTP Path: `/api/v1/health`
   - Port: `8000`

---

## 3. Frontend Deployment (Cloudflare Pages / Vercel)

1. Set Build Command: `npm run build`
2. Set Output Directory: `.output/public`
3. Environment Variables:
   - `VITE_API_BASE_URL=https://your-backend-api.onrender.com/api/v1`
   - `VITE_SUPABASE_URL=https://<your-project>.supabase.co`
   - `VITE_SUPABASE_ANON_KEY=<anon-key>`
