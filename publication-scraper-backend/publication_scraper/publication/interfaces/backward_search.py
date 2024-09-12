from typing import List

from ..models import Publication, PublicationReference, PublicationReferenceType
from .snowballing_search import SnowballingSearch


class BackwardSearch(SnowballingSearch):
    def __init__(
        self, 
        publications: List[Publication], 
        show_metadata: bool = False
    ):
        """ Initialize the backward search. """
        super().__init__()
        self.publications = publications
        self.show_metadata = show_metadata
        self.load_publications()
    

    def load_publications(self):
        """
        Load publications into the dataframe.
        """
        for publication in self.publications:
            

            self.results.append({
                "title":        publication.paper_title,
                "doi":          publication.metadata.doi,
                "citations":   [],
                **self._get_publication_data(publication, self.show_metadata)
            })


    def search(self):
        """
        Performs a backward search, acquiring all papers citing the given paper(s).
        """
        for i in range(len(self.results)):
          publication = self.results[i]
          paper_doi = publication["doi"]
          
          if paper_doi == '' or paper_doi is None:
            print(f"WARNING: Paper with title {publication['title']} does not have a DOI. Skipping.")
            continue
          
          sch_paper = self.sch.get_paper(paper_doi)
          if sch_paper.citations is None or sch_paper.citationCount == 0:
            print(f"Skipped Paper | No citations: {publication['title']}")
            continue
          
          references = sch_paper.citations
          for referenced_paper in references:
            if referenced_paper.externalIds is None: 
                continue

            citation = PublicationReference(
                src = self.publications[i],
                src_doi = paper_doi,
                ref_paper_title = referenced_paper.title,
                ref_doi = referenced_paper.externalIds.get("DOI"),
                ref_url = referenced_paper.url,
                type = PublicationReferenceType.CITATION
            )
              
            citation_publication = self.post_process_results(citation)
            if citation_publication is None:
                continue
            citation_publication = self._get_publication_data(citation_publication, self.show_metadata)
            self.results[i]["citations"].append(citation_publication)
            
        return self.results
