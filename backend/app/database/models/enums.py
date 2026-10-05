import enum
from sqlalchemy import Enum as SAEnum

class InterviewType(str,enum.Enum):
    RESUME_BASED="resume_based"
    ROLE_BASED="role_based"

class InterviewMode(str,enum.Enum):
    PRACTICE="practice"
    STRICT="strict"

class Difficulty(str,enum.Enum):
    FRESHER="fresher"
    SENIOR="senior"
    EXPERT="expert"

class InterviewStatus(str,enum.Enum):
    IN_PROGRESS="in_progress"
    COMPLETED="completed"
    ABANDONED="abandoned"

class RoundType(str,enum.Enum):
    TECHNICAL="technical"
    APTITUDE="aptitude"
    HR="hr"

class QuestionSource(str,enum.Enum):
    QUESTION_BANK="question_bank"
    LLM_GENERATED="llm_generated"

class LightingQuality(str, enum.Enum):
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"

def db_enum(enum_cls:type[enum.Enum],name:str)->SAEnum:
    return SAEnum(
        enum_cls,
        name=name,
        native_enum=False,
        create_constraint=True,
        validate_strings=True,
        values_callable=lambda e:[m.value for m in e],
        length=30,
    )
    