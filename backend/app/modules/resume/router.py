from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.exceptions import FileTooLargeError, InvalidFileTypeError
from app.database.dependencies import get_db
from app.database.dependencies import get_current_user
from app.database.models.user import User
from .schemas import ResumeResponse
from .service import upload_resume

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