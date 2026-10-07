from fastapi import APIRouter
from app.core.config import settings
from app.integrations.supabase_client import supabase_manager
from app.integrations.gemini_client import gemini_manager

router = APIRouter()

@router.get("/health", tags=["Health"])
async def health_check():
    gemini_reachable = gemini_manager.check_reachability() if gemini_manager.is_configured else False
    is_gemini_ok = gemini_reachable or gemini_manager.is_configured
    
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.environment,
        "supabase_connected": supabase_manager.is_connected,
        "gemini_connected": is_gemini_ok,
        "gemini_configured": gemini_manager.is_configured,
        "gemini_reachable": gemini_reachable,
        "gemini_model": settings.gemini_model,
    }
