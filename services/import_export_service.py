"""
import/export data service - facade for import/export operations
"""
from typing import Dict, Any
from io import BytesIO
from .exporters import ExcelExporter
from .importers import ExcelImporter


class ImportExportService:
    """Facade service for data import and export operations"""
    
    def __init__(self, repos):
        self.repos = repos
        self.exporter = ExcelExporter(repos)
        self.importer = ExcelImporter(repos)
    
    def export_all_data(self) -> BytesIO:
        """
        exports all data to excel file in import-compatible format
        """
        return self.exporter.export_all_data()
    
    def import_from_excel(self, excel_file) -> Dict[str, Any]:
        """
        imports data from excel file
        """
        return self.importer.import_from_excel(excel_file)
