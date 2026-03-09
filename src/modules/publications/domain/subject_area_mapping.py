"""
Mapeo de abreviaturas de Scopus a nombres completos de áreas temáticas.

Fuente: areas_categories.csv (CLAVE → AREA TEMATICA)
Scopus Author Retrieval API devuelve el campo @abbrev con estas claves.
"""

SUBJECT_AREA_MAP: dict[str, str] = {
    "AGRI": "Agricultural and Biological Sciences",
    "ARTS": "Arts and Humanities",
    "BIOC": "Biochemistry, Genetics and Molecular Biology",
    "BUSI": "Business, Management and Accounting",
    "CENG": "Chemical Engineering",
    "CHEM": "Chemistry",
    "COMP": "Computer Science",
    "DECI": "Decision Sciences",
    "EART": "Earth and Planetary Sciences",
    "ECON": "Economics, Econometrics and Finance",
    "ENER": "Energy",
    "ENGI": "Engineering",
    "ENVI": "Environmental Science",
    "IMMU": "Immunology and Microbiology",
    "MATE": "Materials Science",
    "MATH": "Mathematics",
    "MEDI": "Medicine",
    "NEUR": "Neuroscience",
    "NURS": "Nursing",
    "PHAR": "Pharmacology, Toxicology and Pharmaceutics",
    "PHYS": "Physics and Astronomy",
    "PSYC": "Psychology",
    "SOCI": "Social Sciences",
    "VETE": "Veterinary",
    "DENT": "Dentistry",
    "HEAL": "Health Professions",
    "MULT": "Multidisciplinary",
}


def resolve_subject_area(abbrev: str) -> str | None:
    """
    Resuelve una abreviatura de Scopus al nombre completo del área temática.

    Args:
        abbrev: Código de abreviatura (ej: "AGRI", "COMP", "ENVI")

    Returns:
        Nombre completo del área temática, o None si la clave no existe.
    """
    return SUBJECT_AREA_MAP.get(abbrev.upper().strip())
