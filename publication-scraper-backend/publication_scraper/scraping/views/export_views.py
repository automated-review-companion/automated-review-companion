from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView

from publication.models import Publication
from scraping.filters import PublicationFilter
from scraping.infrastructure.data_export import (
    BibtexExporter,
    CsvExporter,
    DataExporter,
    ExportType,
    RisExporter,
)
from utils import Controller


class ExportView(APIView):

    filter_backends = [DjangoFilterBackend]
    filterset_class = PublicationFilter
    
    # @Controller
    def post(self, request):
        """ Export the publications based on the given filters. """
        
        export_format = request.data.get('format', ExportType.CSV.value)
        paper_ids = request.data.get('paper_ids', [])
        if isinstance(paper_ids, str):
            paper_ids = paper_ids.split(',')

        # Apply filters
        # filter_backend = DjangoFilterBackend()
        # filter_backend.request = request
        # publications = filter_backend.filter_queryset(request, Publication.objects.all(), self)
        # publications = list(publications)
        publications = Publication.objects.filter(paper_id__in=paper_ids)
        publications = list(publications)
        
        exporter = self.get_exporter(export_format)
        exporter.export(publications)
        
        response = HttpResponse(exporter.exported_data, content_type=exporter.content_type)
        response['Content-Disposition']           = f'attachment; filename="publications.{exporter.file_extension}"'
        response["Access-Control-Expose-Headers"] = "Content-Type, Content-Disposition"
        return response
      
    def get_exporter(self, format: str) -> DataExporter:
        """
        Get the exporter based on the given format.
        
        :param format (str): The format to be used.
        :rettype DataExporter: The exporter to be used.
        """
        
        if format == ExportType.CSV.value:
            return CsvExporter()
        elif format == ExportType.BIBTEX.value:
            return BibtexExporter()
        elif format == ExportType.RIS.value:
            return RisExporter()
          
        raise ValueError(f"Unsupported format: {format}")        
