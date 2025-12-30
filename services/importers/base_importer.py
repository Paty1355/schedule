# base_importer.py
"""
Base importer - common functionality for data import
"""
from typing import Dict, Any, List, Tuple, Callable, Optional, Set
import pandas as pd


class BaseImporter:
    """Base class with common import functionality"""
    
    def __init__(self, repos):
        self.repos = repos
        self._cache: Dict[str, List[Tuple]] = {}
    
    def _create_code_lookup(self, items: List[Tuple], code_index: int = 1) -> Dict:
        """Create lookup dictionary by code (usually index 1)"""
        return {item[code_index]: item for item in items}
    
    def _create_name_lookup(self, items: List[Tuple], first_name_idx: int, last_name_idx: int) -> Dict:
        """Create lookup dictionary by full name"""
        return {f"{item[first_name_idx]} {item[last_name_idx]}": item for item in items}
    
    def _init_stats(self) -> Dict[str, Dict[str, int]]:
        """Initialize statistics dictionary"""
        return {
            'wydzialy': {'added': 0, 'skipped': 0},
            'budynki': {'added': 0, 'skipped': 0},
            'sale': {'added': 0, 'skipped': 0},
            'grupy': {'added': 0, 'skipped': 0},
            'prowadzacy': {'added': 0, 'skipped': 0},
            'przedmioty': {'added': 0, 'skipped': 0},
            'przypisania': {'added': 0, 'skipped': 0},
            'plan': {'added': 0, 'skipped': 0}
        }

    def _get_all_cached(self, repo_key: str, refresh: bool = False) -> List[Tuple]:
        """Return cached repo content and refresh only when requested."""
        if refresh or repo_key not in self._cache:
            self._cache[repo_key] = self.repos[repo_key].get_all()
        return self._cache[repo_key]

    def _invalidate_cache(self, repo_key: str) -> None:
        """Drop cache entry so the next access fetches fresh data."""
        self._cache.pop(repo_key, None)

    def _generic_import(
        self,
        excel_file,
        excel_data,
        sheet_schema,
        repo_key: str,
        stats_key: str,
        stats: Dict,
        errors: List[str],
        db_manager,
        prepare_data: Callable[[pd.Series, Dict], Optional[Dict]],
        existing_check: Optional[Callable[[pd.Series, Dict, Set], bool]] = None,
        existing_items: Optional[Set] = None
    ):
        """
        Generic import method for any entity type.
        
        Args:
            excel_file: Excel file object
            excel_data: Parsed Excel data
            sheet_schema: SheetSchema object with sheet_name and columns
            repo_key: Repository key to use for insert
            stats_key: Key in stats dictionary
            stats: Statistics dictionary
            errors: Error list
            db_manager: Database manager
            prepare_data: Function that takes (row, columns) and returns data dict or None if skip
            existing_check: Optional function to check if item already exists
            existing_items: Optional set of existing items for deduplication
        """
        if sheet_schema.sheet_name not in excel_data.sheet_names:
            return
        
        df = pd.read_excel(excel_file, sheet_name=sheet_schema.sheet_name)
        cols = sheet_schema.columns
        if existing_items is None:
            existing_items = set()
        
        for idx, row in df.iterrows():
            try:
                # Check if already exists
                if existing_check and existing_check(row, cols, existing_items):
                    stats[stats_key]['skipped'] += 1
                    continue
                
                # Prepare data for insertion
                data = prepare_data(row, cols)
                
                if data is None:
                    stats[stats_key]['skipped'] += 1
                    continue
                
                # Insert
                self.repos[repo_key].insert(data)
                stats[stats_key]['added'] += 1
                
            except Exception as e:
                db_manager.conn.rollback()
                stats[stats_key]['skipped'] += 1
                errors.append(f"{stats_key.capitalize()} wiersz {idx+2}: {str(e)}")
        
        self._invalidate_cache(repo_key)
