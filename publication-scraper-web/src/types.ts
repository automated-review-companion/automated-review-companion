
export type SearchResult = {
  matches: SearchMatch,
  results: Publication[],
  variations: KeywordVariation[],
}

export type KeywordVariation = {
  word: string,
  variants: string[]
  synonyms: string[]
}

export type SearchMatch = {
  num_matches: number,
  papers: SearchMatchPaper[],
  percentage_match: number
}

export type SearchMatchPaper = {
  doi: string,
  title: string
}

export type Publication = {
  paper_id: string,
  paper_title: string,
  searched_from: string,
  search_string: string[] | string,
  formatted_search_string: string,
  status: string

  // Metadata fields
  abstract?: string,
  authors?: Author[],
  citation_count?: number,
  conference_journal?: string,
  doi?: string,
  doi_url?: string,
  keywords?: string[],
  publication_date?: string,
  publication_type?: string[],
  publisher?: string,
  semantic_scholar_url?: string,

  // LLM Questions
  llm_responses?: LLMQuestion[]

  // Snowballing fields
  references?: Publication[],
  citations?: Publication[],
  showReferences?: boolean,
  showCitations?: boolean

  // View fields
  diffType?: DiffType
} 

export type DiffType = "add" | "remove" | "common"

export type SnowballingSearch = Publication & {
  references?: Publication[]
  citations?: Publication[]
}

export type Author = {
  name: string,
  affiliation: string[],
}

export type SearchForm = {
  id?: string,
  validation_papers: string[],
  search_terms: {
    advanced: string,
    primary: string[],
    secondary: string[],
    tertiary: string[]
  },
  year_start: number,
  year_end: number,
  sources: SearchEngineType[]
}

export enum SearchEngineType {
  DBLP = "DBLP",
  SEMANTIC_SCHOLAR = "SEMANTIC_SCHOLAR",
  WEB_OF_SCIENCE = "WEB_OF_SCIENCE",
  IEEE_XPLORE = "IEEE_XPLORE",
  SCOPUS = "SCOPUS"
}

export type LLMQuestion = {
  id: number,
  question: string,
  answer: string
}

export type LLMPaperFilterResponse = {
  paper_id: string,
  response: LLMQuestion[]
}

export enum SearchMode {
  SIMPLE = "simple",
  ADVANCED = "advanced"
}