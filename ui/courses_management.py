"""
course and class management
"""
import streamlit as st
import json
from ui.components import render_section_header
from ui.form_helpers import FormHelper, SelectBoxBuilder
from app_config.constants import COURSE_TYPES, COURSE_TYPE_LABELS_PL


def manage_courses(repos):
    """manage courses"""
    render_section_header("Przedmioty", "📚")
    
    st.subheader("Dodaj nowy przedmiot")
    
    departments = repos['departments'].get_all()
    if not departments:
        st.warning("⚠️ Najpierw dodaj wydział!")
        return
    
    FormHelper.show_success_message('course_success')
    
    with st.form("add_course", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            code = st.text_input("Kod przedmiotu (np. INF-101)")
            name = st.text_input("Nazwa przedmiotu")
            selector = SelectBoxBuilder(repos)
            dept_id = selector.department_selector()
        
        with col2:
            course_type_options = {
                COURSE_TYPE_LABELS_PL[ct]: ct for ct in COURSE_TYPES
            }
            selected_type_pl = st.selectbox("Typ zajęć", list(course_type_options.keys()))
            course_type = course_type_options[selected_type_pl]
            hours = st.number_input("Godzin w semestrze", min_value=1, value=30)
        
        if st.form_submit_button("➕ Dodaj przedmiot", type="primary"):
            if code and name and dept_id:
                FormHelper.safe_insert(
                    repos['courses'],
                    {
                        'code': code,
                        'name': name,
                        'department_id': dept_id,
                        'type': course_type,
                        'hours_per_semester': hours
                    },
                    'course_success',
                    f"✅ Dodano przedmiot: {name}"
                )
            else:
                st.warning("⚠️ Wypełnij kod i nazwę przedmiotu!")
    
    st.markdown("---")
    st.subheader("Lista przedmiotów")
    
    def transform_course(c):
        dept = repos['departments'].get_by_id('id', c[3])
        return {
            'ID': c[0],
            'Kod': c[1],
            'Nazwa': c[2],
            'Wydział': dept[2] if dept else '-',
            'Typ': COURSE_TYPE_LABELS_PL.get(c[4], c[4]),
            'Godzin': c[5]
        }
    
    FormHelper.render_data_table(
        repos['courses'],
        columns=["ID", "Kod", "Nazwa", "Wydział", "Typ", "Godzin"],
        data_transformer=transform_course
    )


def manage_course_assignments(repos):
    """manage course assignments"""
    render_section_header("Przypisania Przedmiotów", "🔗")
    
    st.subheader("Dodaj nowe przypisanie")
    
    courses = repos['courses'].get_all()
    groups = repos['groups'].get_all()
    teachers = repos['teachers'].get_all()
    
    if not courses or not groups or not teachers:
        st.warning("⚠️ Najpierw dodaj przedmioty, grupy i prowadzących!")
        return
    
    FormHelper.show_success_message('assignment_success')
    
    with st.form("add_assignment", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            selector = SelectBoxBuilder(repos)
            course_id = selector.course_selector()
            group_id = selector.group_selector()
        
        with col2:
            teacher_id = selector.teacher_selector()
            semester = st.text_input("Semestr (np. 2024Z)", value="2024Z")
        
        note = st.text_area("Notatka (opcjonalnie)")
        
        if st.form_submit_button("➕ Dodaj przypisanie", type="primary"):
            if course_id and group_id and teacher_id:
                FormHelper.safe_insert(
                    repos['course_assignments'],
                    {
                        'course_id': course_id,
                        'group_id': group_id,
                        'teacher_id': teacher_id,
                        'semester': semester,
                        'note': note if note else None
                    },
                    'assignment_success',
                    "✅ Dodano przypisanie"
                )
            else:
                st.warning("⚠️ Wypełnij wszystkie wymagane pola!")
    
    st.markdown("---")
    st.subheader("Lista przypisań")
    
    def transform_assignment(a):
        course = repos['courses'].get_by_id('id', a[1])
        group = repos['groups'].get_by_id('id', a[2])
        teacher = repos['teachers'].get_by_id('id', a[3])
        
        course_type_pl = COURSE_TYPE_LABELS_PL.get(course[4], course[4]) if course else '-'
        
        return {
            'ID': a[0],
            'Przedmiot': f"{course[2]} ({course_type_pl})" if course else '-',
            'Grupa': f"{group[1]} - {group[2]}" if group else '-',
            'Prowadzący': f"{teacher[1]} {teacher[2]}" if teacher else '-',
            'Semestr': a[4],
            'Notatka': a[5] or '-'
        }
    
    FormHelper.render_data_table(
        repos['course_assignments'],
        columns=["ID", "Przedmiot", "Grupa", "Prowadzący", "Semestr", "Notatka"],
        data_transformer=transform_assignment
    )


def manage_time_slots(repos):
    """manage time slots"""
    render_section_header("Sloty Czasowe", "⏰")
    
    st.subheader("Dodaj nowy slot czasowy")
    
    FormHelper.show_success_message('timeslot_success')
    
    with st.form("add_timeslot", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            start_time = st.time_input("Godzina rozpoczęcia")
            slot_order = st.number_input("Kolejność slotu", min_value=1, value=1)
        
        with col2:
            end_time = st.time_input("Godzina zakończenia")
        
        if st.form_submit_button("➕ Dodaj slot", type="primary"):
            if start_time and end_time:
                if end_time <= start_time:
                    st.error("⚠️ Godzina zakończenia musi być późniejsza niż rozpoczęcia!")
                else:
                    FormHelper.safe_insert(
                        repos['time_slots'],
                        {
                            'start_time': start_time,
                            'end_time': end_time,
                            'slot_order': slot_order
                        },
                        'timeslot_success',
                        f"✅ Dodano slot: {start_time} - {end_time}"
                    )
            else:
                st.warning("⚠️ Wypełnij godziny!")
    
    st.markdown("---")
    st.subheader("Lista slotów czasowych")
    
    def transform_timeslot(ts):
        return {
            'ID': ts[0],
            'Początek': str(ts[1]),
            'Koniec': str(ts[2]),
            'Kolejność': ts[3],
            'Czas trwania (min)': ts[4] if len(ts) > 4 else '-'
        }
    
    FormHelper.render_data_table(
        repos['time_slots'],
        columns=["ID", "Początek", "Koniec", "Kolejność", "Czas trwania (min)"],
        data_transformer=transform_timeslot
    )
