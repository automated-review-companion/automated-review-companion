from django_filters.rest_framework import DjangoFilterBackend
from publication.models import Publication
from publication_scraper.permissions import IsReadOnly, IsReadWrite
from rest_framework import viewsets

from ..filters import PublicationFilter
from ..serializers.core_serializers import PublicationSerializer


class PublicationViewSet(viewsets.ModelViewSet):
    """ 
    ViewSet for the Publication model. 
    
    Example requests:
    GET ./publication?paper_id=1234
    
    PUT ./publication?paper_id=1234
    {
        "paper_id": "1234",
        "paper_title": "A paper title",
        "search_string": "A search string",
        "searched_from": "A search engine",
        "formatted_search_string": "A formatted search string",
        "status": "NEW"
    }
    
    POST ./publication
    {
        "paper_id": "1234",
        "paper_title": "A paper title",
        "search_string": "A search string",
        "searched_from": "A search engine",
        "formatted_search_string": "A formatted search string",
        "status": "NEW"
    }
    
    PATCH ./publication?paper_id=1234
    {
        "status": "VALIDATED"
    }
    
    DELETE ./publication?paper_id=1234    
    """
    queryset = Publication.objects.all()
    serializer_class = PublicationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = PublicationFilter

    def get_permissions(self):
        """ Assign permissions based on the request method """
        
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            self.permission_classes = [IsReadOnly]
        else:
            self.permission_classes = [IsReadWrite]
        return [permission() for permission in self.permission_classes]