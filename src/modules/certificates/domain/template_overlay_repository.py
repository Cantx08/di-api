"""
Interfaz para el servicio de superposición de plantillas.
Define el contrato para aplicar plantillas institucionales sobre contenido PDF.
"""

from abc import ABC, abstractmethod


class ITemplateOverlayService(ABC):
    """
    Interfaz abstracta para el servicio de superposición de plantillas.
    
    Define el contrato que deben cumplir las implementaciones concretas
    para superponer contenido sobre plantillas PDF institucionales.
    """

    @abstractmethod
    def overlay_content_on_template(self, content_pdf_bytes: bytes) -> bytes:
        """
        Superpone contenido PDF sobre una plantilla institucional.
        
        Args:
            content_pdf_bytes: Contenido PDF generado en bytes
            
        Returns:
            bytes: PDF resultante con contenido superpuesto sobre plantilla
            
        Raises:
            Exception: Si no se puede procesar la plantilla o el contenido
        """
        pass
    
    @property
    @abstractmethod
    def template_available(self) -> bool:
        """
        Indica si la plantilla está disponible para uso.
        
        Returns:
            bool: True si la plantilla está cargada y lista para usar
        """
        pass
