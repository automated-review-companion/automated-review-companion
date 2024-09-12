import csv
import io

from .exportable import Exportable
from .exporter import DataExporter


class CsvExporter(DataExporter):
    """
    Data Exporter into CSV files.
    Github Issue: (#10) Different Export Format
    """
    def __init__(self) -> None:
        super().__init__()
        self.headers        = []
        self.data           = []
        self.content_type   = 'text/csv'
        self.file_extension = 'csv'
        self.exported_data  = ""
        
    def export(self, exportable: Exportable) -> None:
        """
        Export the given data to a CSV format.
        
        :param data (iterable): The data to be exported.
        :rettype str: Exported data as a string in CSV format.
        """
        super().export(exportable)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(self.headers)
        writer.writerows(self.data)
        self.exported_data = output.getvalue()
        