
import django_filters as dfilter
from publication.models import Publication, PublicationStatus


class PublicationFilter(dfilter.FilterSet):
    """ Filter for the Publication model. """
    
    paper_id = dfilter.CharFilter(lookup_expr='icontains')
    paper_title = dfilter.CharFilter(lookup_expr='icontains')
    search_string = dfilter.CharFilter(lookup_expr='icontains')
    searched_from = dfilter.CharFilter(lookup_expr='icontains')
    status = dfilter.ChoiceFilter(choices=[(status.value, status.name) for status in PublicationStatus])

    class Meta:
        model = Publication
        fields = ['paper_id', 'paper_title', 'search_string', 'searched_from', 'status']