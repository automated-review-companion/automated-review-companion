import time
from typing import Any, Dict, List
from urllib.parse import urlencode

import requests

from publication.models import Publication, PublicationStatus
from scraping.domain import SearchQuery, SearchQueryParser, SearchQueryType
from scraping.models import SearchEngineType
from utils import Profiler
from utils.logger import Logger as Logger

from .search_engine import SearchEngine

log = Logger(__name__)

class DBLPEngine(SearchEngine):
    """ Search engine for DBLP. """

    def __init__(self, search_query: SearchQuery): #List[str], year_start: str, year_end: str):
        super().__init__()
        self.url                            = "https://dblp.org/search/publ/api"
        self.results: List[Publication]     = []
        if search_query:
            self.search_type: SearchQueryType   = search_query.search_type
            self.queries: List[str]             = search_query.search_strings
            self.advanced_query: str            = search_query.advanced_search
            self.year_start: str                = search_query.start_year
            self.year_end: str                  = search_query.end_year
            self.years: str                     = self._format_years(self.year_start, self.year_end)

    @Profiler("DBLP Search")
    def search(self) -> List[Publication]:
        """ Search for papers on DBLP. """

        if self.search_type == SearchQueryType.ADVANCED:
            return self._advanced_search()
        return self._simple_search()

    def _advanced_search(self) -> List[Publication]:
        """ Perform an advanced search on DBLP. """
        log.info(f"Searching for {self.advanced_query}")
        dblp_search_string = self._parse_search_string(self.advanced_query)
        dblp_search_results = self.search_dblp(dblp_search_string + self.years)
        
        if dblp_search_results is None:
            log.info(">>> DBLP total: 0")
            return []
        
        log.info(f">>> DBLP total: {len(dblp_search_results)}")
        self._process_search_results(dblp_search_results, self.advanced_query, dblp_search_string)
        self.save_search_results()
        return self.results
    
    def _simple_search(self) -> List[Publication]:
        """ Perform a simple search on DBLP. """
        for idx, search_string in enumerate(self.queries):
            log.info(f"--- Searching for {search_string} ({idx + 1}/{len(self.queries)}) ---")
            dblp_search_string  = self._parse_search_string(search_string)
            dblp_search_results = self.search_dblp(dblp_search_string + self.years)
            
            if dblp_search_results is None:
                log.info(">>> DBLP total: 0")
                continue
            
            log.info(f">>> DBLP total: {len(dblp_search_results)}")
            self._process_search_results(dblp_search_results, search_string, dblp_search_string)
        
        self.save_search_results()    
        return self.results
    
    def search_dblp(self, query: str) -> List[Dict[str, Any]]:
        """ Search for papers on DBLP. """
       
        options = {
            'q': query,
            'format': 'json',
            'h': 1000,
            'f': 0
        }

        return self._fetch_all_search_results(options)
    
    def _format_years(self, year_start: str, year_end: str) -> str:
        """ 
        Format years for DBLP search. 
        
        Example
        -------
        >>> _format_years("2019", "2021")
        "2019 | 2020 | 2021"
        """
        years = [str(year) for year in range(int(year_start), int(year_end) + 1)]
        return " " + "|".join(f"{year}" for year in years)
  
    def _process_search_results(self, search_results: List[Dict[str, Any]], search_string: str, formatted_search_string: str) -> None:
        """ Process the search resutls from DBLP. """
        
        for count, result in enumerate(search_results, start=1):
            paper_id = self._get_paper_id(result)
            new_paper = Publication(
                paper_title = result.get('info').get('title'),   
                paper_id = paper_id,
                search_string = search_string,
                searched_from = SearchEngineType.DBLP.value,
                formatted_search_string = formatted_search_string,
                status = PublicationStatus.NEW.value
            )
            log.info(f"{search_string}: Paper {count} - {new_paper.paper_title}")
            self.results.append(new_paper)
    
    def _get_paper_id(self, dblp_result: Dict[str, str]) -> str:
        """
        Get the paper ID from the DBLP search result.
        
        :param dblp_result (Dict[str, str]): The search result from DBLP.
        :rettype str: The formatted paper ID.
        """
        information = dblp_result.get('info')
        url = information.get('url')
        doi = information.get('doi')
        
        if doi: 
            return f"DOI:{doi}"
        
        return f"url:{url}"
    
    def _fetch_all_search_results(self, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """ Fetch all search results, handling pagination. """
        
        all_results = []
        
        while True:
            response    = self.fetch_search_results(options)
            hits        = response.get("result", {}).get("hits", {})
            res_count   = int(hits.get("@total", 0))
            res_papers  = hits.get("hit", [])
            
            if not res_papers:
                break
            
            all_results.extend(res_papers)
            if not(isinstance(res_count, int)) and res_count <= 1000:
                break
            
            options['f'] = len(all_results)
            
        return all_results
          
    def fetch_search_results(self, options: Dict[str, Any], max_retries: int = 3, delay: int = 30) -> Dict[str, Any]:
        """Fetch search results from the DBLP API."""
        
        for attempt in range(max_retries):
            response = requests.get(f'{self.url}?{urlencode(options)}')
            if response.status_code == 200:
                return response.json()
            
            log.error(f"Request failed with status code {response.status_code}. Attempt {attempt + 1} of {max_retries}.")
            if attempt < max_retries - 1:
                time.sleep(delay)
                
        raise log.error("Max retries exceeded. Could not establish a connection.")

    def _parse_search_string(self, query: List[str]) -> str:

        if self.search_type == SearchQueryType.ADVANCED:
            parser = SearchQueryParser(self.advanced_query)
            return parser.parse(SearchEngineType.DBLP)

        return ' '.join(f'"{keyword}"$ ' for keyword in query)
    
    def save_results(self):
        return super().save_results()