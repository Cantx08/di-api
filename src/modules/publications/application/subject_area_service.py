"""Servicio para obtener áreas temáticas de un autor desde Scopus Author Retrieval."""

import asyncio
import logging
from typing import List

from ..domain.author_subject_area_repository import IAuthorSubjectAreaRepository

logger = logging.getLogger(__name__)


class SubjectAreaService:
    """
    Servicio para obtener las áreas temáticas de un autor.
    Trabaja directamente con Scopus IDs sin necesidad de base de datos.
    
    Flujo:
    1. Recibe uno o varios scopus_id directamente.
    2. Consulta la API de Author Retrieval para cada scopus_id.
    3. Fusiona las áreas temáticas eliminando duplicados.
    """

    def __init__(
        self,
        author_sa_repo: IAuthorSubjectAreaRepository,
    ):
        self._author_sa_repo = author_sa_repo

    async def get_subject_areas_by_scopus_ids(self, scopus_ids: List[str]) -> List[str]:
        """
        Obtiene las áreas temáticas fusionadas de múltiples Scopus IDs.
        
        Args:
            scopus_ids: Lista de Scopus IDs
            
        Returns:
            Lista ordenada de áreas temáticas únicas
        """
        if not scopus_ids:
            raise ValueError("Se requiere al menos un Scopus ID.")

        logger.info(
            "Obteniendo subject areas para %d Scopus ID(s)", len(scopus_ids)
        )

        tasks = [
            self._author_sa_repo.get_subject_areas_by_scopus_id(sid)
            for sid in scopus_ids
        ]
        results = await asyncio.gather(*tasks)

        merged_areas: set[str] = set()
        for areas_list in results:
            for area in areas_list:
                merged_areas.add(area)

        sorted_areas = sorted(merged_areas)
        logger.info(
            "%d áreas temáticas únicas obtenidas de %d cuentas",
            len(sorted_areas), len(scopus_ids)
        )

        return sorted_areas

    async def get_subject_areas_by_scopus_id(self, scopus_id: str) -> List[str]:
        """
        Obtiene las áreas temáticas de una sola cuenta Scopus.
        
        Args:
            scopus_id: ID del autor en Scopus
            
        Returns:
            Lista ordenada de áreas temáticas
        """
        areas = await self._author_sa_repo.get_subject_areas_by_scopus_id(scopus_id)
        return sorted(set(areas))

