import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

import { Tooltip } from '@mui/material';
import {
  LLMQuestion,
  Publication,
  SearchResult
} from '../types';

export interface PublicationRowProps {
  rowType?: string
  rowIdx?: number | string
  deleteMode?: boolean
  publication: Publication
  handlePaperSelect?: (paper_id: string) => void
  selectedPapers?: string[]
  showMetadata?: boolean
  searchResults: SearchResult
  setSearchResults?: React.Dispatch<React.SetStateAction<SearchResult>>
  llmQuestions?: LLMQuestion[]
}

const PublicationRow: React.FC<PublicationRowProps> = (props) => {
  const { 
    rowType,
    rowIdx,
    deleteMode,
    publication,
    handlePaperSelect,
    selectedPapers,
    showMetadata,
    searchResults,
    llmQuestions,
    setSearchResults
  } = props;

  const getColorByRowType = () => {
    switch (rowType) {
      case 'reference':
        return 'table-info';
      case 'citation':
        return 'table-warning';
      default:
        return '';
    }
  }

  const getDiffRowColor = () => {
    if (publication.diffType === 'add') {
      return 'table-success';
    } else if (publication.diffType === 'remove') {
      return 'table-danger';
    }
    return '';
  }

  const handleReferencesVisibility = () => {
    if (!setSearchResults) return;
    const updatedResults = searchResults.results.map((result: Publication) => {
      if (result.paper_id === publication.paper_id) {
        return {
          ...result,
          showReferences: !result.showReferences
        }
      }
      return result;
    });
    setSearchResults({...searchResults, results: updatedResults})
  }

  const handleCitationsVisibility = () => {
    if (!setSearchResults) return;
    const updatedResults = searchResults.results.map((result: Publication) => {
      if (result.paper_id === publication.paper_id) {
        return {
          ...result,
          showCitations: !result.showCitations
        }
      }
      return result;
    });
    setSearchResults({...searchResults, results: updatedResults})
  }

  // Only applicable to references/citations
  const addToMainSearchResult = (paper: Publication) => {
    if (!setSearchResults) return;
    // remove from references/citations from all results' citations/references
    const updatedResults = searchResults.results.map((result: Publication) => {
      var references: Publication[] = [];
      var citations: Publication[] = [];
      if (result.references && result.references.length > 0) {
        references = result.references.filter((reference) => reference.paper_id !== paper.paper_id)
      }
      if (result.citations && result.citations.length > 0) {
          citations = result.citations.filter((citation) => citation.paper_id !== paper.paper_id)
      }
      return {
        ...result,
        references,
        citations
      }
    });

    setSearchResults({...searchResults, results: [...updatedResults, paper]})
  }

  const handlePaperDelete = (paper_id: string) => {
    if (!setSearchResults) return;
    const updatedResults = searchResults.results.filter((result: Publication) => result.paper_id !== paper_id);
    setSearchResults({...searchResults, results: updatedResults})
  }

  const parseSearchString = (searchString: string[] | string) => {
    if (Array.isArray(searchString)) {
      return `(${searchString.join(', ')})`;
    }
    return searchString
  }

  return (
    <tr key={publication.paper_id}
      className={`${getColorByRowType()} ${getDiffRowColor()} publication-row`}
      style={{ height: "20px" }}
    >
      <td>
        <div className='d-flex items-align-center flex-column gap-2 h-100 w-100'>
          {
            deleteMode &&
            <button
              className="btn btn-danger btn-sm"
              onClick={() => handlePaperDelete(publication.paper_id)}
            >-</button>
          }
          {
            rowType === 'reference' &&
            <Tooltip title="Append to the bottom of the main search results" placement="top">
              <button 
                className="btn btn-primary btn-sm"
                onClick={() => addToMainSearchResult(publication)}
              >+</button>
            </Tooltip>
          }
          {
            rowType === 'citation' && 
            <Tooltip title="Append to the bottom of the main search results" placement="top">
              <button 
                className="btn btn-primary btn-sm"
                onClick={() => addToMainSearchResult(publication)}
              >+</button>
            </Tooltip>
          }
          {
            rowType === 'main' && selectedPapers && handlePaperSelect &&
            <>
              <input
                type="checkbox"
                checked={selectedPapers.includes(publication.paper_id)}
                onClick={() => handlePaperSelect (publication.paper_id)}
              />
              {/* Expand/contract references/citations */}
              {
                publication.references && publication.references.length > 0 &&
                <Tooltip title="Expand/Collapse references" placement="top">
                  {publication.showReferences ? 
                    <ExpandMoreIcon 
                      onClick={handleReferencesVisibility}
                      style={{ 
                        cursor: "pointer",
                        color: "blue"
                      }}
                  /> :
                  <ExpandLessIcon 
                    onClick={handleReferencesVisibility}
                    style={{ 
                      cursor: "pointer",
                      color: "blue"
                    }}
                  />}
                </Tooltip>
              }
              {
                publication.citations && publication.citations.length > 0 &&
                <Tooltip title="Expand/Collapse citations" placement="top">
                  {publication.showCitations ?
                    <ExpandMoreIcon 
                      onClick={handleCitationsVisibility}
                      style={{ 
                        cursor: "pointer",
                        color: "#E6A23B"
                      }}
                    /> :
                    <ExpandLessIcon 
                      onClick={handleCitationsVisibility}
                      style={{ 
                        cursor: "pointer",
                        color: "#E6A23B"
                      }}
                    />
                  }
                </Tooltip>
              }
            </>
          }
        </div>
      </td>
      <td style={{ textAlign: "center" }}>{rowIdx}</td>
      <td>{publication.paper_id}</td>
      <td>
        <div className="publication-data-table-cell" style={{ width: "300px" }}>
          <span dangerouslySetInnerHTML={{__html: publication.paper_title }}></span>
        </div>
      </td>
      <td>{publication.searched_from}</td>
      <td>
        <code>          
          {parseSearchString(publication.search_string)}
        </code>
      </td>
      <td>
        <code>
          {publication.formatted_search_string}
        </code>
      </td>
      {/* <td>{publication.status}</td> */}
      {/* Metadata */}
      {
        showMetadata &&
          <>
            <td>
              <div style={{ maxHeight: "100px", overflow: "scroll"}}>
                {publication.abstract ?? "-"}
              </div>
            </td>
            <td>
              <div className="publication-data-table-cell" style={{ width: "200px"}}>
                {publication.authors?.map((author) => author.name).join(', ') ?? "-"}
              </div>
            </td>
            <td>{publication.citation_count ?? "-"}

            </td>
            <td>{publication.conference_journal ?? "-"}</td>
            <td>{publication.doi ?? "-"}</td>
            {/*todo: doi_url isnt working properly, changed to workaround*/}
            <td>
              {publication.doi ? (
                <a href={`https://doi.org/${publication.doi}`}
                  className='text-blue-500 underline'    
                  target="_blank"
                  rel="noopener noreferrer">
                    {publication.doi}
                </a>
              ) : (
                  'Not Available'
              )}
            </td>
            <td>{publication.keywords?.join(', ') ?? "-"}</td>
            <td>{publication.publication_date ?? "-"}</td>
            <td>{publication.publication_type ?? "-"}</td>
            <td>
              <div className="publication-data-table-cell" style={{ width: "200px"}}>
                {publication.publisher ?? "-"}
              </div>
            </td>
            <td>
              {publication.semantic_scholar_url ? (
                  <a href={publication.semantic_scholar_url}
                     className='text-blue-500 underline' 
                     target="_blank"
                     rel="noopener noreferrer">
                    View on Semantic Scholar
                  </a>
              ) : (
                  '-'
              )}
            </td>
          </>
      }

      {/* Questions */}
      {
          searchResults.results && searchResults.results.length > 0 &&
          searchResults.results[0].llm_responses && searchResults.results[0].llm_responses.length > 0 &&
        llmQuestions && llmQuestions.length > 0 && llmQuestions.map((response: LLMQuestion, index: number) => (
          <td key={response.id} style={{ minWidth: "220px" }}>Q{index + 1} {response.question}</td>
        ))
      }
    </tr>
  )

}

export default PublicationRow;