"""
Servicio para superponer contenido generado sobre plantillas PDF.
Implementación concreta de ITemplateOverlayService usando pypdf y reportlab.
"""
from io import BytesIO
from pathlib import Path
import logging
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from ...domain.template_overlay_repository import ITemplateOverlayService

logger = logging.getLogger(__name__)


class TemplateOverlayService(ITemplateOverlayService):
    """
    Implementación del servicio de superposición de plantillas usando pypdf.
    
    Esta clase implementa ITemplateOverlayService y proporciona la funcionalidad
    concreta para superponer contenido PDF sobre plantillas institucionales.
    """
    
    def __init__(self, template_path: str = None):
        """
        Inicializar el servicio con la ruta de la plantilla.
        
        Args:
            template_path: Ruta al archivo de plantilla PDF
        """
        if template_path is None:
            # Buscar form.pdf en la carpeta raíz del backend
            backend_root = Path(__file__).parent.parent.parent.parent
            template_path = backend_root / "form.pdf"
        
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            logger.warning(f"Plantilla no encontrada en: {self.template_path}")
            self._template_available = False
        else:
            self._template_available = True
            logger.info(f"Plantilla cargada desde: {self.template_path}")
    
    @property
    def template_available(self) -> bool:
        """Indica si la plantilla está disponible para uso."""
        return self._template_available
    
    def overlay_content_on_template(self, content_pdf_bytes: bytes) -> bytes:
        """
        Superponer contenido PDF sobre la plantilla.
        
        Args:
            content_pdf_bytes: Contenido PDF generado en bytes
            
        Returns:
            bytes: PDF resultante con contenido superpuesto sobre plantilla
            
        Raises:
            Exception: Si no se puede procesar la plantilla o el contenido
        """
        if not self.template_available:
            logger.warning("Plantilla no disponible, devolviendo contenido original")
            return content_pdf_bytes
        
        try:
            # Leer el contenido generado
            content_reader = PdfReader(BytesIO(content_pdf_bytes))
            
            # Crear un nuevo PDF writer
            writer = PdfWriter()
            
            # Para cada página del contenido, superponer sobre una copia nueva de la plantilla
            for page_num, content_page in enumerate(content_reader.pages):
                # Leer la plantilla fresh para cada página para evitar referencias compartidas
                template_reader = PdfReader(str(self.template_path))
                template_page = template_reader.pages[0]
                
                # Superponer el contenido sobre la plantilla
                template_page.merge_page(content_page)
                
                # Añadir la página al writer
                writer.add_page(template_page)
            
            # Escribir el resultado a bytes
            output_buffer = BytesIO()
            writer.write(output_buffer)
            result_bytes = output_buffer.getvalue()
            output_buffer.close()
            
            logger.info(f"PDF con plantilla generado exitosamente ({len(result_bytes)} bytes)")
            return result_bytes
            
        except Exception as e:
            logger.error(f"Error al superponer contenido sobre plantilla: {str(e)}")
            # En caso de error, devolver el contenido original
            return content_pdf_bytes
    
    def create_transparent_overlay(self, text_content: str, page_size=letter) -> bytes:
        """
        Crear una superposición transparente con texto.
        
        Args:
            text_content: Contenido de texto para la superposición
            page_size: Tamaño de página
            
        Returns:
            bytes: PDF de superposición en bytes
        """
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=page_size)
        
        # Configurar transparencia
        c.setFillAlpha(0.8)
        
        # Añadir el texto (esto es un ejemplo básico)
        width, height = page_size
        c.drawString(100, height - 100, text_content)
        
        c.save()
        overlay_bytes = buffer.getvalue()
        buffer.close()
        
        return overlay_bytes