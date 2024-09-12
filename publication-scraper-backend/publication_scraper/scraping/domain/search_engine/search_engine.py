from abc import abstractmethod
from typing import List

from django.db import IntegrityError, transaction

from publication.models import Publication
from scraping.models import SearchResult
from utils import Profiler


class SearchEngine:
  
    def __init__(self):
      self.results: List[Publication] = []
      pass
    
    @abstractmethod
    def search(self) -> List[Publication]:
      pass
    
    @abstractmethod
    def _parse_search_string(self, query: str) -> str:
      pass

    @Profiler("Save Results")
    def save_results(self) -> List[Publication]:
        """ Saves the results of publications if not duplicated by paper title or id. """
        
        paper_ids             = [result.paper_id for result in self.results]
        existing_publications = Publication.objects.filter(paper_id__in=paper_ids).values_list('paper_id', flat=True)
        new_results           = [result for result in self.results if result.paper_id not in existing_publications]
        
        with transaction.atomic():
            try:
                saved_publications = Publication.objects.bulk_create(new_results)
            except IntegrityError as e:
                print(f"IntegrityError occurred: {e}")
                saved_publications = []

        return saved_publications

    @Profiler("Save Search Results")
    def save_search_results(self) -> List[Publication]:
        """ Save search results in the database. """
        SearchResult.objects.bulk_create([
            SearchResult(
                query         = result.search_string,
                search_engine = result.searched_from,
                paper_id      = result.paper_id
            ) for idx, result in enumerate(self.results)
        ])
        return self.save_results()