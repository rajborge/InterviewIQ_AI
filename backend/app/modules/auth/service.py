from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime,timezone,timedelta
import hashlib
import secrets as secrets_module
from urllib.parse import urlencode

import httpx
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from app.core.exceptions import EmailAlreadyExistsError,InvalidCredentialsError,OAuthOnlyAccountError,InvalidRefreshTokenError,AppError
from app.core.security import hash_password,create_access_token,generate_refresh_token,verify_password

from app.database.models.user import User
from app.database.models.refresh_token import RefreshToken
from app.database.models.oauth_exchange_code import OAuthExchangeCode

from .schemas import UserRegisterRequest,UserLoginRequest
from app.core.config import settings

REFRESH_TOKEN_EXPIRE_DAYS=30

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
EXCHANGE_CODE_EXPIRE_SECONDS = 60

class OAuthError(AppError):
    def __init__(self, message: str = "Google sign-in failed"):
        super().__init__(message)


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


def build_google_auth_url() -> str:
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
        "prompt": "select_account",
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

def handle_google_callback(db: Session, code: str) -> str:
    token_response = httpx.post(
        GOOGLE_TOKEN_URL,
        data={
            "code": code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": settings.google_redirect_uri,
            "grant_type": "authorization_code",
        },
    )
    if token_response.status_code != 200:
        raise OAuthError()

    google_tokens = token_response.json()
    raw_id_token = google_tokens.get("id_token")
    if raw_id_token is None:
        raise OAuthError()

    try:
        claims = google_id_token.verify_oauth2_token(
            raw_id_token, google_requests.Request(), settings.google_client_id
        )
    except ValueError:
        raise OAuthError()

    google_sub = claims["sub"]
    email = claims["email"]
    name = claims.get("name", email)

    user = db.scalar(select(User).where(User.google_id == google_sub))

    if user is None:
        user = db.scalar(select(User).where(User.email == email))
        if user is not None:
            user.google_id = google_sub  
        else:
            user = User(email=email, name=name, password_hash=None, google_id=google_sub)
            db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(user_id=str(user.id))
    raw_refresh_token, refresh_token_hash = generate_refresh_token()
    db.add(RefreshToken(
        user_id=user.id,
        token_hash=refresh_token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    ))
    db.commit()

    raw_exchange_code = secrets_module.token_urlsafe(32)
    exchange_code_hash = hashlib.sha256(raw_exchange_code.encode()).hexdigest()
    db.add(OAuthExchangeCode(
        code_hash=exchange_code_hash,
        access_token=access_token,
        refresh_token=raw_refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=EXCHANGE_CODE_EXPIRE_SECONDS),
    ))
    db.commit()

    return raw_exchange_code

def redeem_exchange_code(db: Session, raw_code: str) -> tuple[str, str]:
    code_hash = hashlib.sha256(raw_code.encode()).hexdigest()
    row = db.scalar(select(OAuthExchangeCode).where(OAuthExchangeCode.code_hash == code_hash))

    if row is None or row.used or row.expires_at < datetime.now(timezone.utc):
        raise OAuthError("Invalid or expired exchange code")

    row.used = True
    db.commit()

    return row.access_token, row.refresh_token