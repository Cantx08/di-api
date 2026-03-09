""" Cliente para la API de Scopus. """

from typing import Dict, Any, List
from httpx import Timeout, AsyncClient

class ScopusApiClient:
    """Cliente para la API de Scopus."""

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._base_url = "https://api.elsevier.com"
        self._headers = {
            "Accept": "application/json",
            "X-ELS-APIKey": self._api_key
        }
        # Aumentar timeout para autores con muchas publicaciones
        self._timeout = Timeout(120.0, connect=10.0)

    async def get_publications_by_author(self, author_id: str) -> Dict[str, Any]:
        """Busca publicaciones de un autor en Scopus."""
        url = f"{self._base_url}/content/search/scopus"
        start = 0
        count = 200 # Nota: Si el autor tiene >200, se requeriría paginación aquí.
        params = {
            "query": f"AU-ID({author_id})",
            "start": start,
            "count": count
        }
        async with AsyncClient(timeout=self._timeout) as client:
            response = await client.get(url, headers=self._headers, params=params)
            response.raise_for_status()
            return response.json()

    async def get_publication_details(self, scopus_id: str) -> Dict[str, Any]:
        """Obtiene detalles completos de una publicación."""
        url = f"{self._base_url}/content/abstract/scopus_id/{scopus_id}"
        async with AsyncClient(timeout=self._timeout) as client:
            response = await client.get(url, headers=self._headers)
            response.raise_for_status()
            return response.json()

    async def get_author_details(self, author_id: str) -> Dict[str, Any]:
        """
        Obtiene los detalles del perfil del autor, incluyendo sus áreas temáticas.
        Utiliza la vista 'ENHANCED' para asegurar que vengan los subject-areas.
        """
        url = f"{self._base_url}/content/author/author_id/{author_id}"
        params = {
            "view": "ENHANCED"
        }
        async with AsyncClient(timeout=self._timeout) as client:
            response = await client.get(url, headers=self._headers, params=params)
            response.raise_for_status()
            return response.json()

    async def get_author_subject_areas(self, scopus_author_id: str) -> List[str]:
        """
        Obtiene las áreas temáticas de un perfil específico de Scopus.
        Retorna una lista de strings, ej: ['Computer Science', 'Engineering']
        """
        url = f"{self._base_url}/content/author/author_id/{scopus_author_id}"
        params = {
            "view": "ENHANCED" # INDISPENSABLE para ver subject-areas
        }
        
        try:
            async with AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url, headers=self._headers, params=params)
                
                if response.status_code == 404:
                    return []
                response.raise_for_status()
                
                data = response.json()
                
                # Navegación segura en el JSON de Scopus
                author_profile = data.get("author-retrieval-response", [])
                if isinstance(author_profile, list): author_profile = author_profile[0]
                
                subject_areas_raw = author_profile.get("subject-areas", {}).get("subject-area", [])
                
                # Scopus devuelve un dict si es solo una área, o una lista si son varias
                if isinstance(subject_areas_raw, dict):
                    subject_areas_raw = [subject_areas_raw]
                
                # Extraemos el nombre legible (campo "$")
                areas = [area.get("$", "").strip() for area in subject_areas_raw if area.get("$")]
                return areas
                
        except Exception as e:
            print(f"Error recuperando áreas para {scopus_author_id}: {e}")
            return []