import logging
import time
from typing import Any, Dict, List, Optional

import requests

from publication.models import Publication, PublicationStatus
from scraping.domain import SearchQuery, SearchQueryParser, SearchQueryType
from scraping.models import SearchEngineType
from utils import Logger, Profiler

from .search_engine import SearchEngine

log = Logger(__name__)
class SemanticScholarEngine(SearchEngine):
    """ Search engine for Semantic Scholar. """
    
    def __init__(self, search_query: SearchQuery = None): # queries: List[str], year: str):
        super().__init__()
        self.headers = {
            "Content-Type": "application/json", 
            "x-api-key": "X48LIBLqr86ouHlnMYd3z052sgEm3Nd2wMORPzu5"  #env('SEMANTIC_SCHOLAR_API_KEY')
        }
        self.sch_fields: List[str] = [
            "title",
            "externalIds",
            "paperId",
            "url",
            "authors",
        ]
        self.url: str                   = "https://api.semanticscholar.org/graph/v1/paper/search"
        self.bulkUrl: str               = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
        self.arxiv_doi: str             = "DOI:10.48550/arXiv."
        self.results: List[Publication] = []
        
        if search_query:
            self.search_type                = search_query.search_type
            self.queries                    = search_query.search_strings
            self.advanced_query: str        = search_query.advanced_search
            self.year                       = f"{search_query.start_year}-"
        
    def find_by_doi(self, doi: str) -> Optional[Publication]:
        """ Find a publication by its DOI. """
        try: 
            response = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/{doi}")
            if response.status_code == 200:
                data = response.json()
                publication = Publication(
                    paper_title = data.get("title"),
                    paper_id    = f"DOI:{doi}",
                    status      = PublicationStatus.NEW.value
                )
                publication.save()
                return publication
            else :
                log.error(f"Failed to fetch data for DOI {doi}.")
                return None
        except Exception as e:
            log.error(f"Failed to fetch data for DOI {doi}.")
            return None


    @Profiler("Semantic Scholar Search")
    def search(self) -> List[Publication]:
        """ Search for papers on Semantic Scholar. """

        if self.search_type == SearchQueryType.ADVANCED:
            return self._advanced_search()
        return self._simple_search()
    
    
    def _advanced_search(self) -> List[Publication]:
        """ Perform an advanced search on Semantic Scholar. """

        sch_search_string = self._parse_search_string()
        search_results    = self.search_semantic_scholar(
                                search_string=sch_search_string, 
                                bulk=True, 
                                year=self.year
                            )
        search_results    = search_results.get("data")
        
        if search_results is None:
            log.info(">>> Semantic Scholar total: 0")
            return []
        
        self.process_search_results(search_results, self.advanced_query, sch_search_string)
        self.save_search_results()
        return self.results
        
    def _simple_search(self) -> List[Publication]:
        for idx, search_string in enumerate(self.queries):
            sch_search_string = self._parse_search_string()
            log.info(f"--- Searching for {sch_search_string} ({idx + 1}/{len(self.queries)}) ---")
            search_results    = self.search_semantic_scholar(
                                    search_string=sch_search_string, 
                                    bulk=True, 
                                    year=self.year
                                )
            search_results    = search_results.get("data")
            
            if search_results is None:
                log.info(">>> Semantic Scholar total: 0")
                continue
            
            self.process_search_results(search_results, search_string, sch_search_string)
        
        self.save_search_results()    
        return self.results

    def search_semantic_scholar(
        self, 
        search_string: str=None, 
        bulk: bool=False, 
        year: str=None
    ) -> Dict[str, Any]:
        """
        Search for papers on Semantic Scholar.
        Data output schema:
        {
            paperId: str,
            externalIds: {
                DOI: string,
                CorpusId: string
            },
            url: str,
            title: str,
            authors: {
                authorId: string,
                name: string, 
            }[]
        }
        
        -----------------------------------------------------------------
        
        Example:
        >>> print(search_semantic_scholar("'AI' 'Ethics'", bulk=True, year="2017-"))
        {
            'paperId': 'fd00f4e4c2ebdbb091a8f0a53b041bd207501da0', 
            'externalIds': {
                'CorpusId': 197639929
            }, 
            'url': 'https://www.semanticscholar.org/paper/fd00f4e4c2ebdbb091a8f0a53b041bd207501da0', 
            'title': 'care HCI Security and forensics Education User authentication Deception detection Smart tutoring Teaching assistant Posture recognition Gesture detection', 
            'authors': [
                {'authorId': '10109253', 'name': 'Arsalan Mosenia'}, 
                {'authorId': '1398781979', 'name': 'S. Sur-Kolay'}, 
                {'authorId': '145291370', 'name': 'A. Raghunathan'}, 
                {'authorId': '144874163', 'name': 'N. Jha'}
            ]
        }
        """
        api_url       = self.url if not bulk else self.bulkUrl
        search_params = self._parse_search_params(search_string, year) 
        response      = self.fetch_search_results(api_url, params=search_params)
        return response.json()
    
    def process_search_results(
        self, 
        search_results: List[Dict[str, Any]], 
        search_string: str,
        formatted_search_string: str
    ) -> None:
        """ Process the search results from Semantic Scholar. """
        
        for count, result in enumerate(search_results, start=1):
            paper_id    = self._get_paper_id(result)
            publication   = Publication(
                                paper_title             = result.get("title"),
                                paper_id                = paper_id,
                                search_string           = search_string,
                                searched_from           = SearchEngineType.SEMANTIC_SCHOLAR.value,
                                formatted_search_string = formatted_search_string,
                                status                  = PublicationStatus.NEW.value
                            )
            log.info(f"{search_string}: Paper {count} - {publication.paper_title}")
            self.results.append(publication)
     
    def _get_paper_id(self, sch_result: Dict[str, str]) -> str:
        """
        Get the paper ID from the scholar search result.
        Checks for DOI, ArXiv, and paper ID in the given results and returns
        the appropriate formatted string.
        
        :param sch_result (Dict[str, str]): The search result from Semantic Scholar.
        :rettype str: The formatted paper ID.
        """
        external_ids = sch_result.get('externalIds', {})
        doi = external_ids.get('DOI')
        arxiv = external_ids.get('ArXiv')
        paperId = sch_result.get("paperId")
        
        if doi: 
            return f"DOI:{doi}"
        
        if arxiv: 
            return f"{self.arxiv_doi}{arxiv}"
        
        return f"paperid:{paperId}"
        
    def _parse_search_params(self, query: str, year: str) -> Dict[str, str]:
        """Parse the search parameters for the Semantic Scholar API."""
        
        if self.sch_fields == "all":
            return {
                "query": query, 
                "year": year
            }
        else:
            return {
                "query": query, 
                "year": year, 
                "fields": ",".join(self.sch_fields)
            }     
        
    def fetch_search_results(
        self, 
        url: str, 
        params: Dict[str, str], 
        max_retries: int = 3, 
        delay: int = 30
    ) -> Dict[str, Any]:
        """Fetch search results from the Semantic Scholar API."""
        
        for attempt in range(max_retries):
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response
            
            log.error(f"Request failed with status code {response.status_code}. Attempt {attempt + 1} of {max_retries}.")
            if attempt < max_retries - 1:
                time.sleep(delay)
                
        raise Exception(f"Failed to fetch data after {max_retries} retries.")

    def _parse_search_string(self, search_string: List[str] = []) -> str:
        """ 
        Parse the search string for Semantic Scholar. 

        NOTE: match search string with boolean operators, and other terms
        are only matched with the exact phrase.
        """
        if self.search_type == SearchQueryType.ADVANCED:
            parser = SearchQueryParser(self.advanced_query)
            return parser.parse(SearchEngineType.SEMANTIC_SCHOLAR)
        
        return " + ".join(f"'{term}'" for term in search_string)
    
    def save_results(self):
        return super().save_results()