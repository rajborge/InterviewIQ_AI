import json

from google import genai

from app.core.config import settings
from .base import ResumeExtractorBackend

EXTRACTION_PROMPT = """You are extracting structured data from a resume's raw text.
Return ONLY valid JSON matching this exact shape, with no extra commentary:

{{
  "skills": [{{"skill_name": "string"}}],
  "projects": [{{"title": "string", "description": "string or null", "technologies_used": "string or null"}}],
  "education": [{{"institution": "string", "degree": "string or null", "field": "string or null"}}],
  "experience": [{{"company": "string", "role": "string", "description": "string or null"}}]
}}

If a section is not present in the resume, return an empty list for it. Do not invent data that isn't in the text.

Resume text:
{resume_text}
"""


class GeminiResumeExtractor(ResumeExtractorBackend):
    def __init__(self):
        self.client = genai.Client(api_key=settings.gemini_api_key)

    def extract(self, resume_text: str) -> dict:
        response = self.client.models.generate_content(
            model=settings.gemini_model,
            contents=EXTRACTION_PROMPT.format(resume_text=resume_text),
            config={"response_mime_type": "application/json"},
        )
        return json.loads(response.text)