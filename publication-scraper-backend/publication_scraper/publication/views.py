import logging
from itertools import product

from django.http import JsonResponse
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from utils import Logger

from .interfaces.backward_search import BackwardSearch
from .interfaces.filter.llm_filter import FilterResponse, LLMFilter
from .interfaces.forward_search import ForwardSearch
from .interfaces.validation import PublicationValidator
from .models import Publication, PublicationMetadata
from .serializers import (
    PublicationLLMFilterSerializer,
    PublicationSnowballingSerializer,
    PublicationValidationSerializer,
)

log = Logger(__name__)

class PublicationSnowballingView(APIView):
    
    def post(self, request):
        serializer = PublicationSnowballingSerializer(data=request.data)
        if serializer.is_valid():
            
            publication_ids = serializer.validated_data.get('publication_ids')  
            search_type = serializer.validated_data.get('search_type')
            show_metadata = serializer.validated_data.get('show_metadata')
            publications = Publication.objects.filter(paper_id__in=publication_ids)

            log.info(f"Snowballing {search_type} search for {len(publications)} publications.")
            
            if search_type == 'forward':
                fs = ForwardSearch(publications, show_metadata=show_metadata)
                results = fs.search()

            elif search_type == 'backward':
                bs = BackwardSearch(publications, show_metadata=show_metadata)
                results = bs.search()
                
            return JsonResponse({ "results": results})
        return JsonResponse(serializer.errors, status=HTTP_400_BAD_REQUEST)


class PublicationValidationView(APIView):

    def post(self, request):
        serializer = PublicationValidationSerializer(data=request.data)
        if serializer.is_valid():

            query = serializer.validated_data['query']
            all_queries = list(product(query['primary'], query['secondary'], query['tertiary']))
            
            validator = PublicationValidator()
            validated_results = validator.validate(all_queries)
            
            return JsonResponse(validated_results)
        return JsonResponse(serializer.errors, status=HTTP_400_BAD_REQUEST)


class PublicationLLMFilterView(APIView):

    def post(self, request):
        serializer = PublicationLLMFilterSerializer(data=request.data)
        if serializer.is_valid():
            
            questions = serializer.validated_data['questions']
            paper_ids = serializer.validated_data.get('paper_ids')

            # Data transformation
            publications = list(PublicationMetadata.objects.filter(publication_id__in=paper_ids))
            log.info(f"Filtering {len(publications)} publications.")
            if len(publications) != len(paper_ids):
                missing_papers = set(paper_ids) - set([p.publication_id for p in publications])
                missing_publications = Publication.objects.filter(paper_id__in=missing_papers)
                publications.extend(missing_publications)
            
            questions = [
                FilterResponse(
                    id       = question['id'],
                    question = question['question'],
                    answer   = question['answer']
                ) for question in questions
            ]

            # Filter publications by questions
            llm_filter = LLMFilter()
            llm_filter.parse(publications, questions)
            results = llm_filter.completion()

            return JsonResponse({ "results" : results })
        
