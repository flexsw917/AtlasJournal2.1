from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session

from app.api.deps import get_db
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.schemas.auth import LoginRequest, RefreshRequest, SignupRequest, TokenPair, UserRead
from app.services.user_service import authenticate_user, create_user

router = APIRouter()

COOKIE_NAME = "access_token"
COOKIE_PARAMS = {"httponly": True, "samesite": "lax", "secure": False}


def _set_cookie(response: Response, token: str) -> None:
    response.set_cookie(COOKIE_NAME, token, **COOKIE_PARAMS)


def _clear_cookie(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME)


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, session: Session = Depends(get_db)) -> UserRead:
    user = create_user(session, payload.email, payload.password)
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, response: Response, session: Session = Depends(get_db)) -> TokenPair:
    user = authenticate_user(session, payload.email, payload.password)
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    _set_cookie(response, access_token)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout")
def logout(response: Response) -> dict[str, str]:
    _clear_cookie(response)
    return {"status": "logged_out"}


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, response: Response) -> TokenPair:
    try:
        decoded = decode_token(payload.refresh_token)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc
    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user_id = decoded.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    access_token = create_access_token(str(user_id))
    refresh_token = create_refresh_token(str(user_id))
    _set_cookie(response, access_token)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)
