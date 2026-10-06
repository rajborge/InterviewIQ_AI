from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime,timezone,timedelta
import hashlib

from app.core.exceptions import EmailAlreadyExistsError,InvalidCredentialsError,OAuthOnlyAccountError,InvalidRefreshTokenError
from app.core.security import hash_password,create_access_token,generate_refresh_token,verify_password

from app.database.models.user import User
from app.database.models.refresh_token import RefreshToken

from .schemas import UserRegisterRequest,UserLoginRequest

REFRESH_TOKEN_EXPIRE_DAYS=30

def register_user(db:Session,data:UserRegisterRequest)->User:
    existing=db.scalar(select(User).where(User.email==data.email))
    if existing is not None:
        raise EmailAlreadyExistsError(data.email)
    
    user=User(
        email=data.email,
        password_hash=hash_password(data.password),
        name=data.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(
        db:Session,
        data:UserLoginRequest
)->tuple[str,str]:
    user=db.scalar(select(User).where(User.email==data.email))

    if user is None:
        raise InvalidCredentialsError()
    
    if user.password_hash is None:
        raise OAuthOnlyAccountError()
    
    if not verify_password(data.password,user.password_hash):
        raise InvalidCredentialsError()
    
    access_token=create_access_token(user_id=str(user.id))

    raw_refresh_token,refresh_token_hash=generate_refresh_token()
    refresh_token_row=RefreshToken(
        user_id=user.id,
        token_hash=refresh_token_hash,
        expires_at=datetime.now(timezone.utc)+timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    db.add(refresh_token_row)
    db.commit()

    return access_token,raw_refresh_token


def refresh_access_token(
        db:Session,
        raw_refresh_token:str
)->tuple[str,str]:
    token_hash=hashlib.sha256(raw_refresh_token.encode()).hexdigest()

    token_row=db.scalar(select(RefreshToken).where(RefreshToken.token_hash==token_hash))

    if token_row is None:
        raise InvalidRefreshTokenError()
    
    now=datetime.now(timezone.utc)
    if token_row.is_revoked or token_row.expires_at<now:
        raise InvalidRefreshTokenError()
    
    token_row.is_revoked=True

    new_access_token=create_access_token(user_id=str(token_row.user_id))
    new_raw_refresh_token,new_refresh_token_hash=generate_refresh_token()

    new_token_row=RefreshToken(
        user_id=token_row.user_id,
        token_hash=new_refresh_token_hash,
        expires_at=now+timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    )

    db.add(new_token_row)
    db.commit()

    return new_access_token,new_raw_refresh_token


def logout_user(
        db:Session,
        raw_refresh_token:str
)->None:
    token_hash=hashlib.sha256(raw_refresh_token.encode()).hexdigest()

    token_row=db.scalar(select(RefreshToken).where(RefreshToken.token_hash==token_hash))

    if token_row is not None:
        token_row.is_revoked=True
        db.commit()