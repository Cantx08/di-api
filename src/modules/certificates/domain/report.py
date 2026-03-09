from dataclasses import dataclass
from typing import List, Dict, Union
from datetime import datetime

from ...publications.domain.publication import Publication
from .gender import Gender
from .authority import Authority


@dataclass(frozen=True)
class AuthorInfo:
    """Value Object para la información básica del docente."""
    name: str
    gender: Union[Gender, str]  # Permite tanto enum como string personalizado
    department: str
    role: str
    
    def get_article(self) -> str:
        """Retorna el artículo apropiado según el género."""
        if isinstance(self.gender, Gender):
            return "El" if self.gender == Gender.MASCULINO else "La"
        # Para géneros personalizados, usar artículo neutro
        gender_str = str(self.gender).upper()
        if gender_str in ['M', 'MASCULINO', 'HOMBRE']:
            return "El"
        elif gender_str in ['F', 'FEMENINO', 'MUJER']:
            return "La"
        else:
            return "El/La"  # Artículo neutro para casos personalizados
    
    def get_author_coauthor(self) -> str:
        """Retorna la forma apropiada de autor/coautor según el género."""
        if isinstance(self.gender, Gender):
            return "autor/co-autor" if self.gender == Gender.MASCULINO else "autora/co-autora"
        # Para géneros personalizados
        gender_str = str(self.gender).upper()
        if gender_str in ['M', 'MASCULINO', 'HOMBRE']:
            return "autor/co-autor"
        elif gender_str in ['F', 'FEMENINO', 'MUJER']:
            return "autora/co-autora"
        else:
            return "autor/co-autor"  # Forma por defecto para casos personalizados


@dataclass(frozen=True)
class ReportConfiguration:
    """Value Object para la configuración del reporte."""
    memorandum: str
    signatory: Union[Authority, str, Dict[str, str]]  # Enum, string o dict con cargo/nombre
    report_date: str
    elaborador: str = "M. Vásquez"  # Nombre de quien elaboró el reporte
    
    @classmethod
    def generate_with_current_date(cls, memorandum: str = "", signatory: Union[Authority, str, Dict[str, str]] = Authority.DIRECTOR_INVESTIGACION, elaborador: str = "M. Vásquez"):
        """Factory method para crear configuración con fecha actual."""
        report_date = datetime.now().strftime("%d de %B de %Y")
        return cls(memorandum, signatory, report_date, elaborador)


@dataclass(frozen=True)
class PublicationsStatistics:
    """Value Object para las estadísticas de publicaciones."""
    subject_areas: List[str]
    publications_by_year: Dict[str, int]
    
    def has_sufficient_data_for_graph(self) -> bool:
        """Verifica si hay suficientes datos para mostrar un gráfico."""
        return len(self.publications_by_year) > 1


@dataclass(frozen=True)
class PublicationCollections:
    """Value Object que agrupa todas las colecciones de publicaciones."""
    scopus: List[Publication]
    wos: List[Publication]
    regional_publications: List[Publication]
    memories: List[Publication]
    books: List[Publication]
    
    def get_total_publications(self) -> int:
        """Calcula el total de publicaciones."""
        return (len(self.scopus) + len(self.wos) + len(self.regional_publications) + 
                len(self.memories) + len(self.books))
    
    def exists_scopus_publications(self) -> bool:
        """Verifica si hay publicaciones Scopus."""
        return len(self.scopus) > 0
