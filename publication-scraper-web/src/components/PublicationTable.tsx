import { LLMQuestion, SearchResult } from "@/types";
import { useRef, useState } from "react";
import PublicationRow from "./PublicationRow";

export interface PublicationTableProps {
  searchResults: SearchResult;
  setSearchResults?: React.Dispatch<React.SetStateAction<SearchResult>>;
  selectedPapers?: string[];
  handlePaperSelect?: (paperId: string) => void;
  showMetadata?: boolean;
  llmQuestions?: LLMQuestion[];
  deleteMode?: boolean;
}

const PublicationTable: React.FC<PublicationTableProps> = (props) => {
  
  const {
    searchResults,
    setSearchResults,
    selectedPapers,
    handlePaperSelect,
    showMetadata,
    llmQuestions,
    deleteMode
  } = props;

  // Publication Data Table Resizability
  const [columns, setColumns] = useState([
    {
      name: "Paper ID",
      width: 200,
      requirement: true
    },
    {
      name: "Title",
      width: 200,
      requirement: true
    },
    {
      name: "Source",
      width: 100,
      requirement: true
    },
    {
      name: "Search String",
      width: 250,
      requirement: true
    },
    {
      name: "Formatted Search String",
      width: 250,
      requirement: true
    },
    {
      name: "Abstract",
      style: {
        whiteSpace: "nowrap",
        overflow: "hidden",
        textOverflow: "ellipsis",
      },
      width: 350,
      requirement: "showMetadata"
    },
    {
      name: "Authors",
      width: 220,
      requirement: "showMetadata"
    },
    {
      name: "Citations Count",
      width: 150,
      requirement: "showMetadata"
    },
    {
      name: "Conference/Journal",
      width: 200,
      requirement: "showMetadata"
    },
    {
      name: "DOI",
      width: 100,
      requirement: "showMetadata"
    },
    {
      name: "DOI URL",
      width: 100,
      requirement: "showMetadata"
    },
    {
      name: "Keywords",
      width: 100,
      requirement: "showMetadata"
    },
    {
      name: "Publication Date",
      width: 150,
      requirement: "showMetadata"
    },
    {
      name: "Publication Type",
      width: 150,
      requirement: "showMetadata"
    },
    {
      name: "Publisher",
      width: 100,
      requirement: "showMetadata"
    },
    {
      name: "Semantic Scholar URL",
      width: 200,
      requirement: "showMetadata"
    }
  ]);


  const tableRef = useRef<HTMLTableElement>(null);
  const startResizing = (index: number, startX: number) => {
    const doDrag = (e: MouseEvent) => {
      const dx = e.clientX - startX;
      if (tableRef.current) {
        const newWidths = [...columns];
        newWidths[index].width += dx;
        setColumns(newWidths);
      }
      startX = e.clientX;
    }

    const stopDrag = () => {
      document.removeEventListener("mousemove", doDrag);
      document.removeEventListener("mouseup", stopDrag);
    }

    document.addEventListener("mousemove", doDrag);
    document.addEventListener("mouseup", stopDrag);
  }

  const checkColumnRequirement = (requirement: boolean | string) => {
    if (requirement === true) {
      return true;
    } else if (requirement === "showMetadata") {
      return showMetadata;
    }
    return false
  }

  return ( 
    <>
     <div className="table-container">
        <table className="table table-striped border-1 border-slate-600 bg-white min-h-[85vh]" ref={tableRef}>
          <thead className='bg-primary text-white sticky-top' style={{ height: "20px" }}>
            <td style={{ minWidth: "10px" }}></td>
            <td style={{ minWidth: "70px" }}>#</td>
            {
              columns.map((column, index) => {
                if (checkColumnRequirement(column.requirement)) {
                  return (
                    <td 
                      key={index} 
                      className="resizable leading-[14px]" 
                      style={{  minWidth: column.width + "px", ...column.style}}
                    >
                      {column.name}
                      <div className="resizer" onMouseDown={(e) => startResizing(index, e.clientX)} style={{ cursor: "col-resize" }}></div>
                    </td>
                  )}
              })
            }

            {/* Questions */}
            {
                searchResults.results && searchResults.results.length > 0 &&
                searchResults.results[0].llm_responses && searchResults.results[0].llm_responses.length > 0 &&
                llmQuestions && llmQuestions.length > 0 && llmQuestions.map((response: LLMQuestion, index) => (
                    <td key={response.id} style={{minWidth: "220px"}}>Q{index + 1} {response.question}</td>
                ))
            }
          </thead>
          <tbody>
          {searchResults?.results && searchResults.results.length > 0 && searchResults.results.map((result, rowIdx) => {

            let publicationRows = [];

            publicationRows.push(
              <PublicationRow
                rowType='main'
                rowIdx={rowIdx+1}
                deleteMode={deleteMode}
                publication={result}
                handlePaperSelect={handlePaperSelect}
                selectedPapers={selectedPapers}
                showMetadata={showMetadata}
                searchResults={searchResults}
                llmQuestions={llmQuestions}
                setSearchResults={setSearchResults}
              />
            )

            if (result.showReferences && result.references !== undefined && result.references?.length > 0) {
              result.references.forEach((reference, referenceIdx) => {
                publicationRows.push(
                  <PublicationRow
                    rowType="reference"
                    rowIdx={rowIdx+1 + "-R" + referenceIdx}
                    deleteMode={deleteMode}
                    publication={reference}
                    handlePaperSelect={handlePaperSelect}
                    selectedPapers={selectedPapers}
                    showMetadata={showMetadata}
                    searchResults={searchResults}
                    llmQuestions={llmQuestions}
                    setSearchResults={setSearchResults}
                  />
                )
              })
            }


            if (result.showCitations && result.citations !== undefined && result.citations?.length > 0) {
              result.citations.forEach((citation, citationIdx) => {
                publicationRows.push(
                  <PublicationRow
                    rowType="citation"
                    rowIdx={rowIdx+1 + "-C" + citationIdx}
                    deleteMode={deleteMode}
                    publication={citation}
                    handlePaperSelect={handlePaperSelect}
                    selectedPapers={selectedPapers}
                    showMetadata={showMetadata}
                    searchResults={searchResults}
                    llmQuestions={llmQuestions}
                    setSearchResults={setSearchResults}
                  />
                )
              })
            }
            return publicationRows;
          })}
          </tbody>
        </table>    
      </div>
    </>
   );
}
 
export default PublicationTable;