import time
from typing import Any, Dict, List

import requests

from publication.models import Publication, PublicationStatus
from scraping.domain import SearchQuery, SearchQueryParser, SearchQueryType
from scraping.models import SearchEngineType
from utils import Logger, Profiler

from .search_engine import SearchEngine

log = Logger(__name__)

class WebOfScienceEngine(SearchEngine):
    """ Search engine for Web of Science. """
    
    def __init__(self, search_query: SearchQuery):  # queries: List[str], start_year: int, end_year: int) -> None:
        super().__init__()
        self.url     = 'https://api.clarivate.com/api/wos'
        self.headers = {
            'X-ApiKey': "1c19a6c1114c4ee6f84142bba8040e6bbaa9825b", # env('WOS_API_KEY'),
            "Content-Type": "application/json"
        }
        
        self.wos_fields                 = []
        self.search_type                = search_query.search_type
        self.advanced_query             = search_query.advanced_search
        self.queries                    = search_query.search_strings
        self.start_year                 = int(search_query.start_year)
        self.end_year                   = int(search_query.end_year)
        self.results: List[Publication] = []
        
    @Profiler("Web of Science Search")
    def search(self) -> List[Publication]:
        """ 
        Search for papers on Web of Science. 
        Refer to https://webofscience.help.clarivate.com/en-us/Content/search-operators.html
        """
        if self.search_type == SearchQueryType.ADVANCED:
            return self._advanced_search()
        return self._simple_search()
    
    def _advanced_search(self) -> List[Publication]:
        """ Perform an advanced search on Web of Science. """
            
        wos_search_string = self._parse_search_string()
        wos_search_results = self._search(self.advanced_query)
        
        if wos_search_results is None:
            log.info(">>> Web of Science total: 0")
            return []
        
        log.info(f">>> Web of Science total: {len(wos_search_results)}")
        
        self._process_search_results(wos_search_results, self.advanced_query, wos_search_string)
        self.save_search_results()
        return self.results

    def _simple_search(self) -> List[Publication]:
        """ Perform a simple search on Web of Science. """
        for idx, search_string in enumerate(self.queries):
            log.info(f"--- Searching Web of Science for: {search_string} ({idx + 1}/{len(self.queries)}) ---")
            wos_search_string = self._parse_search_string(search_string)
            wos_search_results = self._search(search_string)
            
            if wos_search_results is None:
                log.info(">>> Web of Science total: 0")
                continue
            
            log.info(f">>> Web of Science total: {len(wos_search_results)}")
            
            self._process_search_results(wos_search_results, search_string, wos_search_string)

        self.save_search_results()
        return self.results
    
    def _process_search_results(self, search_results: List[Dict[str, Any]], search_string: str, formatted_search_string: str) -> None:
        """ Process the search results from Web of Science. """
        
        for count, record in enumerate(search_results):
            uid                 = record['UID']
            record_identifiers  = record['dynamic_data']['cluster_related']['identifiers']['identifier']
            titles              = record['static_data']['summary']['titles']['title']
            
            publication         = Publication(
                                    paper_title             = self._get_paper_title(titles),
                                    paper_id                = self._get_paper_id(uid, record_identifiers),
                                    search_string           = search_string,
                                    searched_from           = SearchEngineType.WEB_OF_SCIENCE.value,
                                    formatted_search_string = formatted_search_string,
                                    status                  = PublicationStatus.NEW.value,
                                )
            log.info(f"{search_string}: Paper {count} - {publication.paper_title}")
            self.results.append(publication)
    
    def _search(self, search_string):
        """ Search for papers on Web of Science. """
        
        loop_count      = 0
        start_record    = 1
        total_records   = None
        paper_count     = 0
        search_results: List[Dict[str, Any]] = []
        
        while True:
            search_params   = self._parse_search_params(search_string, start_record)
            data            = self.fetch_search_results(search_params)
            
            query_result    = data.get("QueryResult", {})
            records_found   = query_result.get("RecordsFound", 0)
            
            query_data      = data.get("Data", {})
            query_records   = query_data.get("Records", {})
            records         = query_records.get("records", {})
            records         = records.get("REC", [])
            
            if records_found == 0 or data is None:
                total_records = 0
                break

            if total_records is None:
                total_records = records_found
                
            search_results.extend(records)
            paper_count += len(records)
            start_record += len(records)
            loop_count += 1

            if paper_count >= total_records:
                break
            
            log.info(f"[{loop_count}] {search_params}: {paper_count}/{total_records} found.")

        return search_results

    def _get_paper_id(self, uid, record_identifiers: Dict[str, str]) -> str:
        """ Get the paper ID from the record identifiers. """
        
        for identifier in record_identifiers:
            if isinstance(identifier, dict) and identifier['type'] == 'doi':
                return f"DOI:{identifier['value']}"
        return uid
    
    def _get_paper_title(self, titles: List[Dict[str, str]]) -> str:
        """ Get the paper title from the record titles. """
        
        return next((t['content'] for t in titles if t['type'] == 'item'), 'No title found')
    
    def _parse_search_params(self, search_string: str, start_record: int) -> Dict[str, Any]:
        """ Parse the search parameters for the Web of Science API. """

        if self.search_type == SearchQueryType.ADVANCED:
            parser = SearchQueryParser(self.advanced_query)
            search_string = parser.parse(SearchEngineType.WEB_OF_SCIENCE)
            title_search = f"TS=({search_string})"
        else:
            title_search = f"TS=({search_string})"

        return {
            'usrQuery': f'({title_search}) AND PY=({self.start_year}-{self.end_year})',
            'count': 100,
            'firstRecord': start_record,
            'databaseId': 'WOS',
            'links': "false",
        }
        
    def fetch_search_results(
        self, 
        params: Dict[str, Any],
        max_retries: int = 3,
        delay: int = 5
    ) -> Dict[str, Any]:
        """ Fetch search results from the Web of Science API. """
        
        for attempt in range(max_retries):
            response = requests.get(self.url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json()
            
            if response.status_code == 429:
                log.error(f"Rate limit exceeded. Waiting for {delay} seconds.")
                time.sleep(delay)
                continue
            
            log.error(f"Request failed with status code {response.status_code}: {response.json()}. Attempt {attempt + 1} of {max_retries}.")
            if attempt < max_retries - 1:
                time.sleep(delay)
        
        raise Exception(f"Failed to fetch data after {max_retries} retries.")
    
    def _parse_search_string(self, search_string: List[str] = []):
        """ Parse the search string for Web of Science. """

        if self.search_type == SearchQueryType.ADVANCED:
            parser = SearchQueryParser(self.advanced_query)
            return parser.parse(SearchEngineType.WEB_OF_SCIENCE)
        
        return " ".join(f'"{term}"' for term in search_string)
    
    def save_results(self):
        return super().save_results()