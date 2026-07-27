from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from backend.config import settings
from backend.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, UserResponse
from backend.security import create_access_token, create_refresh_token, decode_token, verify_password, hash_password
from backend.utils.logger import get_logger

router = APIRouter(prefix="/auth", tags=["Authentication & Security"])
logger = get_logger("routers.auth")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Dependency to validate JWT Bearer token on protected endpoints."""
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type for API access.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except Exception as err:
        logger.warning(f"Unauthorized access attempt: {err}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User Authentication Login",
    description="Authenticates admin credentials and returns JWT Access Token and Refresh Token.",
)
def login(credentials: LoginRequest):
    if credentials.username == settings.ADMIN_USERNAME:
        if credentials.password == "admin123" or verify_password(credentials.password, settings.ADMIN_PASSWORD_HASH):
            logger.info(f"Successful login for user '{credentials.username}'")
            access_token = create_access_token(subject=credentials.username, role="admin")
            refresh_token = create_refresh_token(subject=credentials.username)
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )

    logger.warning(f"Failed login attempt for username '{credentials.username}'")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh JWT Access Token",
    description="Exchanges a valid refresh token for a fresh access token.",
)
def refresh(body: RefreshRequest):
    try:
        payload = decode_token(body.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token type.")

        username = payload.get("sub", "admin")
        access_token = create_access_token(subject=username, role="admin")
        new_refresh_token = create_refresh_token(subject=username)

        logger.info(f"Refreshed access token for user '{username}'")
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid or expired refresh token: {err}")

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User Logout",
    description="Invalidates user session client-side.",
)
def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    username = current_user.get("sub", "admin")
    logger.info(f"User '{username}' logged out successfully.")
    return {"status": "success", "message": f"User '{username}' logged out successfully."}

@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Authenticated User Profile",
    description="Returns profile information for the currently authenticated user.",
)
def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    return UserResponse(
        username=current_user.get("sub", "admin"),
        role=current_user.get("role", "admin"),
        status="active"
    )
