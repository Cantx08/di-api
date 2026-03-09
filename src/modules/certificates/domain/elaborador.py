"""
Enumeración para los elaboradores de reportes.
"""
from enum import Enum


class Elaborador(Enum):
    """
    Enum para el elaborador del reporte.
    
    Define las personas predefinidas que pueden
    elaborar los certificados de publicaciones.
    """
    M_VASQUEZ = "M. Vásquez"
    C_CALDERON = "C. Calderón"
    C_RIVADENEIRA = "C. Rivadeneira"
    
    @classmethod
    def from_str(cls, value: str) -> "Elaborador":
        """
        Crea un enum a partir de un string.
        
        Args:
            value: Valor del elaborador
            
        Returns:
            Elaborador enum correspondiente o None si no coincide
            
        Raises:
            ValueError: Si el valor no es válido
        """
        for elaborador in cls:
            if elaborador.value == value:
                return elaborador
        raise ValueError(f"Valor de elaborador no válido: {value}")
    
    @classmethod
    def get_options(cls) -> list:
        """Retorna la lista de opciones disponibles."""
        return [{"value": e.value, "label": e.value} for e in cls]
