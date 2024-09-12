import { Box, Chip, Tooltip } from "@mui/material";
import { SearchResult } from "../types";
import { MultiLayerSearch } from "./SearchTermAutocomplete";

export interface SearchTermProps {
  option: string,
  index: number,
  getTagProps: (params: { index: number }) => any,
  field: MultiLayerSearch,
  searchResults: SearchResult,
  setSearchResults: React.Dispatch<React.SetStateAction<SearchResult>>,
  handleChipClick: (chip: string, field: MultiLayerSearch) => void
}

const SearchTermChip: React.FC<SearchTermProps> = (props) => {
  const { option, index, getTagProps, field, searchResults, handleChipClick } = props;

  if (!searchResults.variations.find((variation) => variation.word === option)) {
    return (
      <Chip
        label={option}
        {...getTagProps({ index })}
      />
    )
  }

  const variations = searchResults.variations.find((variation) => variation.word === option)
  const hasSynonyms = variations && variations?.synonyms.length > 0;
  const hasVariants = variations && variations?.variants.length > 0;

  return ( 
    <Tooltip
      className="word-variant-tooltip"
      title={
        <div>
          {
            hasSynonyms &&
            <>
              <span>Synonyms:</span>
              <Box className="word-variant-box mb-2" width={200}>
                {
                  searchResults.variations.find((variation) => variation.word === option)?.synonyms.map((synonym) => (
                    <div
                      onClick={() => handleChipClick(synonym, field)}
                      className="word-variant-chip"
                      style={{ color: "black", cursor: "pointer" }}
                    >
                      {synonym}
                  </div>
                ))}
              </Box>
            </>
          }
          {
            hasVariants &&
            <>
              <span>Variants:</span>
              <Box className="word-variant-box" width={200}>
                {
                  searchResults.variations.find((variation) => variation.word === option)?.variants.map((variant) => (
                    <div
                      onClick={() => handleChipClick(variant, field)}
                      className="word-variant-chip"
                      style={{ color: "black", cursor: "pointer" }}
                    >
                      {variant}
                  </div>
                ))}
              </Box>
            </>
          }
          </div>
        }
      >
    <Chip
      label={option}
      {...getTagProps({ index })}
    />
  </Tooltip>
  );
}
 
export default SearchTermChip;