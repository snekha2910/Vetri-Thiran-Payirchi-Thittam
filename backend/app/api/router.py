from fastapi import APIRouter
from app.api.v1.health import router as health_router
from app.api.v1.auth import router as auth_router
from app.api.v1.profile import router as profile_router
from app.api.v1.home import router as home_router
from app.api.v1.party import router as party_router
from app.api.v1.jewelry import router as jewelry_router
from app.api.v1.plans import router as plans_router
from app.api.v1.recommendations import router as recs_router
from app.api.v1.history import router as history_router
from app.api.v1.images import router as images_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(profile_router)
api_v1_router.include_router(home_router)
api_v1_router.include_router(party_router)
api_v1_router.include_router(jewelry_router)
api_v1_router.include_router(plans_router)
api_v1_router.include_router(recs_router)
api_v1_router.include_router(history_router)
api_v1_router.include_router(images_router)
