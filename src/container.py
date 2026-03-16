"""
Contenedor de dependencias globales para la aplicación.
"""

from functools import lru_cache
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Configuración centralizada de la aplicación."""
    PROJECT_NAME: str = "Sistema de Publicaciones Académicas (EPN)"
    VERSION: str = "3.0.0"
    API_PREFIX: str = ""

    # Scopus & External APIs
    SCOPUS_API_KEY: str = os.getenv("SCOPUS_API_KEY", "")
    SCOPUS_INST_TOKEN: str = os.getenv("SCOPUS_INST_TOKEN", "")

    # Rutas de Archivos (Data estática)
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    SJR_CSV_PATH: str = os.getenv("SJR_CSV_PATH", str(DATA_DIR / "df_sjr_24_04_2025.csv"))
    AREAS_CSV_PATH: str = os.getenv("AREAS_CSV_PATH", str(DATA_DIR / "areas_categories.csv"))


class Container:
    """
    Contenedor de dependencias Globales.
    Aquí viven las instancias que se comparten entre TODOS los módulos.
    Ya no requiere base de datos.
    """

    def __init__(self):
        self.settings = Settings()


@lru_cache()
def get_container() -> Container:
    """Proveedor del contenedor para inyección de dependencias."""
    return Container()
