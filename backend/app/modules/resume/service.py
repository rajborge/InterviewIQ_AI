from sqlalchemy.orm import Session

from app.database.models.resume import Resume
from app.storage.local import LocalStorage
from .extraction import extract_text_from_pdf
from .validation import validate_resume_file

storage = LocalStorage(base_dir="uploads/resumes")


def upload_resume(db: Session, user_id, filename: str, content: bytes) -> Resume:
    validate_resume_file(content)

    stored_path = storage.save(content, filename)
    extracted_text = extract_text_from_pdf(content)

    resume = Resume(
        user_id=user_id,
        file_path=stored_path,
        extracted_text=extracted_text,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume