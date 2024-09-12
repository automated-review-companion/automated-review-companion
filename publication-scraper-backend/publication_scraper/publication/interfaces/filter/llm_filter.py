from typing import List, Tuple, Union

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel
from publication.interfaces.llm.azure import AzureLLM
from publication.models import Publication, PublicationMetadata
from utils import Logger

log = Logger(__name__)

class FilterResponse(BaseModel):
    id: str
    question: str
    answer: str


class LLMFilterResponse(BaseModel):
    paper_id: str
    response: List[FilterResponse]


class LLMFilter:
    def __init__(self):
        self.prompt = "Ask a question about the paper: {paper_data}\nQuestion and Answers: {qna}\n{format_instructions}"
        self.model = AzureLLM()
        self.llm = self.model.llm
        self.results: List[LLMFilterResponse] = []

    def parse(self, paper_data: List[Union[Publication, PublicationMetadata]], qna: List[FilterResponse]):
        self.paper_data = self._parse_paper_data(paper_data)
        self.qna        = self._parse_qna(qna)


    def completion(self):
        """ Complete the LLM filter """
        for pid, paper in self.paper_data:
            self._complete_llm_filter(pid, paper)
        return self.results
    

    def _complete_llm_filter(self, paper_id: str, paper_data: str):
        """ Complete the LLM filter for a single paper """

        assert self.paper_data, "Paper data is required"
        assert self.qna, "QnA is required"

        parser = JsonOutputParser(pydantic_object=LLMFilterResponse)
        filter_prompt = PromptTemplate(
            template        = self.prompt,
            input_variables = ["paper_data", "qna"],
            partial_variables = {"format_instructions": parser.get_format_instructions()}
        )
        chain = filter_prompt | self.llm | parser
        response = chain.invoke({"paper_data": self.paper_data, "qna": self.qna})
        response["paper_id"] = paper_id
        log.info(f"Completed LLM filter for paper {paper_data}, response: {response}")
        self.results.append(response)

    def _parse_paper_data(self, paper_data: List[Union[PublicationMetadata, Publication]]) -> List[Tuple[str, str]]:
        """ 
        Parse the publication & metadata in the format:
        - field_name: field_value

        Returns a list of tuples with 
        1. publication_id and the 
        2. formatted paper data
        """
        all_paper_data = []
        for paper in paper_data:
            if isinstance(paper, PublicationMetadata):
                paper_data_dict = paper.to_dict(show_publication=True)
                paper_id = paper.publication_id
            else:
                paper_data_dict = paper.to_dict()
                paper_id = paper.paper_id
            paper_data_str = "\n".join([f"{field}: {value}" for field, value in paper_data_dict.items()])
            all_paper_data.append((paper_id, paper_data_str))
        return all_paper_data
        
    def _parse_qna(self, qna: List[FilterResponse]):
        """ 
        Parse the question and answers in the format:
        
            id: number
            question: question
            answer: possible list of answers, separated by a comma
        """
        qna_str = "\n".join([f"{qa.id}: {qa.question}\n{qa.answer}" for qa in qna])
        return qna_str