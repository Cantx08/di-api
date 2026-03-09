from typing import Any
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from ...domain.report_repository import IStyleManager


class ReportLabStyleManager(IStyleManager):
    """Implementación de gestor de estilos usando ReportLab."""
    
    def __init__(self):
        self._styles = getSampleStyleSheet()
        self.customize_styles()
    
    def fetch_style(self, style_name: str) -> Any:
        """Obtiene un estilo por nombre."""
        return self._styles[style_name]
    
    def customize_styles(self) -> None:
        """Configura estilos personalizados para el documento."""
        self._stylize_title()
        self._stylize_subtitle()
        self._stylize_justified_text()
        self._stylize_publications()
        self._stylize_caption()
        self._stylize_signatory()
        self._stylize_author_table()
    
    def _stylize_title(self) -> None:
        """Crea el estilo para el título principal."""
        self._styles.add(ParagraphStyle(name='MainTitle', parent=self._styles['Title'], fontSize=20, spaceAfter=30,
                                        alignment=TA_LEFT, textColor=colors.black, fontName='Helvetica-Bold'))
    
    def _stylize_subtitle(self) -> None:
        """Crea el estilo para subtítulos."""
        self._styles.add(ParagraphStyle(name='SubTitle', parent=self._styles['Heading2'], fontSize=12,
                                        spaceAfter=10, spaceBefore=10, fontName='Helvetica-Bold'))
    
    def _stylize_justified_text(self) -> None:
        """Crea el estilo para texto justificado."""
        self._styles.add(ParagraphStyle(name='Justified', parent=self._styles['Normal'], fontSize=11,
                                        alignment=TA_JUSTIFY, spaceAfter=6, fontName='Times-Roman'))
    
    def _stylize_publications(self) -> None:
        """Crea el estilo para publicaciones."""
        self._styles.add(ParagraphStyle(name='Publication', parent=self._styles['Normal'], fontSize=11, leftIndent=20,
                                        spaceAfter=8, alignment=TA_JUSTIFY, fontName='Times-Roman'))
    
    def _stylize_caption(self) -> None:
        """Crea el estilo para captions centrados."""
        self._styles.add(ParagraphStyle(name='CaptionCenter', parent=self._styles['Normal'], alignment=TA_CENTER,
                                        fontSize=10, textColor=colors.black, fontName='Times-Roman'))
    
    def _stylize_signatory(self) -> None:
        """Crea el estilo para firmas."""
        self._styles.add(ParagraphStyle(name='Signature', parent=self._styles['Normal'], fontSize=11, alignment=TA_LEFT,
                                        fontName='Times-Roman', textColor=colors.black))
    
    def _stylize_author_table(self) -> None:
        """Crea el estilo para la tabla de elaboración."""
        self._styles.add(ParagraphStyle(name='AuthorTable', parent=self._styles['Normal'], fontSize=8,
                                        alignment=TA_LEFT, fontName='Times-Roman', textColor=colors.black))
