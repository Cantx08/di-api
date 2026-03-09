import io
from typing import List, Any
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from ...domain.report_repository import IReportGenerator, IContentBuilder
from ...domain.report import AuthorInfo, ReportConfiguration, PublicationCollections, PublicationsStatistics
from .template_overlay_service import TemplateOverlayService


class NumberedCanvas(canvas.Canvas):
    """Canvas personalizado con numeración de páginas."""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
        
    def save(self):
        num_pages = len(self._saved_page_states)
        for (page_num, page_state) in enumerate(self._saved_page_states):
            self.__dict__.update(page_state)
            self.draw_page_number(page_num + 1, num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
        
    def draw_page_number(self, page_num, total_pages):
        """Dibuja el número de página en formato X/Y."""
        self.setFont("Helvetica", 9)
        self.drawRightString(
            A4[0] - 2*cm, 
            1*cm, 
            f"{page_num}/{total_pages}"
        )


class ReportLabReportGenerator(IReportGenerator):
    """Generador de reportes PDF usando ReportLab."""
    
    def __init__(self, content_builder: IContentBuilder):
        self._content_builder = content_builder
        self._template_service = TemplateOverlayService()
    
    def generate_report(self, author: AuthorInfo, config: ReportConfiguration, publications: PublicationCollections, statistics: PublicationsStatistics, is_draft: bool = False) -> bytes:
        """Genera el reporte completo en formato PDF. Si is_draft=True, sin plantilla institucional."""
        buffer = io.BytesIO()
        doc = self._create_document(buffer)
        
        # Construir el contenido del documento
        story = self._merge_sections(author, config, publications, statistics)
        
        # Construir PDF con numeración de páginas
        doc.build(story, canvasmaker=NumberedCanvas)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        # Si es borrador, devolver sin plantilla; si no, aplicar plantilla institucional
        if not is_draft:
            pdf_bytes = self._template_service.overlay_content_on_template(pdf_bytes)
        
        return pdf_bytes
    
    @staticmethod
    def _create_document(buffer: io.BytesIO) -> SimpleDocTemplate:
        """Crea el documento PDF con configuración básica."""
        return SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=3*cm,
            bottomMargin=2.5*cm
        )
    
    def _merge_sections(self, author: AuthorInfo, config: ReportConfiguration, publications: PublicationCollections, statistics: PublicationsStatistics) -> List[Any]:
        """Construye la historia completa del documento."""
        story = []
        
        # Título principal
        story.extend(self._content_builder.generate_header(author, config))
        
        # Sección Resumen
        story.extend(self._content_builder.generate_summary(author, config, publications))
        
        # Sección Informe Técnico
        story.extend(self._content_builder.generate_technical_report(author, publications, statistics))
        
        # Sección Conclusión
        story.extend(self._content_builder.generate_conclusion(author, config, publications))
        
        # Firmas y tabla al final
        story.extend(self._content_builder.get_signature_section(config))
        
        return story
