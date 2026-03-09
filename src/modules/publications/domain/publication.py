from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Publication:
    """
    Entidad de dominio que representa una publicación científica.
    
    Contiene los datos esenciales de una publicación obtenida de Scopus,
    enriquecida con datos SJR para las categorías temáticas.
    """
    # Identificadores
    scopus_id: str
    eid: str
    doi: Optional[str]
    
    # Datos básicos de la publicación
    title: str
    year: int
    publication_date: str
    source_title: str
    document_type: str
    
    # Filiación institucional del autor consultado
    affiliation_name: str
    affiliation_id: Optional[str] = None
    
    is_epn_affiliated: bool = False

    # Identificador de la revista/fuente en Scopus/SJR
    source_id: Optional[str] = None  # Sourceid de la revista (clave para mapeo SJR)
    
    # Clasificación temática (del SJR histórico)
    # Áreas temáticas generales (ej: ["Computer Science", "Engineering"])
    subject_areas: List[str] = field(default_factory=list)
    # Categorías con cuartiles tal como vienen del SJR (ej: ["Software (Q1)", "Artificial Intelligence (Q2)"])
    categories_with_quartiles: List[str] = field(default_factory=list)
    # Año del SJR utilizado (para años futuros se mapea al último disponible)
    sjr_year_used: Optional[int] = None
