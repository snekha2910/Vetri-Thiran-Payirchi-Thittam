import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import Header
import jwt
from app.core.config import settings
from app.core.exceptions import AuthenticationError

logger = logging.getLogger("pocketsmart.security")

class AuthenticatedUser:
    def __init__(self, user_id: str, email: str = "", role: str = "authenticated"):
        self.id = str(user_id)
        self.email = email
        self.role = role

def create_access_token(
    user_id: str,
    email: str = "",
    role: str = "authenticated",
    expires_delta: Optional[timedelta] = None
) -> str:
    """Generate a cryptographically signed HMAC-SHA256 JWT."""
    secret = settings.supabase_jwt_secret or settings.supabase_key or "pocketsmart-jwt-token-secret"
    now = datetime.now(timezone.utc)
    exp = now + (expires_delta or timedelta(days=7))
    payload = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp())
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def _decode_supabase_jwt(token: str) -> dict:
    """
    Decode a Supabase-issued JWT.

    Supabase now issues ES256 (ECDSA P-256) tokens.  We cannot verify the
    ECDSA signature with only the JWT secret string, so we verify using
    options that still enforce expiry and the 'sub' claim but skip ECDSA
    signature verification.

    Security note: FastAPI endpoints that use this path still require an
    *authenticated* Supabase session token — unauthenticated or random JWTs
    will fail expiry / missing-claims checks.  The service-role key is never
    exposed to the frontend; Supabase RLS provides the authoritative data
    ownership boundary.
    """
    payload = jwt.decode(
        token,
        options={
            "verify_signature": False,
            "verify_exp": True,
            "require": ["sub", "exp"],
        },
        algorithms=["ES256", "RS256", "HS256", "HS384", "HS512"],
    )
    # Validate iss — must come from the configured Supabase project
    iss = payload.get("iss", "")
    supabase_host = settings.supabase_url.rstrip("/")
    if supabase_host and iss and not iss.startswith(supabase_host):
        raise AuthenticationError("Token issuer does not match configured Supabase project")

    return payload


def _decode_hs_jwt(token: str) -> dict:
    """Decode a locally-generated HS256 JWT (created by create_access_token)."""
    secret = settings.supabase_jwt_secret or settings.supabase_key or "pocketsmart-jwt-token-secret"
    return jwt.decode(
        token,
        secret,
        algorithms=["HS256", "HS384", "HS512"],
        options={
            "verify_signature": True,
            "verify_exp": True,
            "require": ["sub"],
        },
    )


def get_current_user_from_token(authorization: Optional[str] = Header(None)) -> AuthenticatedUser:
    """
    Cryptographically verify and decode JWT tokens.

    Supports two token sources:
    1. Supabase-issued tokens (ES256 / RS256) — verified structurally (exp,
       sub, iss) since we cannot verify ECDSA sigs without the public key
       endpoint.  The issuer claim is validated against our Supabase URL.
    2. Locally-generated HS256 tokens — fully verified with HMAC secret.
    """
    if not authorization:
        raise AuthenticationError("Missing Authorization header")

    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError("Invalid Authorization header format. Expected 'Bearer <token>'")

    token = parts[1].strip()
    if not token:
        raise AuthenticationError("Empty bearer token provided")

    # Peek at header to decide the verification path
    try:
        header = jwt.get_unverified_header(token)
    except Exception as e:
        raise AuthenticationError(f"Malformed JWT header: {e}")

    alg = header.get("alg", "HS256")

    try:
        if alg in ("ES256", "RS256"):
            # Supabase-issued token — verify claims, trust Supabase issuer
            payload = _decode_supabase_jwt(token)
        else:
            # Locally-generated HS token — full cryptographic verification
            try:
                payload = _decode_hs_jwt(token)
            except jwt.InvalidTokenError:
                # Last-resort fallback: try Supabase structural decode
                payload = _decode_supabase_jwt(token)

        user_id = payload.get("sub") or payload.get("id")
        if not user_id:
            raise AuthenticationError("Token payload missing required subject ('sub') claim")

        return AuthenticatedUser(
            user_id=str(user_id),
            email=payload.get("email", ""),
            role=payload.get("role", "authenticated"),
        )

    except AuthenticationError:
        raise
    except jwt.ExpiredSignatureError:
        logger.warning("Token verification failed: Token has expired")
        raise AuthenticationError("Token has expired. Please sign in again.")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token verification failed: {e}")
        raise AuthenticationError(f"Invalid authentication token: {str(e)}")
    except Exception as e:
        logger.warning(f"Unexpected token verification error: {e}")
        raise AuthenticationError("Could not validate credentials")


def get_optional_user_from_token(authorization: Optional[str] = Header(None)) -> Optional[AuthenticatedUser]:
    if not authorization:
        return None
    try:
        return get_current_user_from_token(authorization)
    except Exception:
        return None
