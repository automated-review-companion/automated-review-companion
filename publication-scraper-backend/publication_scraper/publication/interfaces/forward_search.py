from typing import List

from utils import Profiler
from utils.logger import Logger

from ..models import Publication, PublicationReference, PublicationReferenceType
from .snowballing_search import SnowballingSearch

log = Logger(__name__)

class ForwardSearch(SnowballingSearch):
  
  def __init__(
      self, 
      publications: List[Publication], 
      show_metadata: bool = False
  ):
    """ Initialize the forward search. """
    super().__init__()
    self.publications: List[Publication] = publications
    self.show_metadata: bool = show_metadata
    self.load_publications()
    
  def load_publications(self):
    """ Serialize publications. """

    for publication in self.publications:
      self.results.append({
        "title": publication.paper_title,
        "doi": publication.metadata.doi,
        "references": [],
        **self._get_publication_data(publication, self.show_metadata)
      })

  @Profiler("Forward Search - Searching")
  def search(self):
    """
    Performs a forward search, acquiring all references of the paper(s).
    """
    for i in range(len(self.results)):
      log.info(f"Searching for references of {self.results[i]['title']}")
      publication = self.results[i]
      paper_doi = publication["doi"]
      
      if paper_doi == "" or paper_doi is None:
        log.warn(f"WARNING: Paper with title {publication['title']} does not have a DOI. Skipping.")
        continue
      
      sch_paper = self.sch.get_paper(paper_doi)
      references = sch_paper.references
      
      if references is None:
        log.warn(f"Skipped Paper | No references: {publication['title']}")
        continue

      for referenced_paper in references:
        if referenced_paper.externalIds is None or referenced_paper.externalIds.get("DOI") is None:  
          log.warn(f"Publication with no DOI: {referenced_paper.title}")
          log.warn(f"External IDs: {referenced_paper.externalIds}")
          continue

        reference = PublicationReference(
            src = self.publications[i],
            src_doi = paper_doi,
            ref_paper_title = referenced_paper.title,
            ref_doi = referenced_paper.externalIds.get("DOI"),
            ref_url = referenced_paper.url,
            type = PublicationReferenceType.REFERENCE
        )

        log.debug(f"Reference: {referenced_paper}")
        reference_publication = self.post_process_results(reference)
        if reference_publication is None:
          continue
        reference_publication = self._get_publication_data(reference_publication, self.show_metadata)
        self.results[i]["references"].append(reference_publication)
    return self.results

  def _get_ref_doi(self, external_ids: dict) -> str:
    """ Get the DOI from the external IDs. """
    
    if (doi := external_ids.get("DOI")) is None:
      doi = external_ids.get("ArXiv")
      if doi:
        return f"arXiv:{doi}"
    return doi