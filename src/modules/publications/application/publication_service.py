""" Servicio de aplicación para gestión de publicaciones. """

import asyncio
from typing import List, Dict, Optional
import logging
from .publication_dto import PublicationResponseDTO, AuthorPublicationsResponseDTO
from ..domain.publication import Publication
from ..domain.publication_repository import IPublicationRepository
from ..domain.sjr_repository import ISJRRepository

logger = logging.getLogger(__name__)


class PublicationService:
    """
    Servicio de aplicación para gestión de publicaciones.
    Trabaja directamente con Scopus IDs sin necesidad de base de datos.
    """
    
    EPN_AFFILIATION_ID = "60072054"
    
    def __init__(
        self,
        publication_repo: IPublicationRepository,
        sjr_repo: ISJRRepository,
    ):
        self._publication_repo = publication_repo
        self._sjr_repo = sjr_repo

    async def get_publications_by_scopus_ids(
        self,
        scopus_ids: List[str],
    ) -> AuthorPublicationsResponseDTO:
        """
        Obtiene publicaciones de múltiples Scopus IDs, elimina duplicados y ordena.
        """
        logger.info(f"Obteniendo publicaciones de {len(scopus_ids)} Scopus ID(s)")

        tasks = [self._fetch_from_scopus(sid) for sid in scopus_ids]
        result_lists = await asyncio.gather(*tasks)

        all_publications: List[Publication] = []
        seen_ids = set()

        for publications in result_lists:
            for pub in publications:
                if pub.scopus_id not in seen_ids:
                    seen_ids.add(pub.scopus_id)
                    all_publications.append(pub)

        all_publications.sort(key=lambda p: p.year, reverse=True)

        logger.info(f"Total de {len(all_publications)} publicaciones únicas obtenidas")

        return AuthorPublicationsResponseDTO(
            author_id=",".join(scopus_ids),
            scopus_ids=scopus_ids,
            total_publications=len(all_publications),
            publications=[PublicationResponseDTO.from_entity(p) for p in all_publications],
        )

    async def _fetch_from_scopus(self, scopus_id: str) -> List[Publication]:
        """Obtiene publicaciones desde la API de Scopus y las enriquece con SJR."""
        raw_publications = await self._publication_repo.get_publications_by_scopus_id(scopus_id)
        
        publications = []
        for raw_pub in raw_publications:
            pub = self._transform_raw_publication(raw_pub, scopus_id)
            pub = self._enrich_with_sjr(pub)
            publications.append(pub)
        
        return publications

    async def get_publications_by_scopus_id(
        self, 
        scopus_id: str
    ) -> List[PublicationResponseDTO]:
        """Obtiene publicaciones de un solo Scopus ID."""
        publications = await self._fetch_from_scopus(scopus_id)
        publications.sort(key=lambda p: p.year, reverse=True)
        return [PublicationResponseDTO.from_entity(p) for p in publications]

    def _transform_raw_publication(self, raw: Dict, scopus_author_id: str) -> Publication:
        """
        Transforma y aplica la lógica de validación de filiación estricta.
        """
        cover_date = raw.get("prism:coverDate", "")
        year = int(cover_date[:4]) if cover_date and len(cover_date) >= 4 else 0
        
        # Validar si este autor, pertenecía a la EPN durante esta publicación
        affiliation_name, affiliation_id, is_epn = self._analyze_affiliation_link(
            raw, scopus_author_id
        )
        
        # Extracción del Sourceid de la revista/fuente
        raw_source_id = raw.get("source-id")
        source_id = str(raw_source_id).strip() if raw_source_id else None

        return Publication(
            scopus_id=raw.get("dc:identifier", "").replace("SCOPUS_ID:", ""),
            eid=raw.get("eid", ""),
            doi=raw.get("prism:doi"),
            source_id=source_id,
            title=raw.get("dc:title", "Sin título"),
            year=year,
            publication_date=cover_date,
            source_title=raw.get("prism:publicationName", ""),
            document_type=raw.get("subtypeDescription", raw.get("prism:aggregationType", "")),
            
            # Nuevos datos calculados
            affiliation_name=affiliation_name,
            affiliation_id=affiliation_id,
            is_epn_affiliated=is_epn,
            
            subject_areas=[],
            categories_with_quartiles=[],
            sjr_year_used=None
        )
    
    def _analyze_affiliation_link(self, raw: Dict, target_author_id: str) -> tuple[str, Optional[str], bool]:
        """
        Analiza si el author_id específico está vinculado al AF-ID de la EPN en este documento.
        Retorna: (Nombre Filiación, ID Filiación, Es_EPN_Boolean)
        """
        # 1. Obtener lista de autores del paper
        authors = raw.get("author", [])
        if isinstance(authors, dict): authors = [authors]
        
        # 2. Obtener lista de afiliaciones globales del paper (para buscar nombres)
        affiliations_metadata = raw.get("affiliation", [])
        if isinstance(affiliations_metadata, dict): affiliations_metadata = [affiliations_metadata]
        
        # Diccionario auxiliar para buscar nombres de afiliaciones por ID rápido
        aff_lookup = {
            aff.get("afid"): aff.get("affilname", "Desconocida") 
            for aff in affiliations_metadata if aff.get("afid")
        }

        # 3. Buscar al autor objetivo
        target_author = next((a for a in authors if a.get("authid") == target_author_id), None)

        if not target_author:
            # Caso raro: El paper salió en la búsqueda pero el autor no aparece en la lista explícita
            # Esto pasa en "Group Authors" a veces. Asumimos False por seguridad.
            return "Autor no listado explícitamente", None, False

        # 4. Obtener los IDs de filiación DE ESTE AUTOR en este paper
        # Scopus devuelve 'afid' como un array de objetos (view=COMPLETE) o string
        author_afids = []
        raw_afids = target_author.get("afid", [])
        
        if isinstance(raw_afids, list):
            # Formato: [{'@_fa': 'true', '$': '12345'}, ...] o ['12345']
            for item in raw_afids:
                if isinstance(item, dict):
                    author_afids.append(item.get("$", ""))
                else:
                    author_afids.append(str(item))
        elif isinstance(raw_afids, dict):
             author_afids.append(raw_afids.get("$", ""))
        elif isinstance(raw_afids, str):
            # A veces viene separado por espacios si no es array
            author_afids = raw_afids.split()

        # 5. VERIFICACIÓN MAESTRA: ¿Está el ID de la EPN en los IDs de este autor?
        is_epn = self.EPN_AFFILIATION_ID in author_afids

        # 6. Resolver nombre de afiliación para mostrar
        if is_epn:
            # Si es EPN, forzamos que se muestre como tal y devolvemos el ID de EPN
            return aff_lookup.get(self.EPN_AFFILIATION_ID, "Escuela Politécnica Nacional"), self.EPN_AFFILIATION_ID, True
        
        # Si no es EPN, devolvemos su primera afiliación (la principal externa)
        if author_afids:
            primary_afid = author_afids[0]
            return aff_lookup.get(primary_afid, "Filiación Externa"), primary_afid, False
            
        return "Sin filiación", None, False

    def _get_author_affiliation(self, raw: Dict, scopus_author_id: str) -> tuple[str, Optional[str]]:
        authors = raw.get("author", [])
        if isinstance(authors, dict):
            authors = [authors]
        
        for author in authors:
            authid = author.get("authid", "")
            if authid == scopus_author_id:
                afid = author.get("afid")
                if afid:
                    affiliations = raw.get("affiliation", [])
                    if isinstance(affiliations, dict):
                        affiliations = [affiliations]
                    
                    for aff in affiliations:
                        if aff.get("afid") == afid:
                            return aff.get("affilname", "Sin filiación"), afid
                    return "Afiliación ID: " + afid, afid
        
        affiliations = raw.get("affiliation", [])
        if isinstance(affiliations, dict):
            affiliations = [affiliations]
        
        if affiliations:
            first_aff = affiliations[0]
            return first_aff.get("affilname", "Sin filiación"), first_aff.get("afid")
        
        return "Sin filiación", None

    def _enrich_with_sjr(self, publication: Publication) -> Publication:
        """
        Enriquece usando Sourceid como búsqueda primaria, con fallback por nombre de revista.
        """
        areas, categories_with_quartiles, sjr_year_used = self._sjr_repo.get_journal_data(
            publication.source_id, 
            publication.year,
            publication.source_title
        )
        
        publication.subject_areas = areas
        publication.categories_with_quartiles = categories_with_quartiles
        publication.sjr_year_used = sjr_year_used
        
        return publication

    async def get_statistics_by_scopus_ids(self, scopus_ids: List[str]) -> Dict:
        """Obtiene estadísticas de publicaciones para uno o varios Scopus IDs."""
        author_pubs = await self.get_publications_by_scopus_ids(scopus_ids)
        
        by_year: Dict[int, int] = {}
        by_type: Dict[str, int] = {}
        
        for pub in author_pubs.publications:
            by_year[pub.year] = by_year.get(pub.year, 0) + 1
            by_type[pub.document_type] = by_type.get(pub.document_type, 0) + 1
        
        return {
            "scopus_ids": scopus_ids,
            "total_publications": author_pubs.total_publications,
            "by_year": dict(sorted(by_year.items(), reverse=True)),
            "by_type": by_type
        }
