"""Enum de género para las certificaciones."""

from enum import Enum


class Gender(str, Enum):
    """Enum para el género del docente."""
    MASCULINO = "M"
    FEMENINO = "F"
