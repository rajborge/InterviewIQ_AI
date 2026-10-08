import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    file_path: str
    extracted_text: str | None
    created_at: datetime
    

class ExtractedSkill(BaseModel):
    skill_name: str


class ExtractedProject(BaseModel):
    title: str
    description: str | None = None
    technologies_used: str | None = None


class ExtractedEducation(BaseModel):
    institution: str
    degree: str | None = None
    field: str | None = None


class ExtractedExperience(BaseModel):
    company: str
    role: str
    description: str | None = None


class ExtractedResumeData(BaseModel):
    skills: list[ExtractedSkill] = []
    projects: list[ExtractedProject] = []
    education: list[ExtractedEducation] = []
    experience: list[ExtractedExperience] = []