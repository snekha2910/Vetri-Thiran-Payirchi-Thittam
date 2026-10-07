from typing import Optional, Dict, Any
from pydantic import EmailStr, Field
from app.schemas.common import BaseSchema

class RegisterRequest(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password at least 6 characters")
    full_name: str = Field("", description="User full name")

class LoginRequest(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=1)

class UserResponse(BaseSchema):
    id: str
    email: str
    full_name: str = ""
    fullName: Optional[str] = None
    token: str = ""
    access_token: Optional[str] = None
    accessToken: Optional[str] = None
    avatar_url: Optional[str] = None
    avatarUrl: Optional[str] = None
    created_at: Optional[str] = None
    createdAt: Optional[str] = None
    user: Optional[Dict[str, Any]] = None

    def __init__(self, **data):
        super().__init__(**data)
        name = data.get("full_name") or data.get("fullName") or ""
        self.full_name = name
        self.fullName = name
        t = data.get("token") or data.get("access_token") or data.get("accessToken") or ""
        self.token = t
        self.access_token = t
        self.accessToken = t
        avatar = data.get("avatar_url") or data.get("avatarUrl")
        self.avatar_url = avatar
        self.avatarUrl = avatar
        created = data.get("created_at") or data.get("createdAt")
        self.created_at = created
        self.createdAt = created
        if not self.user:
            self.user = {
                "id": self.id,
                "email": self.email,
                "full_name": name,
                "fullName": name,
                "avatar_url": avatar,
                "avatarUrl": avatar,
                "created_at": created,
                "createdAt": created,
            }

class ProfileUpdateRequest(BaseSchema):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
