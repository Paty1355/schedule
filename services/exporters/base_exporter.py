"""
Base exporter - common functionality for data export
"""
from typing import Dict, Any, List, Tuple
import pandas as pd


class BaseExporter:
    """Base class with common export functionality"""
    
    def __init__(self, repos):
        self.repos = repos
    
    def _create_lookup_map(self, items: List[Tuple], key_index: int) -> Dict:
        """Create a dictionary for fast lookups by key index"""
        return {item[key_index]: item for item in items}
    
    def _safe_str(self, value, default=''):
        """Safely convert value to string"""
        return str(value) if pd.notna(value) and value else default
