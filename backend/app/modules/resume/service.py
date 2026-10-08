from sqlalchemy.orm import Session

from app.database.models.resume import Resume
from app.database.models.resume_skill import ResumeSkill
from app.database.models.resume_projects import ResumeProject
from app.database.models.resume_experience import ResumeExperience
from app.database.models.resume_education import ResumeEducation

from app.storage.local import LocalStorage
from .extraction import extract_text_from_pdf
from .validation import validate_resume_file

from app.core.exceptions import AppError
from app.integrations.llm.gemini import GeminiResumeExtractor

from .schemas import ExtractedResumeData

from google.genai import errors as genai_errors

extractor = GeminiResumeExtractor()
storage = LocalStorage(base_dir="uploads/resumes")

class ExtractionFailedError(AppError):
    def __init__(self):
        super().__init__("Could not extract structured data from this resume")


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

def extract_resume_details(db: Session, resume: Resume) -> Resume:
    resume_id = resume.id
    text = resume.extracted_text
    if not text:
        raise ExtractionFailedError()

    db.commit()  # end the open read transaction before the slow external call

    try:
        raw_data = extractor.extract(text)
        validated = ExtractedResumeData.model_validate(raw_data)
    except (ValueError, KeyError, genai_errors.APIError):
        raise ExtractionFailedError()

    resume = db.get(Resume, resume_id)

    resume.skills = [ResumeSkill(skill_name=s.skill_name) for s in validated.skills]
    resume.projects = [
        ResumeProject(title=p.title, description=p.description, technologies_used=p.technologies_used)
        for p in validated.projects
    ]
    resume.education = [
        ResumeEducation(institution=e.institution, degree=e.degree, field=e.field)
        for e in validated.education
    ]
    resume.experiences = [
        ResumeExperience(company=x.company, role=x.role, description=x.description)
        for x in validated.experience
    ]

    db.commit()
    db.refresh(resume)
    return resume