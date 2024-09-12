from abc import ABC
from enum import Enum
from typing import Any, List, Union

from scraping.infrastructure.data_export.exportable import Exportable


class DataExporter(ABC):
    def __init__(self):
        self.content_type           = None
        self.file_extension         = None
        self.headers: List[str]     = []
        self.data: List[List[Any]]  = []
        
    def export(self, exportable: Union[Exportable, List[Exportable]]) -> str:
        """
        Export the given data to a specific format.

        :param data (iterable): The data to be exported.
        :rettype str: Exported data as a string in the desired format.
        """
        
        # List[Exportable]
        if isinstance(exportable, list):
            self.exportable: List[Exportable] = []
            for data in exportable:
                data.load_data()
                self.exportable.append(data)
            
            if len(self.exportable) > 0:
                self.headers    = list(self.exportable[0].data.keys())
                self.data       = [list(data.data.values()) for data in self.exportable]
                
        # Exportable
        else:
            exportable.load_data()    
            self.headers    = list(exportable.data.keys())
            self.data       = list(exportable.data.values())
        
        assert all(len(row) == len(self.headers) for row in self.data)
        

class ExportType(Enum):
    CSV = "CSV"
    BIBTEX = "BIBTEX"
    RIS = "RIS"    
    