"""
Enumeración para los tipos de firmantes/autoridades en los reportes.
"""
from enum import Enum


class Authority(Enum):
    """
    Enum para el tipo de firmante del reporte.
    
    Define las autoridades institucionales que pueden
    firmar los certificados de publicaciones.
    """
    DIRECTOR_INVESTIGACION = 1
    VICERRECTOR_INVESTIGACION = 2
    
    @classmethod
    def from_int(cls, value: int) -> "Authority":
        """
        Crea un enum a partir de un entero.
        
        Args:
            value: Valor numérico del firmante (1 o 2)
            
        Returns:
            Authority enum correspondiente
            
        Raises:
            ValueError: Si el valor no es válido
        """
        for authority in cls:
            if authority.value == value:
                return authority
        raise ValueError(f"Valor de autoridad no válido: {value}")
    
    def get_title(self) -> str:
        """Retorna el título formal del firmante."""
        titles = {
            Authority.DIRECTOR_INVESTIGACION: "Director de Investigación",
            Authority.VICERRECTOR_INVESTIGACION: "Vicerrector de Investigación"
        }
        return titles.get(self, "Autoridad")
