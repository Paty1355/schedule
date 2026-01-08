"""
helpers for creating forms
"""
import streamlit as st
from typing import Dict, List, Tuple, Callable, Optional, Any
import traceback
import time
from app_config.constants import COURSE_TYPE_LABELS_PL
from app_config.constants import ROOM_TYPE_LABELS_PL
from app_config.constants import WEEKDAY_OPTIONS_PL, WEEKDAY_PL_TO_EN


class FormHelper:
    """helper class for creating and handling forms"""
    
    @staticmethod
    def show_success_message(key: str):
        """displays and clears success message from session_state"""
        if key not in st.session_state:
            st.session_state[key] = None
        
        if st.session_state[key]:
            st.success(st.session_state[key])
            st.session_state[key] = None
    
    @staticmethod
    def build_options_dict(items: List[Tuple], 
                          label_format: str = "{0} - {1}",
                          id_index: int = 0) -> Dict[str, int]:
        """
        creates a dictionary of options for selectbox
        """
        options = {}
        for item in items:
            if len(item) > 1:
                label = label_format.format(*item[1:])
                options[label] = item[id_index]
        return options
    
    @staticmethod
    def safe_insert(repo, data: dict, success_key: str, 
                   success_message: str) -> bool:
        """
        safely inserts data with error handling
        """
        try:
            with st.expander("🔍 debug - data to insert", expanded=False):
                st.json(data)
            
            repo.insert(data)
            
            st.session_state[success_key] = success_message
            
            time.sleep(0.1)
            
            st.rerun()
            return True
            
        except Exception as e:
            error_msg = str(e)
            st.error(f"❌ Błąd podczas operacji bazodanowej")
            st.error(f"📝 Szczegóły: {error_msg}")
            
            with st.expander("🔍 Pełne szczegóły błędu (dla dewelopera)", expanded=False):
                st.code(traceback.format_exc())
                st.write("**Próbowane dane:**")
                st.json(data)
                st.write(f"**Repozytorium:** {repo.__class__.__name__}")
            
            return False
    
    @staticmethod
    def render_data_table(repo, columns: List[str], 
                         data_transformer: Optional[Callable] = None):
        """
        renders a data table from repository
        """
        try:
            items = repo.get_all()
            if not items:
                st.info("📭 Brak danych w systemie")
                return
            
            if data_transformer:
                data = [data_transformer(item) for item in items]
            else:
                data = items
            
            import pandas as pd
            df = pd.DataFrame(data, columns=columns)
            st.dataframe(df, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Błąd podczas pobierania danych: {str(e)}")
            with st.expander("🔍 Szczegóły błędu"):
                st.code(traceback.format_exc())


class SelectBoxBuilder:
    """builder for selectbox with predefined patterns"""
    
    def __init__(self, repos: Dict):
        self.repos = repos
    
    def department_selector(self, label: str = "department", 
                           include_all: bool = False) -> Optional[int]:
        """selectbox for departments"""
        departments = self.repos['departments'].get_all()
        if not departments:
            st.warning("⚠️ Brak wydziałów w systemie")
            return None
        
        options = {}
        if include_all:
            options["Wszystkie wydziały"] = None
        
        options.update({
            f"{d[1]} - {d[2]}": d[0] for d in departments
        })
        
        selected = st.selectbox(label, list(options.keys()))
        return options[selected]
    
    def building_selector(self, label: str = "building", 
                         dept_id: Optional[int] = None) -> Optional[int]:
        """selectbox for buildings with department filtering"""
        buildings = self.repos['buildings'].get_all()
        
        if dept_id:
            buildings = [b for b in buildings if b[3] == dept_id]
        
        if not buildings:
            st.warning("⚠️ Brak budynków")
            return None
        
        options = {f"{b[1]}": b[0] for b in buildings}
        selected = st.selectbox(label, list(options.keys()))
        return options[selected]
    
    def group_selector(self, label: str = "group",
                      dept_id: Optional[int] = None,
                      include_none: bool = False) -> Optional[int]:
        """selectbox for groups"""
        groups = self.repos['groups'].get_all()
        
        if dept_id:
            groups = [g for g in groups if g[3] == dept_id]
        
        options = {}
        if include_none:
            options["Brak (grupa niezależna)"] = None
        
        options.update({
            f"{g[1]} - {g[2]}": g[0] for g in groups
        })
        
        if not options:
            st.warning("⚠️ Brak grup w systemie")
            return None
        
        selected = st.selectbox(label, list(options.keys()))
        return options[selected]
    
    def teacher_selector(self, label: str = "teacher",
                        dept_id: Optional[int] = None) -> Optional[int]:
        """selectbox for teachers"""
        teachers = self.repos['teachers'].get_all()
        
        if dept_id:
            teachers = [t for t in teachers if t[3] == dept_id]
        
        if not teachers:
            st.warning("⚠️ Brak prowadzących")
            return None
        
        options = {
            f"{t[1]} {t[2]}": t[0] for t in teachers
        }
        
        selected = st.selectbox(label, list(options.keys()))
        return options[selected]
    
    def course_selector(self, label: str = "course",
                       dept_id: Optional[int] = None) -> Optional[int]:
        """selectbox for courses"""

        
        courses = self.repos['courses'].get_all()
        
        if dept_id:
            courses = [c for c in courses if c[3] == dept_id]
        
        if not courses:
            st.warning("⚠️ Brak przedmiotów")
            return None
        
        options = {}
        for c in courses:
            course_type_pl = COURSE_TYPE_LABELS_PL.get(c[4], c[4])
            options[f"{c[1]} - {c[2]} ({course_type_pl})"] = c[0]
        
        selected = st.selectbox(label, list(options.keys()))
        return options[selected]
    
    def room_selector(self, label: str = "room",
                     building_id: Optional[int] = None) -> Optional[int]:
        """selectbox for rooms"""

        rooms = self.repos['rooms'].get_all()
        
        if building_id:
            rooms = [r for r in rooms if r[1] == building_id]
        
        if not rooms:
            st.warning("⚠️ Brak sal")
            return None
        
        options = {}
        for r in rooms:
            room_type_pl = ROOM_TYPE_LABELS_PL.get(r[5], r[5])
            room_label = f"{r[2]} - {r[3] or ''} ({room_type_pl})" if r[3] else f"{r[2]} ({room_type_pl})"
            options[room_label] = r[0]
        
        selected = st.selectbox(label, list(options.keys()))
        return options[selected]

    def weekday_selector(self, label: str = "weekday", 
                        key: Optional[str] = None) -> str:
        """selectbox for weekdays with Polish names"""
        
        selected_pl = st.selectbox(label, WEEKDAY_OPTIONS_PL, key=key)
        return WEEKDAY_PL_TO_EN[selected_pl]

class EditFormHelper:
    """helper for creating edit/delete forms"""
    
    @staticmethod
    def safe_update(repo, id_value: int, data: dict, success_key: str, 
                   success_message: str) -> bool:
        """safely updates data with error handling"""
        try:
            repo.update('id', id_value, data)
            st.session_state[success_key] = success_message
            time.sleep(0.1)
            st.rerun()
            return True
        except Exception as e:
            st.error(f"❌ Błąd aktualizacji: {str(e)}")
            return False
    
    @staticmethod
    def safe_delete(repo, id_value: int, success_key: str,
                   success_message: str) -> bool:
        """safely deletes data with error handling"""
        try:
            repo.delete('id', id_value)
            st.session_state[success_key] = success_message
            time.sleep(0.1)
            st.rerun()
            return True
        except Exception as e:
            st.error(f"❌ Błąd usuwania: {str(e)}")
            return False
    
    @staticmethod
    def render_edit_delete_buttons(repo, item_id: int, update_data: dict,
                                   success_key: str, item_name: str):
        """renders save and delete buttons"""
        col_save, col_del = st.columns(2)
        
        with col_save:
            if st.form_submit_button("💾 Zapisz", type="primary"):
                EditFormHelper.safe_update(
                    repo, item_id, update_data,
                    success_key, f"✅ Zaktualizowano: {item_name}"
                )
        
        with col_del:
            if st.form_submit_button("🗑️ Usuń", type="secondary"):
                EditFormHelper.safe_delete(
                    repo, item_id, success_key,
                    f"✅ Usunięto: {item_name}"
                )
