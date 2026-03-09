from typing import List
from pydantic import BaseModel


class AuthorSubjectAreasResponseDTO(BaseModel):
    """DTO para respuesta de áreas temáticas de un autor."""
    author_id: str
    scopus_ids: List[str] = []
    subject_areas: List[str]