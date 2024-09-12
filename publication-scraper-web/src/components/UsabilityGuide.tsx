import { tooltipText } from '@/data/tooltip';
import CloseIcon from '@mui/icons-material/Close';
import InfoIcon from '@mui/icons-material/Info';
import { IconButton, Modal, Tooltip } from "@mui/material";
import { Button } from './ui/button';


export interface UsabilityGuideProps {
  showUsabilityGuide: boolean,
  setShowUsabilityGuide: React.Dispatch<React.SetStateAction<boolean>>,
  handleClose: () => void
} 

const UsabilityGuide: React.FC<UsabilityGuideProps> = (props) => {
  const { 
    showUsabilityGuide,
    setShowUsabilityGuide,
    handleClose 
  } = props;

  return (
    <>
      <Tooltip title={tooltipText.usabilityGuide}>
        <Button className="bg-blue-500/80" onClick={() => setShowUsabilityGuide(true)}>
          <InfoIcon style={{ fontSize: "1.5rem" }} />
        </Button>
      </Tooltip>
      <Modal open={showUsabilityGuide} onClose={() => setShowUsabilityGuide(false)}>
        <div className="container p-5 z-10 bg-white" style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '80%',
          height: '80%',
          overflow: 'scroll',
          borderRadius: '5px'
        }}>
          <div className="container p-5">

            <div className="d-flex justify-content-between mb-3">
              <h3 className="text-4xl font-medium ">Usability Guide</h3>
              <Tooltip title="Close" className="flex">
                <IconButton onClick={handleClose} color="error">
                  <CloseIcon />
                </IconButton>
              </Tooltip>
            </div>

            <section id="introduction">
              <h4 className="text-3xl font-medium">Introduction</h4>
              <div className="divider border-bottom my-3"></div>
              <div className="d-flex flex-column pb-3">
                <span>ARC is an iterative tool that allows users to search for publications based on the search terms, year range, and databases selected.</span>
                <span>The tool provides functionalities to search for papers, compare search results, snowballing search, and filter papers based on the LLM engine.</span>

                <span className="pt-3">The following sections provide a detailed guide on how to use the tool effectively.</span>
                
                <li><a href="#search-bar-section" className="text-blue-500 underline">Search Bar</a></li>
                <li><a href="#search-results-section" className="text-blue-500 underline">Search Results</a></li>
                <li><a href="#search-diff-section" className="text-blue-500 underline">Search History & Difference Mode</a></li>
                <li><a href="#snowballing-section" className="text-blue-500 underline">Forward and Backward Search (Snowballing)</a></li>
                <li><a href="#metadata-section" className="text-blue-500 underline">Metadata</a></li>
                <li><a href="#llm-question-section" className="text-blue-500 underline">Paper Filtering (LLM-Powered)</a></li>
                <br />

                <span>Click on the section links to navigate to the respective section.</span>
              </div>
            </section>

            <section id="user-flow">
              <h4 className="text-3xl font-medium">User Flow</h4>
              <div className="divider border-bottom my-3"></div>
              <div className="d-flex flex-column pb-3">
                <span>The recommended user flow of the tool is as follows:</span>
                <br />
                <ol className="list-decimal ps-8">
                  <li>Enter the search terms, year range, and select the databases to search from.</li>
                  <li>Click on the Search button to search for publications.</li>
                  <li>View the search results and select the papers.</li>
                  <li>Iteratively modify search parameters to provide a desired set of papers.</li>
                  <li>Perform Snowballing Search to find papers that the selected papers cite or that cite the selected papers.</li>
                  <li>View the metadata of the selected papers.</li>
                  <li>Filter the papers based on the LLM Questions.</li>
                  <li>Export the selected papers in CSV/BibTex/RIS format.</li>
                </ol>
              </div>
            </section>

            <section id="search-bar-section">
              <h4 className="text-3xl font-medium">Search Bar</h4>
              <div className="divider border-bottom my-3"></div>
              <div className="d-flex flex-column pb-3">
                <span>The search bar allows you to search for publications based on the search terms, year range, and databases selected.</span>
                <span>There are two search modes:</span>
                <br />
                <div className="ps-3">
                  <li className="list-disc">Simple mode, you can enter primary, secondary, and tertiary search terms.</li>
                  <li className="list-disc">Advanced mode, you can enter a case-insensitive boolean search string.
                    <ul className="list-decimal ps-8">
                      <li>Use 'AND', 'OR', 'NOT' operators to combine search terms. (Case insensitive) </li>
                      <li>Use quotations to search for exact phrases.</li>
                    </ul>
                  </li>
                </div>
                <br />
                <div className="ps-3">
                  <li>Year range allows you to filter publications based on the publication year.</li>
                  <li>Databases: at least one source must be selected to proceed in searching.</li>
                  <li>Validation papers allow you to enter the DOI of the known existing papers to validate if the search configurations result in the validation papers.</li>
                  <li>Clear button resets and clears all search parameters and results.</li>
                </div>
                <span>To start searching, simply press the Search button.</span>
              </div>
            </section>
            
            <section id="search-results-section">
              <h4 className="text-3xl font-medium">Search Results</h4>
              <div className="divider border-bottom my-3"></div>
              <div className="d-flex flex-column pb-3">
                <span>The search results display the matched papers based on the search configurations.</span>
                <span>Each row represents a publication with the following columns:</span>
                <br />
                <ol className="list-decimal ps-8">
                  <li>Checkbox: allows you to select the paper</li>
                  <li>Paper ID: the unique identifier of the paper</li>
                  <li>Paper Title: the title of the paper</li>
                  <li>Searched From: the source where the paper was searched from</li>
                  <li>Search String: the search string used to find the paper</li>
                  <li>Formatted Search String: the formatted search string</li>
                  <li>Status: the status of the paper</li>
                </ol>
                <br />
                <div className="ps-3">
                  <li>Metadata columns are hidden by default. To show the metadata, click on the Metadata button.</li>
                  <li>LLM Questions columns are hidden by default. To show the LLM Questions, click on the LLM Questions button.</li>
                  <li>Click on the checkbox to select the paper. You can select all papers by clicking on the Select All button.</li>
                  <li>Click on the Export button to export the selected papers in CSV/BibTex/RIS format.</li>
                </div>
              </div>
            </section>

            <section id="search-diff-section">
              <h4 className="text-3xl font-medium">Search History & Difference Mode</h4>
              <div className="divider border-bottom my-3"></div>

              <div className="d-flex flex-column pb-3">
                <span>
                  The Search History allows you to compare two search histories. 
                  The differences between the search results are indicated by green and red rows,
                  indicating the papers that are added and removed from the search results.
                </span>
                <span>Click on the Search History button to enable the difference mode.</span>
                <span>Click on the search history to choose the search history to compare.</span>
                <br />
                <div className="ps-3">
                  <li><b>Original Search Result:</b> shown on the left, indicates columns unique to the search result in green.</li>
                  <li><b>Comparison Search Result:</b> shown on the right, indicates columns unique to the comparison result in red.</li>
                </div>
              </div>
            </section>

            <section id="snowballing-section">
              <h4 className="text-3xl font-medium">Forward and Backward Search (Snowballing)</h4>
              <div className="divider border-bottom my-3"></div>
              <div className="d-flex flex-column pb-3">
                <span>The Snowballing Search allows you to search for papers that the selected papers cite or that cite the selected papers.</span>
                <span className="pb-3">To perform Snowballing Search, follow the following steps:</span>
                <ol>
                  <li>Click on the Forward Search or Backward Search button to start the snowballing search.</li>
                  <li>Click on the Expand/Collapse button on the original paper that has undergone snowballing search to view the references and citations of the paper.</li>
                </ol>
                
                <li>References: the papers that the selected paper cites.</li>
                <li>Citations: the papers that cite the selected paper.</li>
              </div>
            </section>

            <section id="metadata-section">
              <h4 className="text-3xl font-medium">Metadata</h4>
              <div className="divider border-bottom my-3"></div>
              <div className="d-flex flex-column pb-3">
                <span>The metadata columns display the metadata of the selected papers.</span>
                <span>The metadata columns include:</span>
                <br />
                <div className="ps-8">
                  <ol className="list-disc">
                    <li>Abstract</li>
                    <li>Authors</li>
                    <li>Citations Count</li>
                    <li>Conference/Journal</li>
                    <li>DOI</li>
                    <li>DOI URL</li>
                    <li>Keywords</li>
                    <li>Publication Date</li>
                    <li>Publication Type</li>
                    <li>Publisher</li>
                    <li>Semantic Scholar URL</li>
                  </ol>
                </div>
              </div>
            </section>        
            
            <section id="llm-question-section">
              <h4 className="text-3xl font-medium">Paper Filtering (LLM-Powered)</h4>
              <div className="divider border-bottom my-3"></div>
              <div className="d-flex flex-column pb-3">
                <span>The Paper Filtering functionality can further filter the papers provided with more insight by the user.</span>
                <span>The LLM engine (GPT-4) further filters the papers based on the user's preferences.</span>
                <span className="pb-3">In order to provide a more accurate classification result, it is recommended to ensure metadata for the selected papers are populated.</span>
            
                <ol className="list-disc ps-8">
                  <li><b>Question:</b> Each question would be shown as a distinct column for each resulting paper.</li>
                  <li><b>Response:</b> This denotes the possible classifications the LLM can categorize the paper as, based on the metadata</li>
                </ol>
                <br />

                <span>Click on the LLM Filter button to filter the papers based on the LLM Questions.</span>
              </div>
            </section>
          </div>
        </div>
      </Modal>
    </>
  )
};

export default UsabilityGuide;