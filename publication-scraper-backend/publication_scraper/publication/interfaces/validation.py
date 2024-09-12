import pandas as pd
from typing import List, Dict, Hashable, Any
from ..models import Publication, PublicationStatus
from scraping.models import SearchEngineType
import itertools

class PublicationValidator:
    def __init__(self):
      self.dblp_results = Publication.objects.filter(source=SearchEngineType.DBLP.value, status=PublicationStatus.NEW.value)
      self.sch_results = Publication.objects.filter(source=SearchEngineType.SEMANTIC_SCHOLAR.value, status=PublicationStatus.NEW.value)
      self.wos_results = Publication.objects.filter(source=SearchEngineType.WEB_OF_SCIENCE.value, status=PublicationStatus.NEW.value)

    def validate(self, all_queries: List[str]) -> List[Dict[Hashable, Any]]:
      for dblp_result in self.dblp_results:
        dblp_result.formatted_search_string = lambda x: [keyword for keyword in x.replace('"$', '').replace('" ', '').split('"') if keyword]
        dblp_result.save()
      
      for sch_result in self.sch_results:
        sch_result.formatted_search_string = lambda x: x.replace('" + "', '|').replace('"', '').split('|')
        sch_result.save()
        
      for wos_result in self.wos_results:
        wos_result.formatted_search_string = lambda x: x.replace('" "', '|').replace('"', '').strip().split('|')
        wos_result.save()

      search_results = list(itertools.chain(self.dblp_results, self.sch_results, self.wos_results))
      combination_counts = {}
      for combination in all_queries:
        for search_result in search_results:
          if all(keyword in search_result.formatted_search_string for keyword in combination):
            combination_counts[combination] = combination_counts.get(combination, 0) + 1
      
      report_df = pd.DataFrame(combination_counts.items(), columns=['Combination', 'Count'])
      report_df.sort_values(by='Count', ascending=False, inplace=True)
      report_df['Result_Group'] = report_df['Total_Search_Result_Count'].apply(self._categorize)
      report_df.reset_index(drop=True, inplace=True)
      
      result_group_counts = report_df['Result_Group'].value_counts(normalize=True) * 100
      result_group_percentages_df = result_group_counts.reset_index()
      result_group_percentages_df.columns = ['Result_Group', 'Percentage']
      print(result_group_percentages_df)
      
      report_grouped_df = report_df.groupby('Result_Group').apply(lambda x: x.sample(n=3))
      print(report_grouped_df)
    
      for search_result in search_results:
        search_result.status = PublicationStatus.VALIDATED.value
        search_result.save()
      
      ret = report_df.to_dict(orient='records')
      return ret

    def _categorize(self, count: int) -> str:
      if count > 15:
        return 'high'
      elif count > 0:
        return 'medium'
      else:
        return 'low'
        
        
    
        
        