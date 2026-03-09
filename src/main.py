from typing import List, Dict

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 1. Importación del Contenedor Global (Configuración)
from .container import get_container
# 2. Importación de los Routers
from .modules.publications.infrastructure.publication_router import router as publication_router
from .modules.certificates.infrastructure.certificate_router import router as certificate_router

# Obtener configuración
container = get_container()
settings = container.settings

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API para gestión de reportes científicos EPN"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Sistema"])
async def health_check():
    """Verifica que la API esté activa."""
    return {
        "status": "active",
        "version": settings.VERSION,
        "modules_loaded": ["publications", "certificates"]
    }


# ==============================================================================
# ROUTERS
# ==============================================================================
app.include_router(publication_router)
app.include_router(certificate_router)


# ==============================================================================
# ENDPOINTS GLOBALES / UTILITARIOS
# ==============================================================================

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
