from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views.core_views import (
    PublicationMetadataView,
    SearchAndCleanView,
    SearchStringDifferenceView,
    ManualAddPublicationView,
    HistoricalSearchQueryResultsView
)
from .views.crud_views import PublicationViewSet
from .views.export_views import ExportView

# Router for CRUD operations
router = DefaultRouter()
router.register(r'publication', PublicationViewSet)

# Core backend functions
core_urls = [
    path('search-and-clean', SearchAndCleanView.as_view(), name='search-and-clean'),
    path('publication-metadata', PublicationMetadataView.as_view(), name='publication-metadata'),
    path('manual-add-publication', ManualAddPublicationView.as_view(), name='manual-add-publication'),
    path('search-string-difference', SearchStringDifferenceView.as_view(), name='search-string-difference'),
    path('historical-search', HistoricalSearchQueryResultsView.as_view(), name='historical-search'),
]

# Web controller views
web_urls = [
    # path('', include(router.urls)),
    path('export', ExportView.as_view(), name='publication-export'),
    path('export/*', ExportView.as_view(), name='publication-export'),
]
 
urlpatterns = [
    *core_urls,
    *web_urls
]