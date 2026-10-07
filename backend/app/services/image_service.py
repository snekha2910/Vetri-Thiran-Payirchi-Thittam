import uuid
from typing import Optional
from app.core.exceptions import InvalidImageError

MAGIC_NUMBERS = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/webp": [b"RIFF"]
}

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB

class ImageService:
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_BYTES

    @staticmethod
    def validate_image(content: bytes, content_type: str, filename: str) -> None:
        if not content:
            raise InvalidImageError("Uploaded image file is empty")
        
        if len(content) > MAX_FILE_SIZE_BYTES:
            raise InvalidImageError(f"File size exceeds maximum permitted limit of {MAX_FILE_SIZE_BYTES // (1024 * 1024)}MB")

        if content_type not in MAGIC_NUMBERS:
            raise InvalidImageError(f"Unsupported image content type '{content_type}'. Must be JPEG, PNG, or WebP.")

        # Check extension
        dot_idx = filename.rfind(".")
        if dot_idx == -1 or filename[dot_idx:].lower() not in ALLOWED_EXTENSIONS:
            raise InvalidImageError(f"Invalid file extension in '{filename}'. Allowed: .jpg, .jpeg, .png, .webp")

        # Validate magic bytes
        valid_magics = MAGIC_NUMBERS[content_type]
        has_valid_magic = any(content.startswith(magic) for magic in valid_magics)
        if not has_valid_magic:
            raise InvalidImageError(f"File content does not match reported MIME type '{content_type}'")

    @staticmethod
    def generate_filename(original_filename: str) -> str:
        dot_idx = original_filename.rfind(".")
        ext = original_filename[dot_idx:].lower() if dot_idx != -1 else ".jpg"
        return f"{uuid.uuid4()}{ext}"

    @staticmethod
    def get_storage_path(user_id: str, plan_id: Optional[str], filename: str) -> str:
        if plan_id:
            return f"{user_id}/{plan_id}/{filename}"
        return f"{user_id}/uploads/{filename}"
