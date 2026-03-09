from typing import List, Union
from ...publications.domain.publication import Publication
from ..domain.report_repository import IReportGenerator
from ..domain.report import (AuthorInfo, ReportConfiguration, PublicationCollections,
                             PublicationsStatistics)
from ..domain.gender import Gender
from ..domain.authority import Authority


class ReportService:
    """
    Servicio de aplicación para generar reportes de certificación.
    
    Sigue el principio de Inversión de Dependencias (DIP):
    - Depende de abstracciones (IReportGenerator), no de implementaciones concretas
    - Las implementaciones se inyectan desde el contenedor de dependencias
    """

    def __init__(self, report_generator: IReportGenerator):
        """
        Inicializa el servicio con el generador de reportes inyectado.
        
        Args:
            report_generator: Implementación de IReportGenerator inyectada desde infrastructure
        """
        self._report_generator = report_generator

    def generate_report(
            self,
            # Información del docente
            author_name: str,
            author_gender: str,
            department: str,
            role: str,

            # Configuración del reporte
            memorandum: str = "",
            signatory: Union[int, str] = 1,
            signatory_name: str = "",
            report_date: str = "",
            elaborador: str = "M. Vásquez",

            # Publicaciones
            scopus_publications: List[Publication] = None,
            wos_publications: List[Publication] = None,
            regional_publications: List[Publication] = None,
            event_memory: List[Publication] = None,
            book_chapters: List[Publication] = None,

            # Estadísticas
            subject_areas: List[str] = None,
            documents_by_year: dict = None,

            # Modo borrador
            is_draft: bool = False
    ) -> bytes:
        """
        Genera un reporte de certificación de publicaciones en formato PDF.
        
        Args:
            author_name: Nombre completo del docente
            author_gender: Género del docente ("M", "F" o texto personalizado)
            department: Departamento al que pertenece
            role: Cargo del docente
            memorandum: Número del memorando (opcional)
            signatory: Tipo de firmante (1: Directora, 2: Vicerrector, o cargo personalizado)
            signatory_name: Nombre del firmante (requerido para firmantes personalizados)
            report_date: Fecha del reporte (opcional, usa fecha actual si no se proporciona)
            elaborador: Nombre de quien elaboró el reporte
            scopus_publications: Lista de publicaciones Scopus
            wos_publications: Lista de publicaciones WOS
            regional_publications: Lista de publicaciones regionales
            event_memory: Lista de memorias de eventos
            book_chapters: Lista de libros y capítulos
            subject_areas: Lista de áreas temáticas
            documents_by_year: Diccionario con documentos por año
            
        Returns:
            bytes: Contenido del PDF generado
            
        Raises:
            ValueError: Si faltan datos requeridos
        """
        # Validar datos de entrada
        self._check_input_data(author_name, author_gender, department, role)

        # Crear value objects
        author_info = self._create_author_profile(author_name, author_gender, department, role)
        config = self._create_report_configuration(memorandum, signatory, signatory_name, report_date, elaborador)
        publications = self._create_publication_collections(
            scopus_publications, wos_publications, regional_publications,
            event_memory, book_chapters
        )
        statistics = self._generate_publication_statistics(subject_areas, documents_by_year)

        # Generar reporte (con o sin plantilla según modo borrador)
        return self._report_generator.generate_report(author_info, config, publications, statistics, is_draft=is_draft)

    @staticmethod
    def _check_input_data(name: str, gender: str, department: str, role: str) -> None:
        """Valida que los datos de entrada sean correctos."""
        if not name or not name.strip():
            raise ValueError("El nombre del docente es requerido")

        if gender not in ["M", "F"]:
            raise ValueError("El género debe ser 'M' o 'F'")

        if not department or not department.strip():
            raise ValueError("El departamento es requerido")

        if not role or not role.strip():
            raise ValueError("El cargo es requerido")

    @staticmethod
    def _create_author_profile(name: str, gender: str, department: str, role: str) -> AuthorInfo:
        """Crea el value object DocenteInfo."""
        # Si es un valor de enum conocido, usar enum; si no, usar el string personalizado
        if gender in ["M", "F"]:
            gender_value = Gender.MASCULINO if gender == "M" else Gender.FEMENINO
        else:
            gender_value = gender  # Usar el string personalizado
            
        return AuthorInfo(
            name=name.strip(),
            gender=gender_value,
            department=department.strip(),
            role=role.strip()
        )

    @staticmethod
    def _create_report_configuration(memorandum: str, signatory: Union[int, str], signatory_name: str, date: str, elaborador: str = "M. Vásquez") -> ReportConfiguration:
        """Crea el value object ReportConfiguration."""
        # Si es un número, mapear a enum; si es string, crear objeto personalizado
        if isinstance(signatory, int):
            signatory_type = Authority.DIRECTOR_INVESTIGACION if signatory == 1 else Authority.VICERRECTOR_INVESTIGACION
        else:
            # Para firmantes personalizados, crear un diccionario con cargo y nombre
            signatory_type = {
                'cargo': signatory,
                'nombre': signatory_name.strip() if signatory_name else signatory
            }

        if date and date.strip():
            return ReportConfiguration(memorandum.strip(), signatory_type, date.strip(), elaborador)
        else:
            return ReportConfiguration.generate_with_current_date(memorandum.strip(), signatory_type, elaborador)

    @staticmethod
    def _create_publication_collections(
            scopus: List[Publication] = None,
            wos: List[Publication] = None,
            regionals: List[Publication] = None,
            memories: List[Publication] = None,
            books: List[Publication] = None
    ) -> PublicationCollections:
        """Crea el value object ColeccionesPublicaciones."""
        return PublicationCollections(
            scopus=scopus or [],
            wos=wos or [],
            regional_publications=regionals or [],
            memories=memories or [],
            books=books or []
        )

    @staticmethod
    def _generate_publication_statistics(
            subject_areas: List[str] = None,
            publications_by_year: dict = None
    ) -> PublicationsStatistics:
        """Crea el value object PublicationsStatistics."""
        return PublicationsStatistics(
            subject_areas=subject_areas or [],
            publications_by_year=publications_by_year or {}
        )
