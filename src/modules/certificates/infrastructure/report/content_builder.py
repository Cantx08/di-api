import io
from typing import List, Any
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import cm
from reportlab.lib import colors
from ...domain.report_repository import IContentBuilder, IStyleManager, IChartGenerator, IPublicationFormatter
from ...domain.report import AuthorInfo, ReportConfiguration, PublicationsStatistics, PublicationCollections
from ...domain.authority import Authority

DIRECCION_DI = "Dr. Jaime Paúl Sayago Heredia"
VICERRECTORADO_IIV = "Dra. Sandra Patricia Sánchez Gordón"

class ReportLabContentBuilder(IContentBuilder):
    """Constructor de contenido usando ReportLab."""
    
    def __init__(self, style_manager: IStyleManager, chart_generator: IChartGenerator, publication_formatter: IPublicationFormatter):
        self._style_manager = style_manager
        self._chart_generator = chart_generator
        self._publication_formatter = publication_formatter
    
    def generate_header(self, author: AuthorInfo, config: ReportConfiguration) -> List[Any]:
        """Construye el encabezado del documento."""
        header = []
        
        # Título principal con fecha en la misma línea: texto a la izquierda y
        # fecha a la derecha. Usamos una tabla de 2 columnas para posicionarlos.
        title_style = self._style_manager.fetch_style('MainTitle')
        left = Paragraph("Certificación de Publicaciones", title_style)
        # fecha en tamaño más pequeño pero en la misma línea, alineada a la derecha
        date_para = Paragraph(f"<font size=10>{config.report_date}</font>", title_style)

        # ColWidths elegidos para aproximar el ancho de página (ajustable si se desea).
        title_table = Table([[left, date_para]], colWidths=[13*cm, 6*cm], hAlign='LEFT')
        title_table.setStyle(TableStyle([
            # Alinear al fondo de las celdas (mismo ras horizontal / baseline)
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        header.append(title_table)
        header.append(Spacer(1, 20))
        
        # Información del docente
        author_info = f"<b>{author.name}</b><br/><br/>{author.department}<br/><br/>Escuela Politécnica Nacional"
        normal_style = self._style_manager.fetch_style('Normal')
        header.append(Paragraph(f"<font size=12>{author_info}</font>", normal_style))
        header.append(Spacer(1, 20))
        
        return header

    def generate_summary(self, author: AuthorInfo, config: ReportConfiguration, publications: PublicationCollections) -> List[Any]:
        """Construye la sección de resumen."""
        summary_section = []
        
        # Subtítulo "RESUMEN"
        subtitle_style = self._style_manager.fetch_style('SubTitle')
        summary_section.append(Paragraph("<b>RESUMEN</b>", subtitle_style))
        
        # Texto del resumen
        gender_text = "del profesor" if author.gender.value == "M" else "de la profesora"
        total_publications = publications.get_total_publications()
        publication_text = "las publicaciones" if total_publications > 1 else "la publicación"
        
        if config.memorandum:
            summary = f"El presente informe se realiza en base a la solicitud del memorando {config.memorandum}, con la finalidad de certificar {publication_text} {gender_text} {author.name}."
        else:
            summary = f"El presente informe se realiza con la finalidad de certificar {publication_text} {gender_text} {author.name}."

        justified_style = self._style_manager.fetch_style('Justified')
        summary_section.append(Paragraph(summary, justified_style))
        summary_section.append(Spacer(1, 15))

        return summary_section

    def generate_technical_report(self, author: AuthorInfo, publications: PublicationCollections, statistics: PublicationsStatistics) -> List[Any]:
        """Construye la sección de informe técnico."""
        technical_report = []
        
        # Subtítulo "INFORME TÉCNICO"
        #subtitle_style = self._style_manager.fetch_style('SubTitle')
        #technical_report.append(Paragraph("<b>RESUMEN</b>", subtitle_style))
        
        # Introducción
        #technical_report.extend(self._generate_report_introduction(publications))
        
        # Subsecciones
        if publications.scopus:
            technical_report.extend(self._generate_scopus_section(author, publications, statistics))
        
        if publications.wos:
            technical_report.extend(self._generate_wos_section(author, publications))

        if publications.regional_publications:
            technical_report.extend(self._generate_regional_section(author, publications))

        if publications.memories:
            technical_report.extend(self._generate_memories_section(author, publications))

        if publications.books:
            technical_report.extend(self._generate_books_section(author, publications))

        return technical_report

    def _generate_report_introduction(self, publications: PublicationCollections) -> List[Any]:
        """Construye la introducción del informe técnico."""
        text = "La presente certificación se realiza en base a la información recopilada por la Dirección de Investigación"

        if publications.scopus:
            text += ", de la base de datos científicos Scopus"
            if publications.wos or publications.regional_publications or publications.memories or publications.books:
                text += " y bases de datos indexadas"
        elif publications.wos or publications.regional_publications or publications.memories or publications.books:
            text += ", de bases de datos indexadas"
        
        text += "."
        
        justified_style = self._style_manager.fetch_style('Justified')
        return [Paragraph(text, justified_style), Spacer(1, 20)]
    
    def _generate_scopus_section(self, author: AuthorInfo, publications: PublicationCollections, statistics: PublicationsStatistics) -> List[Any]:
        """Construye la sección de publicaciones Scopus."""
        scopus_section = []
        
        subtitle_style = self._style_manager.fetch_style('SubTitle')
        justified_style = self._style_manager.fetch_style('Justified')
        
        scopus_section.append(Paragraph("Publicaciones Scopus", subtitle_style))
        
        # Información del docente y estadísticas
        num_scopus = len(publications.scopus)
        distribution = self._publication_formatter.get_document_type(publications.scopus)
        
        texto_intro = f"{author.get_article()} {author.name}, es {author.role} de la Escuela Politécnica Nacional y miembro del {author.department}."
        scopus_section.append(Paragraph(texto_intro, justified_style))
        scopus_section.append(Spacer(1, 10))
        
        if num_scopus > 1:
            texto_stats = f"Ha participado en un total de {num_scopus} publicaciones Scopus como {author.get_author_coauthor()} de las mismas, distribuidas en {distribution}. Tal como se detalla a continuación:"
        else:
            texto_stats = f"Ha participado en un total de {num_scopus} publicación Scopus como {author.get_author_coauthor()} de la misma, siendo {distribution}. Tal como se detalla a continuación:"
        
        scopus_section.append(Paragraph(texto_stats, justified_style))
        scopus_section.append(Spacer(1, 15))
        
        # Lista de publicaciones
        scopus_section.extend(self._publication_formatter.format_publication_list(publications.scopus, "Scopus"))
        
        filiation_note = "Sin Filiación: Publicación sin filiación de la Escuela Politécnica Nacional."
        scopus_section.append(Paragraph(filiation_note, justified_style))
        scopus_section.append(Spacer(1, 15))

        # Gráfico solo para Scopus si hay datos suficientes
        if len(publications.scopus) > 1 and statistics.has_sufficient_data_for_graph():
            scopus_section.extend(self._draw_chart(statistics, author.name))
        
        # Áreas temáticas solo dentro de Scopus
        if statistics.subject_areas:
            scopus_section.append(Paragraph(
                f"<b>Áreas Temáticas de publicaciones Scopus del {author.name}</b>",
                subtitle_style
            ))
            scopus_section.extend(self._list_subject_areas(author, statistics))
        
        return scopus_section
    
    def _draw_chart(self, statistics: PublicationsStatistics, author_name: str) -> List[Any]:
        """Construye el gráfico de tendencias."""
        elements = []
        justify_style = self._style_manager.fetch_style('Justified')
        
        # Texto introductorio
        elements.append(Paragraph(
            f"Adicionalmente, en la Figura 1 se muestra la tendencia por año de las publicaciones en Scopus del {author_name}:",
            justify_style
        ))
        elements.append(Spacer(1, 15))
        
        # Generar gráfico
        chart_bytes = self._chart_generator.generate_line_chart(
            statistics.publications_by_year, author_name)
        
        # Crear imagen
        img_buffer = io.BytesIO(chart_bytes)
        img = Image(img_buffer, width=15*cm, height=7.5*cm)
        elements.append(img)
        elements.append(Spacer(1, 10))
        
        # Caption centrado
        caption_style = self._style_manager.fetch_style('CaptionCenter')
        elements.append(Paragraph(
            "<b>Figura 1.</b> Publicaciones Scopus por Año - Fuente web de Scopus.",
            caption_style
        ))
        elements.append(Spacer(1, 20))
        
        return elements

    def _list_subject_areas(self, author: AuthorInfo, statistics: PublicationsStatistics) -> List[Any]:
        """Construye la sección de áreas temáticas."""
        areas_subsection = []
        justified_style = self._style_manager.fetch_style('Justified')
        publication_style = self._style_manager.fetch_style('Publication')
        
        num_areas = len(statistics.subject_areas)
        
        if num_areas > 1:
            text = f"{author.get_article()} {author.name}, ha publicado en {num_areas} áreas temáticas, las cuales se detallan a continuación:"
        else:
            text = f"{author.get_article()} {author.name}, ha publicado en {num_areas} área temática, la cual se detalla a continuación:"
        
        areas_subsection.append(Paragraph(text, justified_style))
        areas_subsection.append(Spacer(1, 10))
        
        # Lista de áreas temáticas
        for i, area in enumerate(statistics.subject_areas, 1):
            areas_subsection.append(Paragraph(f"{i}. {area}", publication_style))
        
        areas_subsection.append(Spacer(1, 15))
        return areas_subsection

    def _generate_wos_section(self, author: AuthorInfo, publications: PublicationCollections) -> List[Any]:
        """Construye la sección de publicaciones Web of Science."""
        wos_section = []
        subtitle_style = self._style_manager.fetch_style('SubTitle')
        justified_style = self._style_manager.fetch_style('Justified')
        
        wos_section.append(Paragraph("Publicaciones Web of Science", subtitle_style))
        
        num_wos = len(publications.wos)
        distribution = self._publication_formatter.get_document_type(publications.wos)
        
        if num_wos > 1:
            text = f"Ha participado en un total de {num_wos} publicaciones indexadas en la Web of Science Core Collection como {author.get_author_coauthor()} de las mismas, distribuidas en {distribution}. Tal como se detalla a continuación:"
        else:
            text = f"Ha participado en un total de {num_wos} publicación indexada en la Web of Science Core Collection como {author.get_author_coauthor()} de la misma, siendo {distribution}. Tal como se detalla a continuación:"
        
        wos_section.append(Paragraph(text, justified_style))
        wos_section.append(Spacer(1, 15))
        
        # Lista de publicaciones
        wos_section.extend(self._publication_formatter.format_publication_list(publications.wos, "Web of Science"))
        
        return wos_section
    
    def _generate_regional_section(self, author: AuthorInfo, publications: PublicationCollections) -> List[Any]:
        """Construye la sección de otras indexaciones."""
        regional_section = []
        subtitle_style = self._style_manager.fetch_style('SubTitle')
        justified_style = self._style_manager.fetch_style('Justified')
        
        regional_section.append(Paragraph("Otras Indexaciones", subtitle_style))

        num_regionals = len(publications.regional_publications)

        if num_regionals > 1:
            text = f"{author.get_article()} {author.name}, cuenta con {num_regionals} indexaciones, como se detallan a continuación:"
        else:
            text = f"{author.get_article()} {author.name}, cuenta con {num_regionals} artículo indexado, como se detalla a continuación:"

        regional_section.append(Paragraph(text, justified_style))
        regional_section.append(Spacer(1, 15))

        regional_section.extend(self._publication_formatter.format_publication_list(publications.regional_publications, "Regional"))

        return regional_section

    def _generate_memories_section(self, author: AuthorInfo, publications: PublicationCollections) -> List[Any]:
        """Construye la sección de memorias de eventos científicos."""
        memories_section = []
        subtitle_style = self._style_manager.fetch_style('SubTitle')
        justified_style = self._style_manager.fetch_style('Justified')
        
        memories_section.append(Paragraph("Memorias de Eventos Científicos", subtitle_style))
        
        num_memories = len(publications.memories)
        
        if num_memories > 1:
            text = f"{author.get_article()} {author.name}, cuenta con {num_memories} publicaciones en memorias de eventos científicos, como se detallan a continuación:"
        else:
            text = f"{author.get_article()} {author.name}, cuenta con {num_memories} publicación en memorias de eventos científicos, como se detalla a continuación:"
        
        memories_section.append(Paragraph(text, justified_style))
        memories_section.append(Spacer(1, 15))

        memories_section.extend(self._publication_formatter.format_publication_list(publications.memories, "Memorias"))
        
        return memories_section
    
    def _generate_books_section(self, author: AuthorInfo, publications: PublicationCollections) -> List[Any]:
        """Construye la sección de libros y capítulos de libros."""
        books_section = []
        subtitle_style = self._style_manager.fetch_style('SubTitle')
        justified_style = self._style_manager.fetch_style('Justified')
        
        books_section.append(Paragraph("Libros y Capítulos de Libros", subtitle_style))
        
        num_books = len(publications.books)
        
        if num_books > 1:
            text = f"{author.get_article()} {author.name}, cuenta con {num_books} publicaciones en Libros y Capítulos de Libros, como se detallan a continuación:"
        else:
            text = f"{author.get_article()} {author.name}, cuenta con {num_books} publicación en Libros y Capítulos de Libros, como se detalla a continuación:"
        
        books_section.append(Paragraph(text, justified_style))
        books_section.append(Spacer(1, 15))

        books_section.extend(self._publication_formatter.format_publication_list(publications.books, "Libros"))
        
        return books_section
    
    def generate_conclusion(self, author: AuthorInfo, config: ReportConfiguration, publications: PublicationCollections) -> List[Any]:
        """Construye la sección de conclusión."""
        conclusion = []
        subtitle_style = self._style_manager.fetch_style('SubTitle')
        justified_style = self._style_manager.fetch_style('Justified')
        
        conclusion.append(Paragraph("Conclusión", subtitle_style))
        
        author_text_line = "el" if author.gender.value == "M" else "la"
        publication_count = publications.get_total_publications()
        
        if isinstance(config.signatory, Authority):
            if config.signatory == Authority.DIRECTOR_INVESTIGACION:
                signatory_entity = "la Dirección de Investigación"
            else:
                signatory_entity = "el Vicerrectorado de Investigación, Innovación y Vinculación"
        else:
            # Para firmantes personalizados (dict o string), usar texto genérico
            signatory_entity = "la autoridad competente"
        
        text = f"Por los antecedentes expuestos, {signatory_entity} de la Institución, certifica que {author_text_line} {author.name}, cuenta con un total de {publication_count} "
        
        if publication_count > 1:
            text += "publicaciones."
        else:
            text += "publicación."
        
        conclusion.append(Paragraph(text, justified_style))
        conclusion.append(Spacer(1, 20))
        
        conclusion_paragraph = f"{author_text_line.capitalize()} {author.name} puede hacer uso del presente certificado para lo que considere necesario."
        conclusion.append(Paragraph(conclusion_paragraph, justified_style))
        
        return conclusion
    
    def get_signature_section(self, config: ReportConfiguration) -> List[Any]:
        """Construye la sección de firmas en la parte inferior de la última página."""
        from reportlab.platypus import KeepTogether
        
        elements = []
        
        # Crear un espaciador que empuje las firmas hacia el final de la página
        # Esto empujará las firmas hacia la parte inferior de la página
        elements.append(Spacer(1, 80))  # Espaciado que empuja hacia abajo
        
        # Crear los elementos de firma como un grupo que se mantiene junto
        signature_elements = []
        
        # Información del firmante
        if isinstance(config.signatory, Authority):
            if config.signatory == Authority.DIRECTOR_INVESTIGACION:
                authority = DIRECCION_DI
                signatory_role = "DIRECTOR DE INVESTIGACIÓN DE LA ESCUELA POLITÉCNICA NACIONAL"
            else:
                authority = VICERRECTORADO_IIV
                signatory_role = "VICERRECTORA DE INVESTIGACIÓN, INNOVACIÓN Y VINCULACIÓN DE LA ESCUELA POLITÉCNICA NACIONAL"
        elif isinstance(config.signatory, dict):
            # Firmante personalizado con nombre y cargo separados
            authority = config.signatory.get('nombre', config.signatory.get('cargo', 'AUTORIDAD DESIGNADA'))
            signatory_role = config.signatory.get('cargo', 'AUTORIDAD DESIGNADA DE LA ESCUELA POLITÉCNICA NACIONAL').upper()
        else:
            # Firmante personalizado (string simple)
            authority = str(config.signatory)
            signatory_role = "AUTORIDAD DESIGNADA DE LA ESCUELA POLITÉCNICA NACIONAL"
        
        signature_style = self._style_manager.fetch_style('Signature')
        signature_elements.append(Paragraph(f"<b>{authority}</b>", signature_style))
        signature_elements.append(Paragraph(f"<b>{signatory_role}</b>", signature_style))
        signature_elements.append(Spacer(1, 10))
        
        # Tabla de elaboración - usar el elaborador configurado
        table_style = self._style_manager.fetch_style('AuthorTable')
        table_details = [
            [Paragraph("Elaborado por:", table_style), Paragraph(config.elaborador, table_style)]
        ]

        author_table = Table(table_details, colWidths=[2*cm, 2*cm], hAlign='LEFT')
        author_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Reducir paddings para acercar las líneas al contenido
            ('LEFTPADDING', (0, 0), (-1, -1), 1),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0.5),
            ('TOPPADDING', (0, 0), (-1, -1), 0.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5),
        ]))
        
        signature_elements.append(author_table)
        
        # Mantener los elementos de firma juntos y añadirlos
        elements.append(KeepTogether(signature_elements))
        
        return elements
