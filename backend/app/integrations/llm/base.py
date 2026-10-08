from abc import ABC, abstractmethod


class ResumeExtractorBackend(ABC):
    @abstractmethod
    def extract(self, resume_text: str) -> dict:
        """Return raw JSON-shaped dict matching the expected resume data schema."""