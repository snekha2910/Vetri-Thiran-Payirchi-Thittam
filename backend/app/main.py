from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.exceptions import PocketSmartException
from app.api.router import api_v1_router

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title=settings.app_name,
    description="PocketSmart AI — Complete Financial & Lifestyle Budgeting Engine API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
origins = settings.cors_origins if isinstance(settings.cors_origins, list) else [settings.cors_origins]
origins = [o.rstrip("/") for o in origins if o]

if settings.is_development:
    dev_origins = {
        "http://localhost:8080",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    }
    origins = list(set(origins).union(dev_origins))

cors_kwargs = {
    "allow_origins": origins,
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
    "expose_headers": ["*"],
}
if settings.is_development:
    cors_kwargs["allow_origin_regex"] = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"

app.add_middleware(
    CORSMiddleware,
    **cors_kwargs
)

# Exception handlers
@app.exception_handler(PocketSmartException)
async def pocketsmart_exception_handler(request: Request, exc: PocketSmartException):
    headers = {}
    if hasattr(exc, "retry_after") and exc.retry_after:
        headers["Retry-After"] = str(exc.retry_after)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": exc.code,
            "message": exc.message,
            "details": exc.details
        },
        headers=headers if headers else None
    )

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        safe_err = {
            "field": ".".join(str(loc) for loc in err.get("loc", [])),
            "message": str(err.get("msg", "Validation error"))
        }
        errors.append(safe_err)
    # Using 422 Unprocessable Content
    status_code = getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", status.HTTP_422_UNPROCESSABLE_ENTITY)
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "code": "VALIDATION_ERROR",
            "message": "Invalid request parameters",
            "details": errors
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "code": "INTERNAL_SERVER_ERROR",
            "message": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )

# Include API Router
app.include_router(api_v1_router)

@app.get("/", tags=["Root"])
async def root():
    return {
        "service": settings.app_name,
        "docs_url": "/docs",
        "api_v1": "/api/v1"
    }
