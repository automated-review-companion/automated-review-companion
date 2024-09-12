export const tooltipText = {
  usabilityGuide: "Click to view the usability guide",
  search: {
    primary: {
      hint: "Primary search term is required", 
      example: "i.e., AI, Deep Learning, etc. (Press Enter to add the search term)",
    },
    secondary: {
      hint: "Secondary search term",
      example: "i.e., Machine Learning, Generative AI, etc. (Press Enter to add the search term)",
    },
    tertiary: {
      hint: "Tertiary search term",
      example: "i.e., Deep Reinforcement Learning, Neural Networks, etc. (Press Enter to add the search term)",
    },
    advanced: "Required field: advanced case-insensitive boolean search string. Use 'AND', 'OR', 'NOT' operators to combine search terms, and quotations to search for exact phrases.",
    yearRange: "Year range including the start and end years (i.e., 2023 - 2024)",
    database: "Select the databases to search from: Click on the database name to toggle the selection; a filled checkbox indicates the database is selected. At least one must be selected.",
    validationPapers: "Enter the DOI of the validation papers to validate if the search configurations result in the validation papers.",
    clearButton: "Resets and clears all search parameters and results",
    llmQuestions: "Enter the questions to filter the papers. At least one question is required. Answers should be comma-separated categorical answers.",
    llmQuestion: {
      add: "Add a question",
      remove: "Remove a question"
    },
    history: "Enable diff mode to compare two search histories. Click on the search history to choose the search history to compare.",
  },
  results: {
    toggleFullScreen: {
      enter: "Click to enter fullscreen",
      exit: "Click to exit fullscreen"
    },
    filterBar: "Filter the search results",
    manualAdd: "Manually add a paper to the search results",
    manualAddCsv: "Drag a CSV file here with DOIs to manually add papers",
    selectAll: "Select all papers in the search results",
    deselectAll: "Deselect all papers in the search results",
    hideMetadata: "Hide metadata for the selected papers",
    populateMetadata: "Populate metadata for the selected papers. Only applicable to papers with DOI",
    forwardSearch: "Search for papers that the selected papers cite",
    backwardSearch: "Search for papers that cite the selected papers",
    export: "Export selected papers in CSV/BibTex/RIS format",
  }
}