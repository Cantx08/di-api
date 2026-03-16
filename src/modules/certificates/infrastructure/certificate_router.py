"""
Router para el módulo de certificados.
Define los endpoints para generar certificados de publicaciones académicas.
Sin dependencias de base de datos: recibe Scopus IDs y datos manuales.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import Response

from ..application.report_dto import ReportRequestDTO
from ..application.report_service import ReportService
from ..application.draft_processor_service import DraftProcessorService
from ..domain.report_repository import IReportGenerator
from ..domain.elaborador import Elaborador
from .report.pdf_generator import ReportLabReportGenerator
from .report.content_builder import ReportLabContentBuilder
from .report.style_manager import ReportLabStyleManager
from .report.chart_generator import MatplotlibChartGenerator
from .report.publication_formatter import ReportLabPublicationFormatter
from .report.template_overlay_service import TemplateOverlayService
from ...publications.infrastructure.scopus_publication_repository import ScopusPublicationRepository
from ...publications.infrastructure.sjr_file_repository import SJRFileRepository
from ...publications.infrastructure.scopus_author_subject_area_repository import ScopusAuthorSubjectAreaRepository
from ...publications.application.publication_service import PublicationService
from ...publications.application.subject_area_service import SubjectAreaService
from ...publications.domain.publication import Publication
from ....container import get_container

router = APIRouter(prefix="/certificates", tags=["Certificados"])


def get_report_service() -> ReportService:
    """
    Factory para crear el servicio de reportes con sus dependencias.
    """
    style_manager = ReportLabStyleManager()
    chart_generator = MatplotlibChartGenerator()
    publication_formatter = ReportLabPublicationFormatter(style_manager)
    content_builder = ReportLabContentBuilder(style_manager, chart_generator, publication_formatter)

    report_generator: IReportGenerator = ReportLabReportGenerator(content_builder)

    return ReportService(report_generator)


def get_draft_processor_service() -> DraftProcessorService:
    """
    Factory para crear el servicio de procesamiento de borradores.
    """
    template_service = TemplateOverlayService()
    return DraftProcessorService(template_service)


def get_publication_service() -> PublicationService:
    """
    Factory para crear el servicio de publicaciones.
    Ya no requiere base de datos.
    """
    container = get_container()

    publication_repo = ScopusPublicationRepository(
        api_key=container.settings.SCOPUS_API_KEY,
        inst_token=container.settings.SCOPUS_INST_TOKEN
    )
    sjr_repo = SJRFileRepository(csv_path=container.settings.SJR_CSV_PATH)

    return PublicationService(
        publication_repo=publication_repo,
        sjr_repo=sjr_repo,
    )


def get_subject_area_service() -> SubjectAreaService:
    """
    Factory para crear el servicio de áreas temáticas del autor.
    Ya no requiere base de datos.
    """
    container = get_container()
    author_sa_repo = ScopusAuthorSubjectAreaRepository(
        api_key=container.settings.SCOPUS_API_KEY,
        inst_token=container.settings.SCOPUS_INST_TOKEN
    )
    return SubjectAreaService(author_sa_repo=author_sa_repo)


@router.post(
    "/generate",
    response_class=Response,
    summary="Generar certificado de publicaciones",
    description="""
    Genera un certificado PDF de publicaciones académicas para un docente.
    
    Recibe directamente los Scopus IDs en `author_ids` y los datos del docente
    de forma manual (nombre, género, departamento, cargo, etc.).
    
    El certificado incluye:
    - Información del docente (nombre, departamento, cargo)
    - Lista de publicaciones Scopus con categorías y cuartiles
    - Gráfico de tendencia de publicaciones por año
    - Áreas temáticas de investigación
    - Firma digital de la autoridad correspondiente
    """
)
async def generate_certificate(
    request: ReportRequestDTO,
    report_service: ReportService = Depends(get_report_service),
    publication_service: PublicationService = Depends(get_publication_service),
    subject_area_service: SubjectAreaService = Depends(get_subject_area_service)
):
    """Endpoint para generar un certificado de publicaciones."""
    try:
        print(f"[CERT] Datos recibidos: {request.model_dump()}")
        print(f"[CERT] Nombre: {request.docente_nombre}")
        print(f"[CERT] Departamento: {request.departamento}")
        print(f"[CERT] Cargo: {request.cargo}")

        # Recolectar publicaciones de todos los Scopus IDs
        all_publications: List[Publication] = []
        all_subject_areas: set = set()

        for scopus_id in request.author_ids:
            # Obtener publicaciones directamente por Scopus ID
            pubs = await publication_service.get_publications_by_scopus_id(scopus_id)
            for pub_dto in pubs:
                pub = Publication(
                    scopus_id=pub_dto.scopus_id,
                    eid=pub_dto.eid,
                    doi=pub_dto.doi,
                    title=pub_dto.title,
                    year=pub_dto.year,
                    publication_date=pub_dto.publication_date,
                    source_title=pub_dto.source_title,
                    document_type=pub_dto.document_type,
                    affiliation_name=pub_dto.affiliation_name,
                    affiliation_id=pub_dto.affiliation_id,
                    source_id=pub_dto.source_id,
                    subject_areas=pub_dto.subject_areas,
                    categories_with_quartiles=pub_dto.categories_with_quartiles,
                    sjr_year_used=pub_dto.sjr_year_used
                )
                all_publications.append(pub)

            # Obtener subject areas desde Author Retrieval API
            try:
                scopus_areas = await subject_area_service.get_subject_areas_by_scopus_id(scopus_id)
                all_subject_areas.update(scopus_areas)
            except Exception:
                pass

        # Eliminar duplicados basados en scopus_id
        seen_ids = set()
        unique_publications = []
        for pub in all_publications:
            if pub.scopus_id not in seen_ids:
                seen_ids.add(pub.scopus_id)
                unique_publications.append(pub)

        # Ordenar por año descendente
        unique_publications.sort(key=lambda p: p.year, reverse=True)

        # Calcular estadísticas por año
        pubs_by_year = {}
        for pub in unique_publications:
            year_str = str(pub.year)
            pubs_by_year[year_str] = pubs_by_year.get(year_str, 0) + 1

        # Clasificar publicaciones por tipo/fuente
        scopus_pubs = _filter_by_type(unique_publications, "scopus")
        wos_pubs = _filter_by_type(unique_publications, "wos")
        regional_pubs = _filter_by_type(unique_publications, "regional")
        memories = _filter_by_type(unique_publications, "memoria")
        book_chapters = _filter_by_type(unique_publications, "libro")

        # Generar PDF
        pdf_bytes = report_service.generate_report(
            author_name=request.docente_nombre,
            author_gender=request.docente_genero,
            department=request.departamento,
            role=request.cargo,
            memorandum=request.memorando or "",
            signatory=request.firmante,
            signatory_name=request.firmante_nombre or "",
            report_date=request.fecha or "",
            elaborador=request.elaborador or "M. Vásquez",
            scopus_publications=scopus_pubs,
            wos_publications=wos_pubs,
            regional_publications=regional_pubs,
            event_memory=memories,
            book_chapters=book_chapters,
            subject_areas=sorted(list(all_subject_areas)),
            documents_by_year=pubs_by_year,
            is_draft=request.is_draft
        )

        # Crear nombre del archivo
        prefix = "borrador" if request.is_draft else "certificado"
        file_name = f"{prefix}_{request.docente_nombre.replace(' ', '_')}.pdf"

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={file_name}"}
        )

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Datos inválidos: {str(ve)}") from ve
    except Exception as e:
        import traceback
        print(f"[CERT ERROR] Traceback completo:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generando el certificado: {str(e)}") from e


@router.get(
    "/elaboradores",
    summary="Obtener opciones de elaboradores",
    description="Retorna la lista de elaboradores predefinidos disponibles para los certificados."
)
async def get_elaboradores():
    """Endpoint para obtener las opciones de elaboradores."""
    return Elaborador.get_options()


@router.post(
    "/process-draft",
    response_class=Response,
    summary="Procesar borrador PDF y genera certificado final",
    description="""
    Genera el certificado final a partir del borrador en PDF generado.
    
    El archivo debe ser un PDF válido con tamaño máximo de 10MB.
    """
)
async def process_draft(
    file: UploadFile = File(..., description="Archivo PDF borrador a procesar"),
    draft_service: DraftProcessorService = Depends(get_draft_processor_service)
):
    """Endpoint para procesar un borrador PDF y convertirlo en certificado final."""
    # Validar tipo de archivo
    if not file.content_type or 'pdf' not in file.content_type.lower():
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser un PDF"
        )

    # Leer contenido del archivo
    try:
        draft_pdf_bytes = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400,
                            detail=f"Error al leer el archivo: {str(e)}"
                            ) from e

    # Validar tamaño máximo (10MB)
    max_size = 10 * 1024 * 1024  # 10 MB
    if len(draft_pdf_bytes) > max_size:
        raise HTTPException(status_code=400,
                            detail="El archivo excede el tamaño máximo permitido (10MB)"
                            )

    # Procesar el borrador
    try:
        final_pdf_bytes = await draft_service.process_draft(draft_pdf_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400,
                            detail=str(e)
                            ) from e
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Error al procesar el borrador: {str(e)}"
                            ) from e

    # Retornar PDF final
    return Response(
        content=final_pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=certificado_final.pdf"
        }
    )


def _filter_by_type(publications: List[Publication], source_name: str) -> List[Publication]:
    """Filtra publicaciones por tipo/fuente."""
    filtered = []

    for pub in publications:
        source_lower = (pub.source_title or "").lower()
        document_type_lower = (pub.document_type or "").lower()
        categories_str = ""
        if pub.categories_with_quartiles:
            if isinstance(pub.categories_with_quartiles, list):
                categories_str = " ".join(pub.categories_with_quartiles).lower()
            else:
                categories_str = str(pub.categories_with_quartiles).lower()

        if source_name == "scopus":
            is_book = ("book" in document_type_lower or
                       "chapter" in document_type_lower or
                       "libro" in source_lower)
            is_wos = ("web of science" in source_lower or "wos" in source_lower)
            is_regional = any(kw in source_lower for kw in ["scielo", "redalyc", "latindex"])

            if not (is_book or is_wos or is_regional):
                filtered.append(pub)

        elif source_name == "wos":
            if ("web of science" in source_lower or
                    "wos" in source_lower or
                    "conference proceedings citation index" in categories_str):
                filtered.append(pub)

        elif source_name == "regional":
            if any(keyword in source_lower for keyword in ["scielo", "redalyc", "latindex"]):
                filtered.append(pub)

        elif source_name == "memoria":
            if "memoria_manual" in categories_str:
                filtered.append(pub)

    return filtered
