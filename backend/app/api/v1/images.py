import logging
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, status
from app.core.security import AuthenticatedUser
from app.core.dependencies import get_current_user
from app.services.image_service import ImageService
from app.repositories.plan_repository import plan_repository
from app.integrations.supabase_client import supabase_manager
from app.core.config import settings
from app.core.exceptions import InvalidImageError, NotFoundError, AuthorizationError, PocketSmartException

logger = logging.getLogger("pocketsmart.images")

router = APIRouter(prefix="/images", tags=["Images"])

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    plan_id: Optional[str] = Form(None),
    image_type: Optional[str] = Form("outfit"),
    user: AuthenticatedUser = Depends(get_current_user)
):
    # Verify plan ownership if plan_id is provided
    if plan_id:
        plan = await plan_repository.get_plan_by_id(plan_id)
        if not plan:
            raise NotFoundError("Specified plan was not found")
        if str(plan.get("user_id")) != str(user.id):
            raise AuthorizationError("Access denied: You do not own this plan")

    # Safe chunked reading with hard size limit enforcement
    chunks = []
    total_size = 0
    max_size = ImageService.MAX_FILE_SIZE_BYTES
    chunk_size = 64 * 1024  # 64 KB

    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > max_size:
            raise InvalidImageError(f"Image exceeds maximum allowable limit of {max_size // (1024 * 1024)}MB")
        chunks.append(chunk)

    content = b"".join(chunks)
    ImageService.validate_image(content, file.content_type or "image/jpeg", file.filename or "upload.jpg")

    clean_filename = ImageService.generate_filename(file.filename or "upload.jpg")
    storage_path = ImageService.get_storage_path(user.id, plan_id, clean_filename)
    bucket_name = "planner-images"

    # Persist directly to Supabase Storage bucket
    if supabase_manager.is_connected:
        try:
            supabase_manager.client.storage.from_(bucket_name).upload(
                path=storage_path,
                file=content,
                file_options={"content-type": file.content_type or "image/jpeg", "upsert": "true"}
            )
        except Exception as e:
            logger.warning(f"Supabase storage upload notice: {e}")

    if settings.supabase_url:
        public_url = f"{settings.supabase_url.rstrip('/')}/storage/v1/object/public/{bucket_name}/{storage_path}"
    else:
        public_url = f"/storage/v1/object/public/{bucket_name}/{storage_path}"

    return {
        "file_url": public_url,
        "storage_path": storage_path,
        "file_name": clean_filename,
        "content_type": file.content_type,
        "size_bytes": len(content)
    }
