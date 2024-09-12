import logging
from datetime import datetime
from typing import Any, Dict, List, Union

import requests

# from serpapi import GoogleSearch
from crossref.restful import Works
from publication.models import Publication, PublicationMetadata
from utils import Profiler
from utils.logger import Logger as Logger

log = Logger(__name__)
class PublicationMetadataExtractor:
    
    def __init__(self, paper_ids: Union[str, List[str]]):
        # For reference as PublicationMetadata fields -- Can be deleted afterwards
        log.info("Initializing PublicationMetadataExtractor")

        self.metadata_fields = [
            "PaperTitle",
            "DOI",
            "Authors",
            "Abstract",
            "Publisher",
            "SemanticScholarUrl",
            "DoiUrl",
            "PublicationDate",
            "FieldOfStudy",
            "Conference-Journal",
            "PublicationTypes",
            "SearchString",
            "CitationCount",
            "SearchedFrom",
        ]
        self.sch_fields = [
            "title",
            "externalIds",
            "authors",
            "abstract",
            "url",
            "publicationDate",
            "fieldsOfStudy",
            "venue",
            "publicationTypes",
            "citationCount",
            "externalIds",
        ]
        self.crossref_fields = [
            "indexed",
            "publisher-location",
            "reference-count",
            "publisher",
            "isbn-type",
        ]
        self.crossref_works = Works()
        self.headers        = { "Content-Type": "application/json" }
        self.base_url       = "https://api.semanticscholar.org/graph/v1/paper"
        
        if isinstance(paper_ids, str):
            paper_ids = [paper_ids]

        self.papers = self.get_papers(paper_ids)
        self.extracted_metadata: List[PublicationMetadata] = []
        self.failed_papers: List[Publication] = []
        self.initialize_process()
        
    def get_papers(self, paper_ids: List[str]) -> List[Publication]:
        """ Get the papers based on the given paper IDs. """
        return list(Publication.objects.filter(paper_id__in=paper_ids))
    
    @Profiler("Extracting Metadata")
    def initialize_process(self, cache: bool = True):
        """ atomically extract metadata for all papers. """
        for index, paper in enumerate(self.papers):
            log.info(f"Extracting metadata for paper {index + 1}/{len(self.papers)} - {paper.paper_title}")
            
            if cache:
                extracted_metadata = PublicationMetadata.objects.filter(publication=paper)
                if extracted_metadata.exists():
                    log.warn(f"Metadata already extracted for {paper.paper_title} in cache.")
                    self.extracted_metadata.append(extracted_metadata.first())
                    continue
            else:
                extracted_metadata = PublicationMetadata.objects.filter(publication=paper)
                if extracted_metadata.exists():
                    extracted_metadata.delete()

            try:
                extracted_metadata = self._extract_data(paper)
                processed_metadata = self.post_processing(extracted_metadata)
                processed_metadata.save()
                self.extracted_metadata.append(processed_metadata)
            except Exception as e:
                log.error(f"Error extracting metadata for {paper.paper_title}. - {e}")
                self.failed_papers.append((index, paper))
        
        if len(self.failed_papers) > 0:
            log.error(f"Failed to extract metadata for {len(self.failed_papers)} papers:")
            for index, paper in self.failed_papers:
                log.error(f"{index} - {paper.paper_title}")

    def _extract_data(self, paper: Publication) -> PublicationMetadata:
        """
        Extract metadata from a single paper.
        """
        pid       = self._get_paper_id(paper.paper_id)
        api_url   = f"{self.base_url}/{pid}"
        sch_paper = self._extract_sch(api_url, self.sch_fields)
        
        # If there is an error, try searching for the paper by its title
        if sch_paper.get("error"):
            
            log.warn(f"Error extracting metadata for {paper.paper_title}. Searching by title.")
            api_url = f"{self.base_url}/search?query={paper.paper_title}"
            sch_paper = self._extract_sch(api_url, self.sch_fields)
            doi = self._get_doi(paper=sch_paper, paper_id=paper.paper_id)
            crossref_paper = self._get_crossref_paper(doi)
            
            if len(sch_paper.get("data", [])) == 0:
                return PublicationMetadata(
                    publication   = paper,
                    paper_title   = paper.paper_title,
                    doi           = pid,
                    search_string = paper.search_string,
                    searched_from = paper.searched_from
                )
            
            sch_paper = sch_paper["data"][0]
        
        # Extract other metadata fields
        doi             = self._get_doi(paper=sch_paper, paper_id=paper.paper_id)
        crossref_paper  = self._get_crossref_paper(doi)
        authors         = self._extract_authors(sch_paper, crossref_paper)
        abstract        = self._extract_abstract(sch_paper, crossref_paper)
        publisher       = self._extract_publisher(crossref_paper, doi)
        paper_type      = self._extract_paper_type(crossref_paper, sch_paper)
        fields_of_study = self._get_fields_of_study(sch_paper)
        doi_url         = f"https://doi.org/{doi}" if doi else None
        pub_date        = self._get_publication_date(sch_paper, crossref_paper)

        # TODO: paper keywords missing
        # TODO: paper type is conference/journal for arxiv papers
        # TODO: conference-journal name mismatch with publisher, i.e., for paper with name"ChatGPT in education: A discourse analysis of worries and concerns on social media", the conference name is "International Conference on Artificial Intelligence in Education", but the publisher is "Arxiv" (becauseit queryed from arxiv), need "Springer" instead.
        
        metadata = PublicationMetadata(
            publication           = paper,
            paper_title           = paper.paper_title,
            doi                   = doi,
            authors               = authors,
            abstract              = abstract,
            publisher             = publisher,
            semantic_scholar_url  = sch_paper.get("url"),
            doi_url               = doi_url,
            publication_date      = pub_date,
            field_of_study        = fields_of_study,
            conference_journal    = sch_paper.get("venue"),
            publication_type      = paper_type,
            search_string         = paper.search_string,
            citation_count        = sch_paper.get("citationCount"),
            searched_from         = paper.searched_from
        )
        return metadata
    
    def post_processing(self, paper: PublicationMetadata) -> PublicationMetadata:
        """
        Post-process extracted metadata.
        Apply cast_affliation to authors field.
        """
        # TODO: Fix this
        crossref_authors = {}
        FIRST_NAME_IDX = 0
        LAST_NAME_IDX  = -1
        
        paper.authors          = self._cast_affliation(paper.authors)
        paper.doi_url          = self._get_doi_url(paper.doi)
        paper.publication_type = self._get_publication_type(paper.publication_type)
        crossref_paper         = self._get_crossref_paper(paper.doi) 
        
        if not paper.authors:
            return paper
        
        # TODO: turn authors into a FK object with (author_name, family, and affiliation)
    
        if crossref_paper:
            crossref_paper_authors = crossref_paper.get("author", [])
            for author in crossref_paper_authors:
                
                if author["affiliation"] == []:
                    continue
                
                first_name  = author.get("given", "")
                last_name   = author.get("family", "")
                author_name = f"{first_name} {last_name}"
                
                if author.get("affiliation"):
                    crossref_authors[author_name] = [affil.get("name") for affil in author.get("affiliation")]

        for author in paper.authors:
            if author["affiliation"] == ["No Affiliation"]:
                author_name             = author["name"]
                author_name_components  = author_name.split(" ")
                author_name             = author_name_components[FIRST_NAME_IDX] + " " + author_name_components[LAST_NAME_IDX]
                
                if author_name in crossref_authors:
                    author["affiliation"] = crossref_authors[author_name]
                # else:
                #     author["affiliation"] = self._get_affiliations_google_scholar(author_name)
        return paper
    
    # Helpers
    def _extract_sch(self, api_url: str, sch_fields: List[str]) -> Dict[str, Any]:
        """ Extract metadata from Semantic Scholar. """
        
        params = { "fields": ",".join(sch_fields) }
        try:
            response = requests.get(api_url, headers=self.headers, params=params)
            result = response.json()
            return result
        except Exception as e:
            log.error(e)
            return {"error": e}

    def _get_paper_id(self, paper_id: str) -> str:
        """ Get the paper ID from the record identifiers. """
        
        if "URL" in paper_id and "abs-" in paper_id:
            return "arXiv:" + paper_id.split("abs-")[1].replace("-", ".")
        
        return paper_id
  
    def _get_doi(self, paper: Dict[str, Any], paper_id: str) -> str:
        """ Get the DOI from the paper. """
        
        external_ids = paper.get("externalIds", {})
        doi = external_ids.get("DOI", None)
        
        if doi is None and str(paper_id).startswith("DOI"):
            doi = paper_id.split(":")[1]

        # TODO handle arXiv papers
        
        return doi
    
    def _get_affiliations_google_scholar(self, author_name) -> list[str]:
        
        params = {
            "engine": "google_scholar_profiles",
            "mauthors": author_name.strip(),
            "api_key": os.environ.get("GOOGLE_SCHOLAR_API_KEY"),
        }

        try:
            search          = GoogleSearch(params)
            results         = search.get_dict()
            metadata        = results.get("metadata", {})
            metadata_status = metadata.get("status")
            profiles        = results.get("profiles", [])
            
            if metadata_status == "Error" or len(profiles) == 0:
                return ["No Affiliation"]
            return [results["profiles"][0]["affiliations"]]
        
        except Exception as e:
            print(e)
            return ["No Affiliation"]

    def _get_crossref_paper(self, doi: str):
        """ Get the paper from Crossref. """
        
        try:
            crossref_paper = self.crossref_works.doi(doi)
            if not crossref_paper:
                log.error(f"Paper with DOI {doi} not found")
        except Exception as e:
            log.error(f"Paper with DOI {doi} not found", e)
            crossref_paper = None
        
        return crossref_paper
  
    def _extract_authors(self, sch_paper, crossref_paper):
        """Extract authors from the paper."""
        
        authors = None
        if crossref_paper is not None:
            authors = crossref_paper.get("author")
            
        if authors:
            for i in range(len(authors)):
                author        = authors[i]
                author_name   = f'{author.get("given", "")} {author.get("family", "")}'
                affiliations  = author.get("affiliation", [])
                school_names  = (
                    [affil.get("name") for affil in affiliations]
                    if affiliations != []
                    else ["No Affiliation"]
                )
                
                # Create a new dictionary with only 'name' and 'affiliation'
                authors[i] = {
                    "name": author_name.strip(),
                    "affiliation": school_names,
                }
            return authors
            
        authors = sch_paper.get("authors")
        if not(authors):
            return []

        for i in range(len(authors)):
            author        = authors[i]
            affiliations  = author.get("affiliations")
            
            if not(affiliations):
                author_name = author["name"]
                affiliations = ["No Affiliation"]

            authors[i] = {
                "name": author_name.strip(),
                "affiliation": affiliations,
            }

        return authors
    
    def _extract_abstract(self, sch_paper: Dict[str, Any], crossref_paper: Union[None, Dict[str, Any]]):
        """ Extract the abstract from the paper. """
        
        if abstract := sch_paper.get("abstract"):
            return abstract
        
        if crossref_paper and (abstract := crossref_paper.get("abstract")):
            return abstract
            

        # TODO: Can try scraping via sch_paper["url"]

        log.warn("No abstract available.")
        return "No abstract available."
    

    def _extract_publisher(self, crossref_paper: Union[None, Dict[str, Any]], doi: str):
        """ Extract the publisher from the paper. """

        if crossref_paper:
            return crossref_paper.get("publisher")
            
        if doi and "arxiv" in doi.lower():
            return "arXiv"
            
        return "n/a"
  
    def _extract_paper_type(self, crossref_paper: Union[None, Dict[str, Any]], sch_paper: Dict[str, Any]) -> List[str]:
        """ Extract the paper type from the paper. """
        
        if crossref_paper and crossref_paper.get("type"):
            return [crossref_paper.get("type")]
        
        paper_type = sch_paper.get("publicationTypes", [])
        if not(paper_type): 
            return []
        
        paper_type = ["".join(t.split("-")).lower() for t in paper_type]
        return paper_type
  
    def _cast_affliation(self, authors):
        """ Cast the 'affiliation' field to a list. """
        
        if not(authors): 
            return authors
        
        for i in range(len(authors)):
            author = dict(authors[i])
            if type(author["affiliation"]) is str:
                author["affiliation"] = [author["affiliation"]]
            authors[i] = author
        
        return authors
  
    def _get_doi_url(self, doi_url: str) -> str:
        """ Get the DOI URL. """
        
        if doi_url and isinstance(doi_url, str):
            return doi_url
        return None
  
    def _get_publication_type(self, publication_type: Union[str, List[str]]) -> List[str]:
        """ Get the publication type. """
        
        if publication_type and isinstance(publication_type, str):
            return [ "".join(t.split("-")).lower() for t in publication_type ]  
        return publication_type
    
    def _get_fields_of_study(self, sch_paper: Dict[str, Any]) -> List[str]:
        """ Get the fields of study. """
        
        fields_of_study = sch_paper.get("fieldsOfStudy", [])
        if not(fields_of_study):
            return ""
        return fields_of_study  
    
    def _get_publication_date(self, sch_paper: Dict[str, Any], crossref_paper: Union[None, Dict[str, Any]]) -> str:
        """ Get the publication date. """
        
        if sch_paper and (pub_date := sch_paper.get("publicationDate")):
            return pub_date
        
        if crossref_paper and (pub_date := crossref_paper.get("created")):
            pub_date = pub_date.get("date-time").split("T")[0]
            return pub_date

        # TODO: Can try scraping via sch_paper["url"]
        return datetime.now().strftime("%Y-%m-%d")