from abc import abstractmethod

from django.db.models import Model as DjangoModel


class Exportable:
    """
    Exportable is a class that represents a data structure 
    that can be exported to a file.
    """
    
    def __init__(self):
        self.data = {}
    
    @abstractmethod
    def exportable_fields(self):
        """ Return the fields that can be exported. """
        pass
    
    def load_data(self):
        """
        Export the data to a specific format.
        
        :param exporter (DataExporter): The exporter to be used.
        :rettype str: Exported data as a string in the desired format.
        
        Example Usage:
        Retrieve your <Exportable> data
        
            publications = Publication.objects.all()  
            
            exporter = CSVExporter()
            exporter.export(publications)
        
        Returns the exported data as a string in <ExportType> format:
        
            exporter.exported_data
            exporter.content_type
            exporter.file_extension
        """
        
        for name in self.exportable_fields():
            if self._is_attribute(name):
                if isinstance(getattr(self, name), DjangoModel):
                    innner_attribute = getattr(self, name).to_dict()
                    self.data = {
                        **self.data,
                        **innner_attribute
                    }
                    print(self.data)
                else:
                    self.data[name] = getattr(self, name)

    def _is_attribute(self, name: str) -> bool:
        """
        Check if the given name is an attribute of the object.
        
        :param name (str): The name to be checked.
        :rettype bool: True if the name is an attribute, False otherwise.
        """
        try:
            is_private_attribute    = name.startswith('_')
            is_callable             = callable(getattr(self, name))
            is_magic_method         = name.startswith('__') and name.endswith('__')
            is_attribute = not(is_private_attribute or is_callable or is_magic_method)
            
            return is_attribute
        except Exception as e:
            raise Exception(f"Attribute: {name} Error: {e}")