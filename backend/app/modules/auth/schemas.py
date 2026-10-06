import uuid
from datetime import datetime

from pydantic import BaseModel,ConfigDict,EmailStr,Field

class UserRegisterRequest(BaseModel):
    email:EmailStr
    password:str=Field(min_length=8,max_length=128)
    name:str=Field(min_length=1,max_length=100)

class UserLoginRequest(BaseModel):
    email:EmailStr
    password:str

class UserResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)

    id:uuid.UUID
    email:str
    name:str
    created_at:datetime

class TokenResponse(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str="bearer"

class RefreshRequest(BaseModel):
    refresh_token:str