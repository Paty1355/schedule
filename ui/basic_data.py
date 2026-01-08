"""
managing basic
"""
import streamlit as st
import json
from ui.components import render_section_header
from ui.form_helpers import FormHelper, SelectBoxBuilder
from services.data_service import DataTransformService
from app_config.constants import ROOM_TYPES, ROOM_TYPE_LABELS_PL


def manage_departments_buildings(repos):
    """manage departments and buildings"""
    render_section_header("Wydziały i Budynki", "🏢")
    
    tab1, tab2 = st.tabs(["📚 Wydziały", "🏛️ Budynki"])
    
    with tab1:
        _manage_departments(repos)
    
    with tab2:
        _manage_buildings(repos)


def _manage_departments(repos):
    """manage departments"""
    st.subheader("Dodaj nowy wydział")
    
    FormHelper.show_success_message('dept_success')
    
    with st.form("add_department", clear_on_submit=True):
        code = st.text_input("Kod wydziału (np. WI)", max_chars=20)
        name = st.text_input("Nazwa wydziału")
        
        if st.form_submit_button("➕ Dodaj wydział", type="primary"):
            if code and name:
                FormHelper.safe_insert(
                    repos['departments'],
                    {'code': code, 'name': name},
                    'dept_success',
                    f"✅ Dodano wydział: {name}"
                )
            else:
                st.warning("⚠️ Wypełnij wszystkie pola!")
    
    st.markdown("---")
    st.subheader("Lista wydziałów")
    
    FormHelper.render_data_table(
        repos['departments'],
        columns=["ID", "Kod", "Nazwa"]
    )


def _manage_buildings(repos):
    """manage buildings"""
    st.subheader("Dodaj nowy budynek")
    
    selector = SelectBoxBuilder(repos)
    departments = repos['departments'].get_all()
    
    if not departments:
        st.warning("⚠️ Najpierw dodaj wydział!")
        return
    
    FormHelper.show_success_message('building_success')
    
    with st.form("add_building", clear_on_submit=True):
        name = st.text_input("Nazwa budynku")
        address = st.text_input("Adres")
        dept_id = selector.department_selector()
        
        if st.form_submit_button("➕ Dodaj budynek", type="primary"):
            if name and dept_id:
                FormHelper.safe_insert(
                    repos['buildings'],
                    {
                        'name': name,
                        'address': address if address else None,
                        'department_id': dept_id
                    },
                    'building_success',
                    f"✅ Dodano budynek: {name}"
                )
            else:
                st.warning("⚠️ Podaj nazwę budynku!")
    
    st.markdown("---")
    st.subheader("Lista budynków")
    
    data_service = DataTransformService(repos)
    FormHelper.render_data_table(
        repos['buildings'],
        columns=["ID", "Nazwa", "Adres", "Wydział"],
        data_transformer=data_service.transform_building
    )


def manage_rooms(repos):
    """manage rooms"""
    render_section_header("Sale Wykładowe", "🚪")
    
    st.subheader("Dodaj nową salę")
    
    buildings = repos['buildings'].get_all()
    if not buildings:
        st.warning("⚠️ Najpierw dodaj budynek!")
        return
    
    FormHelper.show_success_message('room_success')
    
    with st.form("add_room", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            selector = SelectBoxBuilder(repos)
            building_id = selector.building_selector()
            code = st.text_input("Kod sali (np. A101)")
            name = st.text_input("Nazwa sali (opcjonalnie)")
        
        with col2:
            capacity = st.number_input("Pojemność", min_value=1, value=30)
            room_type_options = {
                ROOM_TYPE_LABELS_PL[rt]: rt for rt in ROOM_TYPES
            }
            selected_type_pl = st.selectbox("Typ sali", list(room_type_options.keys()))
            room_type = room_type_options[selected_type_pl]
        
        note = st.text_area("Notatki (opcjonalnie)")
        
        if st.form_submit_button("➕ Dodaj salę", type="primary"):
            if code and building_id:
                FormHelper.safe_insert(
                    repos['rooms'],
                    {
                        'building_id': building_id,
                        'code': code,
                        'name': name if name else None,
                        'capacity': capacity,
                        'type': room_type,
                        'note': note if note else None,
                        'equipment': json.dumps([]),
                        'accessibility': json.dumps({})
                    },
                    'room_success',
                    f"✅ Dodano salę: {code}"
                )
            else:
                st.warning("⚠️ Podaj kod sali!")
    
    st.markdown("---")
    st.subheader("Lista sal")
    
    data_service = DataTransformService(repos)
    FormHelper.render_data_table(
        repos['rooms'],
        columns=["ID", "Kod", "Nazwa", "Budynek", "Pojemność", "Typ", "Notatki"],
        data_transformer=data_service.transform_room
    )


def manage_groups(repos):
    """manage student groups"""
    render_section_header("Grupy Studenckie", "👥")
    
    st.subheader("Dodaj nową grupę")
    
    departments = repos['departments'].get_all()
    if not departments:
        st.warning("⚠️ Najpierw dodaj wydział!")
        return
    
    FormHelper.show_success_message('group_success')
    
    with st.form("add_group", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            code = st.text_input("Kod grupy (np. INF-I-1)")
            name = st.text_input("Nazwa grupy")
            selector = SelectBoxBuilder(repos)
            dept_id = selector.department_selector()
        
        with col2:
            students_count = st.number_input("Liczba studentów", min_value=1, value=30)
            parent_id = selector.group_selector(
                label="Grupa nadrzędna (opcjonalnie)",
                include_none=True
            )
        
        if st.form_submit_button("➕ Dodaj grupę", type="primary"):
            if code and name and dept_id:
                FormHelper.safe_insert(
                    repos['groups'],
                    {
                        'code': code,
                        'name': name,
                        'department_id': dept_id,
                        'students_count': students_count,
                        'accessibility_requirements': json.dumps({}),
                        'parent_group_id': parent_id
                    },
                    'group_success',
                    f"✅ Dodano grupę: {name}"
                )
            else:
                st.warning("⚠️ Wypełnij kod i nazwę grupy!")
    
    st.markdown("---")
    st.subheader("Lista grup")
    
    data_service = DataTransformService(repos)
    FormHelper.render_data_table(
        repos['groups'],
        columns=["ID", "Kod", "Nazwa", "Wydział", "Studenci", "Grupa nadrzędna"],
        data_transformer=data_service.transform_group
    )


def manage_teachers(repos):
    """manage teachers"""
    render_section_header("Prowadzący", "👨‍🏫")
    
    st.subheader("Dodaj nowego prowadzącego")
    
    departments = repos['departments'].get_all()
    if not departments:
        st.warning("⚠️ Najpierw dodaj wydział!")
        return
    
    FormHelper.show_success_message('teacher_success')
    
    with st.form("add_teacher", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("Imię")
            last_name = st.text_input("Nazwisko")
        
        with col2:
            selector = SelectBoxBuilder(repos)
            dept_id = selector.department_selector()
        
        if st.form_submit_button("➕ Dodaj prowadzącego", type="primary"):
            if first_name and last_name and dept_id:
                FormHelper.safe_insert(
                    repos['teachers'],
                    {
                        'first_name': first_name,
                        'last_name': last_name,
                        'department_id': dept_id,
                        'accessibility': json.dumps({})
                    },
                    'teacher_success',
                    f"✅ Dodano prowadzącego: {first_name} {last_name}"
                )
            else:
                st.warning("⚠️ Wypełnij imię i nazwisko!")
    
    st.markdown("---")
    st.subheader("Lista prowadzących")
    
    data_service = DataTransformService(repos)
    FormHelper.render_data_table(
        repos['teachers'],
        columns=["ID", "Imię", "Nazwisko", "Wydział"],
        data_transformer=data_service.transform_teacher
    )


def manage_unavailabilities(repos):
    """manage unavailabilities"""
    render_section_header("Niedostępności", "🚫")
    
    tab1, tab2 = st.tabs(["👨‍🏫 Prowadzący", "👥 Grupy"])
    
    with tab1:
        _manage_teacher_unavailabilities(repos)
    
    with tab2:
        _manage_group_unavailabilities(repos)


def _manage_teacher_unavailabilities(repos):
    """teacher unavailabilities"""
    st.subheader("Dodaj niedostępność prowadzącego")
    
    teachers = repos['teachers'].get_all()
    if not teachers:
        st.warning("⚠️ Najpierw dodaj prowadzących!")
        return
    
    FormHelper.show_success_message('teacher_unavail_success')
    
    with st.form("add_teacher_unavail", clear_on_submit=True):
        selector = SelectBoxBuilder(repos)
        teacher_id = selector.teacher_selector()
        
        col1, col2 = st.columns(2)
        with col1:
            weekday = selector.weekday_selector()
            start_time = st.time_input("Od godziny")
        
        with col2:
            end_time = st.time_input("Do godziny")
            reason = st.text_input("Powód (opcjonalnie)")
        
        if st.form_submit_button("➕ Dodaj niedostępność"):
            if teacher_id:
                FormHelper.safe_insert(
                    repos['teacher_unavailabilities'],
                    {
                        'teacher_id': teacher_id,
                        'weekday': weekday,
                        'start_time': start_time,
                        'end_time': end_time,
                        'reason': reason if reason else None
                    },
                    'teacher_unavail_success',
                    "✅ Dodano niedostępność"
                )
    
    st.markdown("---")
    
    data_service = DataTransformService(repos)
    FormHelper.render_data_table(
        repos['teacher_unavailabilities'],
        columns=["ID", "Prowadzący", "Dzień", "Od", "Do", "Powód"],
        data_transformer=data_service.transform_teacher_unavailability
    )


def _manage_group_unavailabilities(repos):
    """group unavailabilities"""
    st.subheader("Dodaj niedostępność grupy")
    
    groups = repos['groups'].get_all()
    if not groups:
        st.warning("⚠️ Najpierw dodaj grupy!")
        return
    
    FormHelper.show_success_message('group_unavail_success')
    
    with st.form("add_group_unavail", clear_on_submit=True):
        selector = SelectBoxBuilder(repos)
        group_id = selector.group_selector()
        
        col1, col2 = st.columns(2)
        with col1:
            weekday = selector.weekday_selector(key="group_weekday")
            start_time = st.time_input("Od godziny", key="group_start")
        
        with col2:
            end_time = st.time_input("Do godziny", key="group_end")
            reason = st.text_input("Powód (opcjonalnie)", key="group_reason")
        
        if st.form_submit_button("➕ Dodaj niedostępność"):
            if group_id:
                FormHelper.safe_insert(
                    repos['group_unavailabilities'],
                    {
                        'group_id': group_id,
                        'weekday': weekday,
                        'start_time': start_time,
                        'end_time': end_time,
                        'reason': reason if reason else None
                    },
                    'group_unavail_success',
                    "✅ Dodano niedostępność"
                )
    
    st.markdown("---")
    
    data_service = DataTransformService(repos)
    FormHelper.render_data_table(
        repos['group_unavailabilities'],
        columns=["ID", "Grupa", "Dzień", "Od", "Do", "Powód"],
        data_transformer=data_service.transform_group_unavailability
    )
