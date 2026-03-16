"""Repositorio de áreas temáticas del autor usando la API Author Retrieval de Scopus."""

import logging
from typing import List
from httpx import Timeout, AsyncClient, HTTPStatusError

from ..domain.author_subject_area_repository import IAuthorSubjectAreaRepository
from ..domain.subject_area_mapping import resolve_subject_area

logger = logging.getLogger(__name__)


class ScopusAuthorSubjectAreaRepository(IAuthorSubjectAreaRepository):
    """
    Obtiene las áreas temáticas del perfil de un autor desde la API
    Author Retrieval de Scopus (vista ENHANCED).
    """

    def __init__(self, api_key: str, inst_token: str):
        self._api_key = api_key
        self._inst_token = inst_token
        self._base_url = "https://api.elsevier.com"
        self._headers = {
            "Accept": "application/json",
            "X-ELS-APIKey": self._api_key,
            "X-ELS-Insttoken": self._inst_token
        }
        self._timeout = Timeout(60.0, connect=10.0)

    async def get_subject_areas_by_scopus_id(self, scopus_id: str) -> List[str]:
        """
        Consulta la API Author Retrieval con view=ENHANCED para extraer
        las subject-areas del perfil del autor.

        Formato de respuesta esperado de Scopus:
        {
          "author-retrieval-response": [{
            "subject-areas": {
              "subject-area": [
                {"@abbrev": "COMP", "$": "Computer Science", ...},
                {"@abbrev": "ENGI", "$": "Engineering", ...}
              ]
            }
          }]
        }
        """
        url = f"{self._base_url}/content/author/author_id/{scopus_id}"
        params = {"view": "ENHANCED"}

        try:
            async with AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url, headers=self._headers, params=params)
                response.raise_for_status()
                data = response.json()

            # Navegar la estructura de respuesta de Scopus
            retrieval = data.get("author-retrieval-response", [])
            if isinstance(retrieval, list) and retrieval:
                retrieval = retrieval[0]
            elif isinstance(retrieval, dict):
                pass  # ya es el objeto
            else:
                logger.warning("Respuesta inesperada de Author Retrieval para %s", scopus_id)
                return []

            subject_areas_obj = retrieval.get("subject-areas", {})
            subject_area_list = subject_areas_obj.get("subject-area", [])

            if isinstance(subject_area_list, dict):
                subject_area_list = [subject_area_list]

            areas: List[str] = []
            for sa in subject_area_list:
                abbrev = sa.get("@abbrev", "").strip()
                if abbrev:
                    full_name = resolve_subject_area(abbrev)
                    if full_name:
                        areas.append(full_name)
                    else:
                        logger.warning(
                            "Abreviatura de subject area desconocida '%s' para autor %s",
                            abbrev, scopus_id
                        )

            logger.debug("Author %s subject areas: %s", scopus_id, areas)
            return areas

        except HTTPStatusError as e:
            logger.error(
                "Error HTTP al obtener subject areas del autor %s: %s",
                scopus_id, e.response.status_code
            )
            return []
        except Exception as e:
            logger.error(
                "Error inesperado al obtener subject areas del autor %s: %s",
                scopus_id, str(e)
            )
            return []
