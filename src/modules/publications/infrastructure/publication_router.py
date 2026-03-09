"""Router para el módulo de publicaciones. Sin dependencias de base de datos."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from .scopus_publication_repository import ScopusPublicationRepository
from .sjr_file_repository import SJRFileRepository
from .scopus_author_subject_area_repository import ScopusAuthorSubjectAreaRepository
from ..application.publication_dto import (
    PublicationResponseDTO,
    AuthorPublicationsResponseDTO,
)
from ..application.subject_area_dto import AuthorSubjectAreasResponseDTO
from ..application.publication_service import PublicationService
from ..application.subject_area_service import SubjectAreaService
from ....container import get_container

router = APIRouter(prefix="/publications", tags=["Publicaciones"])


def get_service() -> PublicationService:
    """
    Factory para crear el servicio de publicaciones con sus dependencias.
    Ya no requiere base de datos.
    """
    container = get_container()

    publication_repo = ScopusPublicationRepository(
        api_key=container.settings.SCOPUS_API_KEY
    )
    sjr_repo = SJRFileRepository(csv_path=container.settings.SJR_CSV_PATH)

    return PublicationService(
        publication_repo=publication_repo,
        sjr_repo=sjr_repo,
    )


def get_subject_area_service() -> SubjectAreaService:
    """
    Factory para crear el servicio de áreas temáticas.
    Ya no requiere base de datos.
    """
    container = get_container()

    author_sa_repo = ScopusAuthorSubjectAreaRepository(
        api_key=container.settings.SCOPUS_API_KEY
    )

    return SubjectAreaService(author_sa_repo=author_sa_repo)


@router.get(
    "/scopus/{scopus_id}",
    response_model=List[PublicationResponseDTO],
    summary="Obtener publicaciones por Scopus ID",
    description="""
    Obtiene las publicaciones directamente desde una cuenta Scopus específica.
    Las publicaciones incluyen información enriquecida con SJR (cuartiles y categorías).
    """,
)
async def get_publications_by_scopus_id(
    scopus_id: str,
    service: PublicationService = Depends(get_service),
):
    """Endpoint para obtener publicaciones por Scopus ID directamente."""
    try:
        return await service.get_publications_by_scopus_id(scopus_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener publicaciones de Scopus: {str(e)}",
        )


@router.get(
    "/scopus",
    response_model=AuthorPublicationsResponseDTO,
    summary="Obtener publicaciones de múltiples Scopus IDs",
    description="""
    Obtiene las publicaciones de uno o varios Scopus IDs, elimina duplicados
    y devuelve un resultado consolidado.
    
    Ejemplo: `/publications/scopus?ids=12345678&ids=87654321`
    """,
)
async def get_publications_by_scopus_ids(
    ids: List[str] = Query(..., description="Lista de Scopus IDs"),
    service: PublicationService = Depends(get_service),
):
    """Endpoint para obtener publicaciones de múltiples Scopus IDs."""
    try:
        return await service.get_publications_by_scopus_ids(ids)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener publicaciones: {str(e)}",
        )


@router.get(
    "/scopus/{scopus_id}/stats",
    summary="Obtener estadísticas de publicaciones por Scopus ID",
    description="Obtiene estadísticas de publicaciones por año y tipo.",
)
async def get_publication_stats(
    scopus_id: str,
    service: PublicationService = Depends(get_service),
):
    """Endpoint para obtener estadísticas de un Scopus ID."""
    try:
        return await service.get_statistics_by_scopus_ids([scopus_id])
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener estadísticas: {str(e)}",
        )


@router.get(
    "/scopus/{scopus_id}/subject-areas",
    response_model=AuthorSubjectAreasResponseDTO,
    summary="Obtener áreas temáticas de un autor por Scopus ID",
    description="""
    Obtiene las áreas temáticas del perfil de un autor consultando la API
    Author Retrieval de Scopus.
    """,
)
async def get_author_subject_areas(
    scopus_id: str,
    service: SubjectAreaService = Depends(get_subject_area_service),
):
    """Endpoint para obtener áreas temáticas de un autor desde Scopus."""
    try:
        subject_areas = await service.get_subject_areas_by_scopus_id(scopus_id)
        return AuthorSubjectAreasResponseDTO(
            author_id=scopus_id,
            subject_areas=subject_areas,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener áreas temáticas: {str(e)}",
        )
