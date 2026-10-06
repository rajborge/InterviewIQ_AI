from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

import secrets
import hashlib
from datetime import datetime,timedelta,timezone

import jwt
from jwt.exceptions import ExpiredSignatureError,InvalidTokenError

from .config import settings

ALGORITHM=settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES=settings.access_token_expire_minutes

_password_hasher=PasswordHasher()

def hash_password(plain_password:str)->str:
    return _password_hasher.hash(plain_password)

def verify_password(plain_password:str,password_hash:str)->bool:
    try:
        _password_hasher.verify(password_hash,plain_password)
        return True
    except VerifyMismatchError:
        return False
    
def create_access_token(user_id:str)->str:
    now=datetime.now(timezone.utc)
    payload={
        "sub":user_id,
        "iat":now,
        "exp":now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload,settings.secret_key,algorithm=ALGORITHM)

def decode_access_token(token:str)->dict:
    try:
        return jwt.decode(token,settings.secret_key,algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise ValueError("Access token has expired")
    except InvalidTokenError:
        raise ValueError("Access token is invalid")
    
def generate_refresh_token()->tuple[str,str]:
    raw_token=secrets.token_urlsafe(64)
    token_hash=hashlib.sha256(raw_token.encode()).hexdigest()
    return raw_token,token_hash