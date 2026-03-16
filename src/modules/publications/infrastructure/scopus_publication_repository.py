""" Repositorio de publicaciones que consume la API de Scopus. """

from typing import List, Optional, Dict, Any
from httpx import Timeout, AsyncClient, HTTPStatusError, RequestError
from ..domain.publication_repository import IPublicationRepository


class ScopusPublicationRepository(IPublicationRepository):
    """
    Repositorio de publicaciones que consume la API de Scopus.
    
    Implementa la interfaz IPublicationRepository para obtener
    publicaciones científicas desde el servicio de Elsevier.
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
        # Aumentar timeout para autores con muchas publicaciones
        self._timeout = Timeout(120.0, connect=10.0)

    async def get_publications_by_scopus_id(
        self, 
        scopus_author_id: str
    ) -> List[Dict[str, Any]]:
        """
        Obtiene las publicaciones de un autor por su Scopus ID.
        
        Args:
            scopus_author_id: ID del autor en Scopus
            
        Returns:
            Lista de diccionarios con los datos crudos de las publicaciones
        """
        all_entries = []
        start = 0
        count = 25  # Máximo permitido por la API de Scopus
        
        async with AsyncClient(timeout=self._timeout) as client:
            while True:
                url = f"{self._base_url}/content/search/scopus"
                params = {
                    "query": f"AU-ID({scopus_author_id})",
                    "start": start,
                    "count": count,
                    "view": "COMPLETE"  # Obtener datos completos para cada publicación
                }
                
                response = await client.get(url, headers=self._headers, params=params)
                response.raise_for_status()
                
                data = response.json()
                search_results = data.get("search-results", {})
                entries = search_results.get("entry", [])
                
                # Verificar si hay resultados válidos
                if not entries or (len(entries) == 1 and entries[0].get("error")):
                    break
                all_entries.extend(entries)
                # Verificar si hay más páginas
                total_results = int(search_results.get("opensearch:totalResults", 0))
                if start + count >= total_results:
                    break
                start += count
        return all_entries

    async def get_publication_details(
        self, 
        scopus_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles completos de una publicación específica.
        
        Args:
            scopus_id: ID de la publicación en Scopus
            
        Returns:
            Diccionario con los detalles completos o None si no existe
        """
        try:
            url = f"{self._base_url}/content/abstract/scopus_id/{scopus_id}"
            async with AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url, headers=self._headers)
                response.raise_for_status()
                data = response.json()
                return data.get("abstracts-retrieval-response", {})               
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise
        except RequestError:
            return None
