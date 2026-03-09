"""Authentication endpoints."""

from fastapi import APIRouter, HTTPException, Request, status

from ..auth import verify_google_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
async def auth_me(request: Request):
    """Return the authenticated user's profile from a Google ID token."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )

    token = auth_header[len("Bearer "):]
    user_info = verify_google_token(token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired Google token",
        )

    return {
        "id": user_info["sub"],
        "email": user_info["email"],
        "name": user_info["name"],
        "picture": user_info["picture"],
    }
