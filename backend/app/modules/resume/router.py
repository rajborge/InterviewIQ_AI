from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.exceptions import FileTooLargeError, InvalidFileTypeError

from app.database.dependencies import get_db
from app.database.dependencies import get_current_user

from app.database.models.user import User
from app.database.models.resume import Resume

from .schemas import ResumeResponse
from .service import upload_resume,extract_resume_details,ExtractionFailedError

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload(
    file: UploadFile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeResponse:
    content = await file.read()

    try:
        resume = upload_resume(db, current_user.id, file.filename, content)
    except InvalidFileTypeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except FileTooLargeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return resume

@router.post("/{resume_id}/extract-details", response_model=ResumeResponse)
def extract_details(
    resume_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeResponse:
    resume = db.scalar(select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id))
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    try:
        resume = extract_resume_details(db, resume)
    except ExtractionFailedError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))

    return resume