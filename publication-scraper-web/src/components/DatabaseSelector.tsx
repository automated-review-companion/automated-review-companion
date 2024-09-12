import { cn } from "@/lib/utils";
import { SearchEngineType, SearchForm } from "@/types";
import { ToggleGroup, ToggleGroupItem } from "./ui/toggle-group";

export interface DatabaseSelectorProps {
  searchForm: SearchForm;
  setSearchForm: (searchForm: SearchForm) => void;
}

const DatabaseSelector: React.FC<DatabaseSelectorProps> = (props) => {
  const { searchForm, setSearchForm } = props;

  const parseSearchEngineName = (source: SearchEngineType) => {
    switch (source) {
      case SearchEngineType.DBLP:
        return 'DBLP';
      case SearchEngineType.SEMANTIC_SCHOLAR:
        return 'Semantic Scholar';
      case SearchEngineType.WEB_OF_SCIENCE:
        return 'Web of Science';
      case SearchEngineType.IEEE_XPLORE:
        return 'IEEE Xplore';
      case SearchEngineType.SCOPUS:
        return 'Scopus';
      default:
        return '';
    }
  }
  
  return ( 
      <ToggleGroup type="multiple" className="flex flex-wrap justify-content-start">
      {
        Object.values(SearchEngineType).map((source) => (
            <ToggleGroupItem 
              key={source} 
              value={source} 
              className={cn(searchForm.sources.find((s) => s === source) === source ? "bg-primary" : " bg-white ")}
              onClick={() => setSearchForm({
                ...searchForm,
                sources: searchForm.sources.find((s) => s === source)
                    ? searchForm.sources.filter((s) => s !== source)
                    : [...searchForm.sources, source]
              })}>{parseSearchEngineName(source)}
            </ToggleGroupItem>
        ))
      }
    </ToggleGroup>
   );
}
 
export default DatabaseSelector;