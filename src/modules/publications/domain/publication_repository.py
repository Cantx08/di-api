from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class IPublicationRepository(ABC):
    """
    Interfaz del repositorio de publicaciones.
    
    Define el contrato para obtener publicaciones desde fuentes externas
    como la API de Scopus.
    """

    @abstractmethod
    async def get_publications_by_scopus_id(self, scopus_author_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene las publicaciones de un autor por su Scopus ID.
        
        Args:
            scopus_author_id: ID del autor en Scopus (ej: "57200000000")
            
        Returns:
            Lista de diccionarios con los datos crudos de las publicaciones
        """
        pass

    @abstractmethod
    async def get_publication_details(self, scopus_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles completos de una publicación específica.
        
        Args:
            scopus_id: ID de la publicación en Scopus
            
        Returns:
            Diccionario con los detalles completos o None si no existe
        """
        pass
