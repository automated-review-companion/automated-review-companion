from enum import Enum
from typing import List


class SearchQueryType(str, Enum):
    SIMPLE = "SIMPLE"
    ADVANCED = "ADVANCED"


class SearchQuery:
    
    def __init__(
        self, 
        search_strings: List[str], 
        advanced_search: str        = None,
        start_year: str             = None,
        end_year: str               = None,
    ):
        self.search_strings = search_strings
        self.advanced_search = advanced_search
        self.start_year = start_year
        self.end_year = end_year

        if advanced_search:
            self.search_type = SearchQueryType.ADVANCED
        else:
            self.search_type = SearchQueryType.SIMPLE