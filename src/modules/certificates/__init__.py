"""
Módulo de certificados de publicaciones académicas.

Este módulo permite generar certificados PDF de publicaciones
académicas para los docentes de la institución.
"""
from .infrastructure.certificate_router import router

__all__ = ['router']