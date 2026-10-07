from fastapi import FastAPI

from app.database import base
from app.modules.auth.router import router as auth_router
from app.modules.resume.router import router as resumes_router

app=FastAPI()

app.include_router(auth_router)
app.include_router(resumes_router)