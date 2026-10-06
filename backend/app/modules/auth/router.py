from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session

from app.core.exceptions import EmailAlreadyExistsError,InvalidCredentialsError,OAuthOnlyAccountError,InvalidRefreshTokenError
from app.database.dependencies import get_db,get_current_user
from .schemas import UserRegisterRequest,UserResponse,UserLoginRequest,TokenResponse,RefreshRequest
from .service import register_user,login_user,refresh_access_token,logout_user

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