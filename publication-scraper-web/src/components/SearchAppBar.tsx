import { SearchMode } from "../types";

export interface SearchAppBarProps {
  searchMode: SearchMode,
  handleSelectSearchMode: (mode: SearchMode) => void   
}

const SearchAppBar: React.FC<SearchAppBarProps> = (props) => {
  const { searchMode, handleSelectSearchMode } = props;
  return ( 
      <nav className="d-flex mt-3">
        <input
            type="radio"
            className="btn-check search-nav-item"
            name="options"
            id="option1"
            autoComplete='off'
            checked={searchMode === SearchMode.SIMPLE}
            onClick={() => handleSelectSearchMode(SearchMode.SIMPLE)}
        />
        <label className="search-nav-item" htmlFor="option1">Multi-layer Keyword Search</label>

        <input
            type="radio"
            className="btn-check"
            id="advanced-search"
            autoComplete='off'
            checked={searchMode === SearchMode.ADVANCED}
            onClick={() => handleSelectSearchMode(SearchMode.ADVANCED)}
        />
        <label className="search-nav-item" htmlFor="advanced-search">Advanced Keyword Search</label>
      </nav>
   );
}
 
export default SearchAppBar;