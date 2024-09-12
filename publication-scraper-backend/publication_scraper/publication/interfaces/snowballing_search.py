from typing import Any, Dict, Optional

from semanticscholar import SemanticScholar

from publication.models import (
    Publication,
    PublicationMetadata,
    PublicationReference,
    PublicationStatus,
)
from scraping.interfaces.extract_metadata import PublicationMetadataExtractor
from scraping.models import SearchEngineType
from utils.logger import Logger

log = Logger(__name__)

class SnowballingSearch:
    def __init__(self):
        self.columns = [
          'referenced_paper_title',
          'referenced_doi',
          'referenced_url',
          'from_doi',
        ]
        self.results = []
        self.sch = SemanticScholar()
    

    def load_publications(self):
        """ Load publications into the dataframe. """
        raise NotImplementedError
    

    def search(self):
        """ Perform a search. """
        raise NotImplementedError
    
    
    def post_process_results(self, reference: PublicationReference) -> Optional[Publication]:
        """
        Post-process the results.

        Adds the results to the database if they do not already exist.
        Also populates the database with the metadata of the results.
        """

        log.debug(f"Processing reference: {reference}")
        paper_doi = f"DOI:{reference.ref_doi}"
        publication = Publication.objects.filter(paper_id=paper_doi)
        
        if publication.exists():
            log.info(f"Publication with DOI {paper_doi} already exists.")
            publication = publication.first()
            try: 
                metadata = publication.metadata
            except PublicationMetadata.DoesNotExist:
                metadata = None
            
            if metadata is None:
                try:
                    metadata = self._get_metadata(paper_doi)
                except IndexError:
                    log.error(f"Metadata not found for {paper_doi}")
                    return None

                publication.metadata = metadata
                publication.save()
        else:
            publication = Publication.objects.create(
                paper_id = paper_doi,
                paper_title = reference.ref_paper_title,
                search_string = reference.type.value,
                searched_from = SearchEngineType.SEMANTIC_SCHOLAR,
                formatted_search_string = reference.type.value,
                status = PublicationStatus.NEW,
            )
            metadata = self._get_metadata(paper_doi)
            publication.metadata = metadata
            metadata.save()
            publication.save()
            
        return publication
    

    def _get_metadata(self, paper_doi: str) -> PublicationMetadata:
        """ Get metadata for a given DOI. """

        log.info(f"Getting metadata for {paper_doi}")
        extractor = PublicationMetadataExtractor(paper_doi)
        return extractor.extracted_metadata[0]
        

    def _get_publication_data(self, publication: Publication, show_metadata: bool) -> Dict[str, Any]:
        """ Get publication data if show_metadata is flagged. """

        if show_metadata:
            return publication.metadata.to_dict(show_publication = True)
        return publication.to_dict()