from fastapi import APIRouter,Depends,HTTPException,status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.exceptions import EmailAlreadyExistsError,InvalidCredentialsError,OAuthOnlyAccountError,InvalidRefreshTokenError
from app.database.dependencies import get_db,get_current_user
from .schemas import UserRegisterRequest,UserResponse,UserLoginRequest,TokenResponse,RefreshRequest,ExchangeCodeRequest
from .service import register_user,login_user,refresh_access_token,logout_user,build_google_auth_url,handle_google_callback,redeem_exchange_code,OAuthError


from app.database.models.user import User

router=APIRouter(prefix="/auth",tags=["auth"])

@router.post("/register",response_model=UserResponse,status_code=status.HTTP_201_CREATED)
def register(
    data:UserRegisterRequest,
    db:Session=Depends(get_db)
    )->UserResponse:
    try:
        user=register_user(db,data)
    except EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists."
        )
    return user

@router.post("/login",response_model=TokenResponse)
def login(
    data:UserLoginRequest,
    db:Session=Depends(get_db),
)->TokenResponse:
    try:
        access_token,refresh_token=login_user(db,data)
    except InvalidCredentialsError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid email or password")
    except OAuthOnlyAccountError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=str(e))
    
    return TokenResponse(access_token=access_token,refresh_token=refresh_token)


@router.post("/refresh",response_model=TokenResponse)
def refresh(
    data:RefreshRequest,
    db:Session=Depends(get_db),
)->TokenResponse:
    try:
        access_token,refresh_token=refresh_access_token(db,data.refresh_token)
    except InvalidRefreshTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=str(e))
    
    return TokenResponse(access_token=access_token,refresh_token=refresh_token)

@router.post("/logout",status_code=status.HTTP_204_NO_CONTENT)
def logout(
    data:RefreshRequest,
    db:Session=Depends(get_db),
)->None:
    logout_user(db,data.refresh_token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return current_user


@router.get("/google/login")
def google_login() -> RedirectResponse:
    return RedirectResponse(url=build_google_auth_url())


@router.get("/google/callback")
def google_callback(code: str, db: Session = Depends(get_db)) -> RedirectResponse:
    try:
        exchange_code = handle_google_callback(db, code)
    except OAuthError:
        return RedirectResponse(url="http://localhost:5173/login?error=oauth_failed")

    return RedirectResponse(url=f"http://localhost:5173/oauth/callback?code={exchange_code}")



@router.post("/google/exchange", response_model=TokenResponse)
def google_exchange(data: ExchangeCodeRequest, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        access_token, refresh_token = redeem_exchange_code(db, data.code)
    except OAuthError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)