from fastapi import Depends
from app.core.security import AuthenticatedUser, get_current_user_from_token, get_optional_user_from_token

def get_current_user(user: AuthenticatedUser = Depends(get_current_user_from_token)) -> AuthenticatedUser:
    return user

def get_optional_user(user: AuthenticatedUser | None = Depends(get_optional_user_from_token)) -> AuthenticatedUser | None:
    return user
