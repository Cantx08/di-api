
from typing import List, Optional
from pydantic import BaseModel
from ..domain.publication import Publication


class PublicationResponseDTO(BaseModel):
    """DTO de respuesta para una publicación."""
    scopus_id: str
    eid: str
    doi: Optional[str]
    source_id: Optional[str]
    title: str
    year: int
    publication_date: str
    source_title: str
    document_type: str
    affiliation_name: str
    affiliation_id: Optional[str]
    subject_areas: List[str]
    categories_with_quartiles: List[str]
    sjr_year_used: Optional[int]

    @staticmethod
    def from_entity(publication: Publication) -> 'PublicationResponseDTO':
        return PublicationResponseDTO(
            scopus_id=publication.scopus_id,
            eid=publication.eid,
            doi=publication.doi,
            
            # Mapeamos el Sourceid de la revista
            source_id=publication.source_id,

            title=publication.title,
            year=publication.year,
            publication_date=publication.publication_date,
            source_title=publication.source_title,
            document_type=publication.document_type,
            affiliation_name=publication.affiliation_name,
            affiliation_id=publication.affiliation_id,
            subject_areas=publication.subject_areas,
            categories_with_quartiles=publication.categories_with_quartiles,
            sjr_year_used=publication.sjr_year_used
        )


class AuthorPublicationsResponseDTO(BaseModel):
    """DTO de respuesta para las publicaciones de un autor."""
    author_id: str
    scopus_ids: List[str]
    total_publications: int
    publications: List[PublicationResponseDTO]


class DocumentsByYearDTO(BaseModel):
    """DTO para estadísticas de documentos por año."""
    year: int
    count: int


class PublicationsStatsResponseDTO(BaseModel):
    """DTO de respuesta para estadísticas de publicaciones."""
    author_id: str
    total_publications: int
    documents_by_year: List[DocumentsByYearDTO]
    documents_by_type: dict
