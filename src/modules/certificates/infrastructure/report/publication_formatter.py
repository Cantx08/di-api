from typing import List, Any
from reportlab.platypus import Paragraph, Spacer
from ....publications.domain.publication import Publication
from ...domain.report_repository import IPublicationFormatter, IStyleManager


class ReportLabPublicationFormatter(IPublicationFormatter):
    """Implementación de formateador de publicaciones usando ReportLab."""
    
    def __init__(self, style_manager: IStyleManager):
        self._style_manager = style_manager
    
    def format_publication_list(self, publications: List[Publication], publication_type: str) -> List[Any]:
        """Formatea una lista de publicaciones."""
        elements = []
        
        for i, pub in enumerate(publications, 1):
            pub_text = self._generate_publications_list(pub, i, publication_type)
            
            publication_style = self._style_manager.fetch_style('Publication')
            elements.append(Paragraph(pub_text, publication_style))
        
        elements.append(Spacer(1, 15))
        return elements
    
    def _generate_publications_list(self, pub: Publication, num: int, db_name: str) -> str:
        """Construye el texto formateado de una publicación."""
        # Verificar si alguna categoría contiene Q1
        has_q1 = self._contains_q1_category(pub.categories_with_quartiles)
        
        # Construir texto base de la publicación
        pub_text = f"{num}. ({pub.year}) \"{pub.title}\". {pub.source_title}."
        
        # Normalizar y determinar el tipo de documento
        source_type_raw = (pub.document_type or "").strip()
        source_type_lower = source_type_raw.lower()
        
        # Obtener etiqueta de indexación según el tipo de documento
        indexation_label = self._get_indexation_label(source_type_lower)

        # Considerar 'No indexada' como ausencia de categorías
        has_valid_categories = False
        if pub.categories_with_quartiles:
            # si categories_with_quartiles es string y contiene 'no indexada', lo tratamos como sin categorías
            if isinstance(pub.categories_with_quartiles, str) and 'no indexada' in pub.categories_with_quartiles.lower():
                has_valid_categories = False
            else:
                # lista o string válidos
                # si formato resultante no es vacío, consideramos que hay categorías
                formatted = self._format_categories(pub.categories_with_quartiles)
                has_valid_categories = bool(formatted and formatted.strip())
        else:
            has_valid_categories = False

        if has_valid_categories:
            journal_categories = self._format_categories(pub.categories_with_quartiles)
            pub_text += f" <b>{indexation_label} - {journal_categories}</b>."
        else:
            pub_text += f" <b>{indexation_label}</b>."
        
        # Agregar DOI si existe
        if pub.doi:
            pub_text += f" DOI: {pub.doi}"
        
        # Agregar indicación de filiación si no es EPN
        if pub.affiliation_name and "escuela politécnica nacional" not in pub.affiliation_name.lower():
            pub_text += " <u>(Sin Filiación)</u>"
        
        # Si tiene al menos una categoría Q1, aplicar negritas a toda la publicación
        if has_q1:
            pub_text = f"<b>{pub_text}</b>"
        
        return pub_text
    
    @staticmethod
    def _get_indexation_label(document_type: str) -> str:
        """
        Obtiene la etiqueta de indexación según el tipo de documento.
        
        Args:
            document_type: Tipo de documento en minúsculas
            
        Returns:
            str: Etiqueta de indexación apropiada
        """
        # Mapeo de tipos de documento a etiquetas de indexación
        if 'conference' in document_type or 'proceedings' in document_type:
            return "Conferencia indexada en Scopus"
        elif 'book chapter' in document_type or 'chapter' in document_type:
            return "Cap. Libro indexado en Scopus"
        elif 'book' in document_type and 'chapter' not in document_type:
            return "Libro indexado en Scopus"
        elif 'review' in document_type:
            return "Review indexado en Scopus"
        elif 'article' in document_type or document_type == '' or 'artículo' in document_type:
            return "Indexada en Scopus"
        else:
            # Para otros tipos, usar etiqueta genérica
            return "Indexada en Scopus"
    
    @staticmethod
    def _format_categories(categories: Any) -> str:
        """Formatea las categorías de una publicación."""
        if isinstance(categories, str):
            return categories
        elif isinstance(categories, list) and len(categories) > 0:
            if len(categories[0]) > 1:
                return "; ".join(categories)
            else:
                return "".join(categories)
        else:
            return str(categories)
    
    @staticmethod
    def _contains_q1_category(categories: Any) -> bool:
        """
        Verifica si alguna de las categorías de la publicación contiene Q1.
        
        Args:
            categories: Categorías de la publicación (puede ser string, lista, etc.)
            
        Returns:
            bool: True si al menos una categoría tiene Q1, False en caso contrario
        """
        if not categories:
            return False
        
        # Convertir a string para facilitar la búsqueda
        categories_str = ""
        if isinstance(categories, str):
            categories_str = categories
        elif isinstance(categories, list):
            categories_str = "; ".join(str(cat) for cat in categories)
        else:
            categories_str = str(categories)
        
        # Buscar Q1 en el texto (con variaciones comunes)
        categories_upper = categories_str.upper()
        
        # Patrones de búsqueda para Q1
        q1_patterns = [
            "(Q1)",      # Formato estándar: Category (Q1)
            " Q1 ",      # Q1 con espacios
            " Q1;",      # Q1 seguido de punto y coma
            " Q1,",      # Q1 seguido de coma
        ]
        
        for pattern in q1_patterns:
            if pattern in categories_upper:
                return True
        
        # También verificar si empieza o termina con Q1
        if categories_upper.startswith("Q1") or categories_upper.endswith("Q1"):
            return True
        
        return False
    
    def get_document_type(self, publications: List[Publication]) -> str:
        """Obtiene la distribución de tipos de documentos."""
        count_types = {}
        for pub in publications:
            source_type = pub.document_type or "Artículo"
            count_types[source_type] = count_types.get(source_type, 0) + 1
        
        distributions = []
        for source_type, count in count_types.items():
            singular, plural = self._translate_doc_type(source_type)
            if count > 1:
                distributions.append(f"{count} {plural}")
            else:
                distributions.append(f"{count} {singular}")
        
        if len(distributions) > 1:
            return " y ".join([", ".join(distributions[:-1]), distributions[-1]])
        elif distributions:
            return distributions[0]
        else:
            return "Sin especificar"

    @staticmethod
    def _translate_doc_type(source_type: str) -> tuple:
        """Traduce tipos de documento comunes al español y devuelve (singular, plural).

        Si no se reconoce, aplica una heurística simple.
        """
        if not source_type:
            return ("Artículo", "Artículos")

        key = source_type.strip().lower()

        translations = {
            'article': ("Artículo", "Artículos"),
            'artículo': ("Artículo", "Artículos"),
            'conference paper': ("Artículo de Conferencia", "Artículos de Conferencia"),
            'conference': ("Artículo de Conferencia", "Artículos de Conferencia"),
            'proceedings': ("Artículo de Conferencia", "Artículos de Conferencia"),
            'book chapter': ("Capítulo de Libro", "Capítulos de Libro"),
            'chapter': ("Capítulo de Libro", "Capítulos de Libro"),
            'book': ("Libro", "Libros"),
        }

        if key in translations:
            return translations[key]

        # Si la cadena ya está en español y termina en 's', asumimos plural/singular
        if key.endswith('s'):
            singular = source_type.rstrip('s').capitalize()
            plural = source_type.capitalize()
            return (singular, plural)

        # Heurística por defecto: añadir 's' para plural (no perfecto, pero suficiente)
        singular = source_type.capitalize()
        plural = singular + 's'
        return (singular, plural)
