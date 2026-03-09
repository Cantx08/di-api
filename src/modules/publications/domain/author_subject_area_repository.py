from abc import ABC, abstractmethod
from typing import List


class IAuthorSubjectAreaRepository(ABC):
    """
    Interfaz del repositorio para obtener áreas temáticas de un autor
    desde la API de Author Retrieval de Scopus.
    """

    @abstractmethod
    async def get_subject_areas_by_scopus_id(self, scopus_id: str) -> List[str]:
        """
        Obtiene las áreas temáticas del perfil de un autor en Scopus.
        
        Args:
            scopus_id: ID del autor en Scopus
            
        Returns:
            Lista de nombres de áreas temáticas (ej: ["Computer Science", "Engineering"])
        """
        ...
