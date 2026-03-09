from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ...publications.domain.publication import Publication
from .report import AuthorInfo, ReportConfiguration, PublicationsStatistics, PublicationCollections


class IChartGenerator(ABC):
    """Interfaz para generadores de gráficos."""

    @abstractmethod
    def generate_line_chart(self, documents_by_year: Dict[str, int], author_name: str) -> bytes:
        """Genera un gráfico de tendencias por año."""
        pass


class IStyleManager(ABC):
    """Interfaz para manejo de estilos de documento."""

    @abstractmethod
    def fetch_style(self, style_name: str) -> Any:
        """Obtiene un estilo por nombre."""
        pass

    @abstractmethod
    def customize_styles(self) -> None:
        """Configura estilos personalizados."""
        pass


class IContentBuilder(ABC):
    """Interfaz para construcción de contenido del reporte."""

    @abstractmethod
    def generate_header(self, author: AuthorInfo, config: ReportConfiguration) -> List[Any]:
        """Construye el encabezado del documento."""
        pass

    @abstractmethod
    def generate_summary(self, author: AuthorInfo, config: ReportConfiguration, publications: PublicationCollections) -> \
    List[Any]:
        """Construye la sección de resumen."""
        pass

    @abstractmethod
    def generate_technical_report(self, author: AuthorInfo, publications: PublicationCollections,
                                  statistics: PublicationsStatistics) -> List[Any]:
        """Construye la sección de informe técnico."""
        pass

    @abstractmethod
    def generate_conclusion(self, author: AuthorInfo, config: ReportConfiguration,
                            publications: PublicationCollections) -> List[Any]:
        """Construye la sección de conclusión."""
        pass

    @abstractmethod
    def get_signature_section(self, config: ReportConfiguration) -> List[Any]:
        """Construye la sección de firmas."""
        pass


class IReportGenerator(ABC):
    """Interfaz principal para generación de reportes."""

    @abstractmethod
    def generate_report(self, author: AuthorInfo, config: ReportConfiguration, publications: PublicationCollections,
                        statistics: PublicationsStatistics, is_draft: bool = False) -> bytes:
        """Genera el reporte completo en formato PDF. Si is_draft=True, sin plantilla institucional."""
        pass


class IPublicationFormatter(ABC):
    """Interfaz para formateo de publicaciones."""

    @abstractmethod
    def format_publication_list(self, publications: List[Publication], publication_type: str) -> List[Any]:
        """Formatea una lista de publicaciones."""
        pass

    @abstractmethod
    def get_document_type(self, publications: List[Publication]) -> str:
        """Obtiene los tipos de documentos."""
        pass
