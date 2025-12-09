import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DBManager
from database.repositories import *
from database.db_utils import conn_params, create_database_if_not_exists, run_sql_file
from streamlit_config import setup_page_config, load_custom_css
from ui.home import show_home
from ui.basic_data import (
    manage_departments_buildings, manage_rooms, 
    manage_groups, manage_teachers, manage_unavailabilities
)
from ui.courses_management import (
    manage_courses, manage_course_assignments, manage_time_slots
)
from ui.schedule_generator import generate_schedule_ai
from ui.schedule_viewer import view_schedules
from ui.validation import validate_schedule, manual_schedule_edit
from ui.import_export import import_export_data
from ui.edit_data import (
    edit_delete_departments_buildings, edit_delete_rooms,
    edit_delete_groups, edit_delete_teachers, edit_delete_courses,
    edit_delete_course_assignments, edit_time_slots
)


def initialize_db():
    """database initialization"""
    dbname = conn_params.get('dbname', 'timetable_db')
    create_database_if_not_exists(conn_params, dbname)
    db_manager = DBManager(conn_params)
    
    sql_file_path = os.path.join(os.path.dirname(__file__), 'database', 'db_schema.sql')
    run_sql_file(conn_params, sql_file_path)
    
    return db_manager



def get_repositories(db_manager):
    """returns a dictionary with all repositories"""
    return {
        'departments': DepartmentsRepository(db_manager),
        'buildings': BuildingsRepository(db_manager),
        'rooms': RoomsRepository(db_manager),
        'groups': GroupsRepository(db_manager),
        'teachers': TeachersRepository(db_manager),
        'courses': CoursesRepository(db_manager),
        'course_assignments': CourseAssignmentsRepository(db_manager),
        'time_slots': TimeSlotsRepository(db_manager),
        'assignments': AssignmentRepository(db_manager),
        'teacher_unavailabilities': TeacherUnavailabilitiesRepository(db_manager),
        'group_unavailabilities': GroupUnavailabilitiesRepository(db_manager)
    }



def main():
    """main application function"""
    setup_page_config()
    load_custom_css()
    
    db_manager = initialize_db()
    repos = get_repositories(db_manager)
    
    # sidebar - navigation
    with st.sidebar:
        st.markdown("## 📅 System Planu Zajęć")
        st.markdown("---")
        
        menu_option = st.radio(
            "**Nawigacja**",
            [
                "🏠 Strona Główna",
                "📊 Dane Podstawowe",
                "📚 Przedmioty i Zajęcia",
                "🤖 Generator Planu",
                "📋 Podgląd i Raporty",
                "⚙️ Narzędzia"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # submenu
        if menu_option == "📊 Dane Podstawowe":
            submenu = st.selectbox(
                "Wybierz sekcję:",
                ["🏢 Wydziały i Budynki", "🚪 Sale", "👥 Grupy", "👨‍🏫 Prowadzący", "🚫 Niedostępności"],
                label_visibility="collapsed"
            )
        elif menu_option == "📚 Przedmioty i Zajęcia":
            submenu = st.selectbox(
                "Wybierz sekcję:",
                ["📖 Przedmioty", "📋 Przypisania", "⏰ Sloty Czasowe"],
                label_visibility="collapsed"
            )
        elif menu_option == "📋 Podgląd i Raporty":
            submenu = st.selectbox(
                "Wybierz sekcję:",
                ["📊 Podgląd Planów", "🔍 Walidacja", "✍️ Edycja Manualna"],
                label_visibility="collapsed"
            )
        elif menu_option == "⚙️ Narzędzia":
            submenu = st.selectbox(
                "Wybierz narzędzie:",
                ["📥 Import/Eksport", "✏️ Edycja Danych"],
                label_visibility="collapsed"
            )
        else:
            submenu = None
        
        st.markdown("---")
        
        # quick stats
        with st.expander("📊 Szybkie statystyki"):
            try:
                st.metric("📚 Przedmioty", len(repos['courses'].get_all()))
                st.metric("👥 Grupy", len(repos['groups'].get_all()))
                st.metric("🚪 Sale", len(repos['rooms'].get_all()))
                st.metric("📅 Zajęcia", len(repos['assignments'].get_all()))
            except:
                st.info("Ładowanie...")
        
        st.markdown("---")
        st.caption("v1.0 | © 2025")
    
    # routing
    if menu_option == "🏠 Strona Główna":
        show_home(repos)
    
    elif menu_option == "📊 Dane Podstawowe":
        if submenu == "🏢 Wydziały i Budynki":
            manage_departments_buildings(repos)
        elif submenu == "🚪 Sale":
            manage_rooms(repos)
        elif submenu == "👥 Grupy":
            manage_groups(repos)
        elif submenu == "👨‍🏫 Prowadzący":
            manage_teachers(repos)
        elif submenu == "🚫 Niedostępności":
            manage_unavailabilities(repos)
    
    elif menu_option == "📚 Przedmioty i Zajęcia":
        if submenu == "📖 Przedmioty":
            manage_courses(repos)
        elif submenu == "📋 Przypisania":
            manage_course_assignments(repos)
        elif submenu == "⏰ Sloty Czasowe":
            manage_time_slots(repos)
    
    elif menu_option == "🤖 Generator Planu":
        generate_schedule_ai(repos)
    
    elif menu_option == "📋 Podgląd i Raporty":
        if submenu == "📊 Podgląd Planów":
            view_schedules(repos)
        elif submenu == "🔍 Walidacja":
            validate_schedule(repos)
        elif submenu == "✍️ Edycja Manualna":
            manual_schedule_edit(repos)
    
    elif menu_option == "⚙️ Narzędzia":
        if submenu == "📥 Import/Eksport":
            import_export_data(repos)
        elif submenu == "✏️ Edycja Danych":
            show_edit_data_menu(repos)



def show_edit_data_menu(repos):
    """data edit menu"""
    edit_tabs = st.tabs([
        "🏢 Wydziały/Budynki", "🚪 Sale", "👥 Grupy", 
        "👨‍🏫 Prowadzący", "📖 Przedmioty", "📋 Przypisania", "⏰ Sloty"
    ])
    
    with edit_tabs[0]:
        edit_delete_departments_buildings(repos)
    with edit_tabs[1]:
        edit_delete_rooms(repos)
    with edit_tabs[2]:
        edit_delete_groups(repos)
    with edit_tabs[3]:
        edit_delete_teachers(repos)
    with edit_tabs[4]:
        edit_delete_courses(repos)
    with edit_tabs[5]:
        edit_delete_course_assignments(repos)
    with edit_tabs[6]:
        edit_time_slots(repos)



if __name__ == "__main__":
    main()
