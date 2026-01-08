"""
edit and delete data
"""
import streamlit as st
import json
from ui.components import render_section_header
from ui.form_helpers import FormHelper, SelectBoxBuilder, EditFormHelper
from app_config.constants import (
    ROOM_TYPES, 
    ROOM_TYPE_LABELS_PL, 
    COURSE_TYPES, 
    COURSE_TYPE_LABELS_PL
)


# helper functions

def _render_entity_list(repos, repo_name, columns, label_func, 
                       edit_func, icon="📄"):
    """generic renderer for entity list with editing"""
    try:
        items = repos[repo_name].get_all()
    except Exception as e:
        st.error(f"❌ {str(e)}")
        return
    
    if not items:
        st.info("ℹ️ no data in system")
        return
    
    st.info(f"📊 found {len(items)} records")
    
    for item in items:
        label = label_func(item, repos)
        with st.expander(f"{icon} {label}", expanded=False):
            edit_func(item, repos)


def _get_selectbox_value(options, current_id):
    """returns currently selected key in selectbox"""
    return next(
        (k for k, v in options.items() if v == current_id),
        list(options.keys())[0] if options else None
    )


# departments & buildings

def edit_delete_departments_buildings(repos):
    """edit departments and buildings"""
    render_section_header("Edycja Wydziałów i Budynków", "✏️")
    
    tab1, tab2 = st.tabs(["🏢 Wydziały", "🏛️ Budynki"])
    
    with tab1:
        st.subheader("Edytuj lub usuń wydział")
        _render_entity_list(
            repos, 'departments', ['ID', 'Kod', 'Nazwa'],
            lambda d, r: f"{d[1]} - {d[2]}",
            _edit_department_form,
            "📁"
        )
    
    with tab2:
        st.subheader("Edytuj lub usuń budynek")
        departments = repos['departments'].get_all()
        if not departments:
            st.warning("⚠️ Najpierw dodaj wydziały!")
            return
        
        _render_entity_list(
            repos, 'buildings', ['ID', 'Nazwa', 'Adres', 'Wydział'],
            lambda b, r: f"{b[1]} ({r['departments'].get_by_id('id', b[3])[2] if r['departments'].get_by_id('id', b[3]) else '?'})",
            _edit_building_form,
            "🏛️"
        )


def _edit_department_form(dept, repos):
    """department edit form"""
    with st.form(f"edit_dept_{dept[0]}"):
        new_code = st.text_input("Kod wydziału:", value=dept[1])
        new_name = st.text_input("Nazwa wydziału:", value=dept[2])
        
        EditFormHelper.render_edit_delete_buttons(
            repos['departments'], dept[0],
            {'code': new_code, 'name': new_name},
            'dept_edit_success', dept[2]
        )


def _edit_building_form(building, repos):
    """building edit form"""
    departments = repos['departments'].get_all()
    
    with st.form(f"edit_building_{building[0]}"):
        new_name = st.text_input("Nazwa budynku:", value=building[1])
        new_address = st.text_input("Adres:", value=building[2] or "")
        
        dept_options = {f"{d[1]} - {d[2]}": d[0] for d in departments}
        current_dept = _get_selectbox_value(dept_options, building[3])
        selected_dept = st.selectbox("Wydział:", list(dept_options.keys()),
                                    index=list(dept_options.keys()).index(current_dept))
        
        EditFormHelper.render_edit_delete_buttons(
            repos['buildings'], building[0],
            {
                'name': new_name,
                'address': new_address if new_address else None,
                'department_id': dept_options[selected_dept]
            },
            'building_edit_success', building[1]
        )


# rooms

def edit_delete_rooms(repos):
    """edit rooms"""
    render_section_header("Edycja Sal", "🚪")
    
    buildings = repos['buildings'].get_all()
    if not buildings:
        st.warning("⚠️ Najpierw dodaj budynki!")
        return
    
    try:
        rooms = repos['rooms'].get_all()
    except Exception as e:
        st.error(f"❌ {str(e)}")
        return
    
    if not rooms:
        st.info("ℹ️ no rooms in system")
        return
    
    st.info(f"📊 found {len(rooms)} rooms")
    
    # filtering
    search = st.text_input("🔍 Szukaj sali (kod lub nazwa):")
    filtered_rooms = [
        r for r in rooms 
        if not search or search.lower() in r[2].lower() or 
        (r[3] and search.lower() in r[3].lower())
    ]
    
    for room in filtered_rooms:
        building = repos['buildings'].get_by_id('id', room[1])
        building_name = building[1] if building else "?"
        room_type_pl = ROOM_TYPE_LABELS_PL.get(room[5], room[5])
        
        label = f"{room[2]} - {room[3] or 'Brak nazwy'} ({building_name}) [{room_type_pl}]"
        
        with st.expander(f"🚪 {label}", expanded=False):
            _edit_room_form(room, repos, buildings)


def _edit_room_form(room, repos, buildings):
    """room edit form"""
    with st.form(f"edit_room_{room[0]}"):
        col1, col2 = st.columns(2)
        
        with col1:
            building_options = {b[1]: b[0] for b in buildings}
            current_building = _get_selectbox_value(building_options, room[1])
            selected_building = st.selectbox(
                "Budynek:", list(building_options.keys()),
                index=list(building_options.keys()).index(current_building)
            )
            
            new_code = st.text_input("Kod sali:", value=room[2])
            new_name = st.text_input("Nazwa sali:", value=room[3] or "")
        
        with col2:
            new_capacity = st.number_input("Pojemność:", min_value=1, value=room[4])
            
            room_type_options = {ROOM_TYPE_LABELS_PL[rt]: rt for rt in ROOM_TYPES}
            current_type_pl = ROOM_TYPE_LABELS_PL.get(room[5], room[5])
            current_type_idx = list(room_type_options.keys()).index(current_type_pl) if current_type_pl in room_type_options else 0
            
            selected_room_type_pl = st.selectbox("Typ sali:", list(room_type_options.keys()), index=current_type_idx)
            new_type = room_type_options[selected_room_type_pl]
            
            new_note = st.text_area("Notatki:", value=room[6] or "")
        
        EditFormHelper.render_edit_delete_buttons(
            repos['rooms'], room[0],
            {
                'building_id': building_options[selected_building],
                'code': new_code,
                'name': new_name if new_name else None,
                'capacity': new_capacity,
                'type': new_type,
                'note': new_note if new_note else None,
                'equipment': json.dumps([]),
                'accessibility': json.dumps({})
            },
            'room_edit_success', room[2]
        )


# groups

def edit_delete_groups(repos):
    """edit groups"""
    render_section_header("Edycja Grup", "👥")
    
    departments = repos['departments'].get_all()
    if not departments:
        st.warning("⚠️ Najpierw dodaj wydziały!")
        return
    
    _render_entity_list(
        repos, 'groups', ['ID', 'Kod', 'Nazwa'],
        lambda g, r: f"{g[1]} - {g[2]} ({r['departments'].get_by_id('id', g[3])[2] if r['departments'].get_by_id('id', g[3]) else '?'})",
        _edit_group_form,
        "👥"
    )


def _edit_group_form(group, repos):
    """group edit form"""
    departments = repos['departments'].get_all()
    groups = repos['groups'].get_all()
    
    with st.form(f"edit_group_{group[0]}"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_code = st.text_input("Kod grupy:", value=group[1])
            new_name = st.text_input("Nazwa grupy:", value=group[2])
            
            dept_options = {f"{d[1]} - {d[2]}": d[0] for d in departments}
            current_dept = _get_selectbox_value(dept_options, group[3])
            selected_dept = st.selectbox("Wydział:", list(dept_options.keys()),
                                        index=list(dept_options.keys()).index(current_dept))
        
        with col2:
            new_students = st.number_input("Liczba studentów:", min_value=1, value=group[4])
            
            parent_options = {"Brak (grupa niezależna)": None}
            parent_options.update({f"{g[1]} - {g[2]}": g[0] for g in groups if g[0] != group[0]})
            
            current_parent = _get_selectbox_value(parent_options, group[6]) if group[6] else "Brak (grupa niezależna)"
            selected_parent = st.selectbox("Grupa nadrzędna:", list(parent_options.keys()),
                                          index=list(parent_options.keys()).index(current_parent))
        
        EditFormHelper.render_edit_delete_buttons(
            repos['groups'], group[0],
            {
                'code': new_code,
                'name': new_name,
                'department_id': dept_options[selected_dept],
                'students_count': new_students,
                'accessibility_requirements': json.dumps({}),
                'parent_group_id': parent_options[selected_parent]
            },
            'group_edit_success', group[2]
        )


# teachers

def edit_delete_teachers(repos):
    """edit teachers"""
    render_section_header("Edycja Prowadzących", "👨‍🏫")
    
    departments = repos['departments'].get_all()
    if not departments:
        st.warning("⚠️ Najpierw dodaj wydziały!")
        return
    
    _render_entity_list(
        repos, 'teachers', ['ID', 'Imię', 'Nazwisko'],
        lambda t, r: f"{t[1]} {t[2]} ({r['departments'].get_by_id('id', t[3])[2] if r['departments'].get_by_id('id', t[3]) else '?'})",
        _edit_teacher_form,
        "👨‍🏫"
    )


def _edit_teacher_form(teacher, repos):
    """teacher edit form"""
    departments = repos['departments'].get_all()
    
    with st.form(f"edit_teacher_{teacher[0]}"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_first_name = st.text_input("Imię:", value=teacher[1])
            new_last_name = st.text_input("Nazwisko:", value=teacher[2])
        
        with col2:
            dept_options = {f"{d[1]} - {d[2]}": d[0] for d in departments}
            current_dept = _get_selectbox_value(dept_options, teacher[3])
            selected_dept = st.selectbox("Wydział:", list(dept_options.keys()),
                                        index=list(dept_options.keys()).index(current_dept))
        
        EditFormHelper.render_edit_delete_buttons(
            repos['teachers'], teacher[0],
            {
                'first_name': new_first_name,
                'last_name': new_last_name,
                'department_id': dept_options[selected_dept],
                'accessibility': json.dumps({})
            },
            'teacher_edit_success', f"{teacher[1]} {teacher[2]}"
        )


# courses

def edit_delete_courses(repos):
    """edit courses"""
    render_section_header("Edycja Przedmiotów", "📖")
    
    departments = repos['departments'].get_all()
    if not departments:
        st.warning("⚠️ Najpierw dodaj wydziały!")
        return
    
    try:
        courses = repos['courses'].get_all()
    except Exception as e:
        st.error(f"❌ {str(e)}")
        return
    
    if not courses:
        st.info("ℹ️ no courses in system")
        return
    
    st.info(f"📊 found {len(courses)} courses")
    
    search = st.text_input("🔍 Szukaj przedmiotu:")
    filtered = [c for c in courses if not search or search.lower() in c[1].lower() or search.lower() in c[2].lower()]
    
    for course in filtered:
        dept = repos['departments'].get_by_id('id', course[3])
        dept_name = dept[2] if dept else "?"
        course_type_pl = COURSE_TYPE_LABELS_PL.get(course[4], course[4])
        
        with st.expander(f"📖 {course[1]} - {course[2]} ({dept_name}) [{course_type_pl}]", expanded=False):
            _edit_course_form(course, repos, departments)


def _edit_course_form(course, repos, departments):
    """course edit form"""
    with st.form(f"edit_course_{course[0]}"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_code = st.text_input("Kod przedmiotu:", value=course[1])
            new_name = st.text_input("Nazwa przedmiotu:", value=course[2])
            
            dept_options = {f"{d[1]} - {d[2]}": d[0] for d in departments}
            current_dept = _get_selectbox_value(dept_options, course[3])
            selected_dept = st.selectbox("Wydział:", list(dept_options.keys()),
                                        index=list(dept_options.keys()).index(current_dept))
        
        with col2:
            course_type_options = {COURSE_TYPE_LABELS_PL[ct]: ct for ct in COURSE_TYPES}
            current_type_pl = COURSE_TYPE_LABELS_PL.get(course[4], course[4])
            current_type_idx = list(course_type_options.keys()).index(current_type_pl) if current_type_pl in course_type_options else 0
            
            selected_course_type_pl = st.selectbox("Typ zajęć:", list(course_type_options.keys()), index=current_type_idx)
            new_type = course_type_options[selected_course_type_pl]
            
            new_hours = st.number_input("Godzin w semestrze:", min_value=1, value=course[5])
        
        EditFormHelper.render_edit_delete_buttons(
            repos['courses'], course[0],
            {
                'code': new_code,
                'name': new_name,
                'department_id': dept_options[selected_dept],
                'type': new_type,
                'hours_per_semester': new_hours
            },
            'course_edit_success', course[2]
        )


# course assignments

def edit_delete_course_assignments(repos):
    """edit assignments"""
    render_section_header("Edycja Przypisań", "📋")
    
    try:
        assignments = repos['course_assignments'].get_all()
        courses = repos['courses'].get_all()
        groups = repos['groups'].get_all()
        teachers = repos['teachers'].get_all()
    except Exception as e:
        st.error(f"❌ {str(e)}")
        return
    
    if not all([assignments, courses, groups, teachers]):
        st.info("ℹ️ no data in system")
        return
    
    st.info(f"📊 found {len(assignments)} assignments")
    
    for assignment in assignments:
        course = repos['courses'].get_by_id('id', assignment[1])
        group = repos['groups'].get_by_id('id', assignment[2])
        teacher = repos['teachers'].get_by_id('id', assignment[3])
        
        course_type_pl = COURSE_TYPE_LABELS_PL.get(course[4], course[4]) if course else '?'
        label = f"{course[2] if course else '?'} ({course_type_pl}) | {group[2] if group else '?'} | {teacher[1]} {teacher[2] if teacher else '?'}"
        
        with st.expander(f"📋 {label}", expanded=False):
            _edit_assignment_form(assignment, repos, courses, groups, teachers)


def _edit_assignment_form(assignment, repos, courses, groups, teachers):
    """assignment edit form"""
    with st.form(f"edit_ca_{assignment[0]}"):
        col1, col2 = st.columns(2)
        
        with col1:
            # course
            course_options = {
                f"{c[1]} - {c[2]} ({COURSE_TYPE_LABELS_PL.get(c[4], c[4])})": c[0]
                for c in courses
            }
            current_course = _get_selectbox_value(course_options, assignment[1])
            selected_course = st.selectbox("Przedmiot:", list(course_options.keys()),
                                          index=list(course_options.keys()).index(current_course))
            
            # group
            group_options = {f"{g[1]} - {g[2]}": g[0] for g in groups}
            current_group = _get_selectbox_value(group_options, assignment[2])
            selected_group = st.selectbox("Grupa:", list(group_options.keys()),
                                         index=list(group_options.keys()).index(current_group))
        
        with col2:
            # teacher
            teacher_options = {f"{t[1]} {t[2]}": t[0] for t in teachers}
            current_teacher = _get_selectbox_value(teacher_options, assignment[3])
            selected_teacher = st.selectbox("Prowadzący:", list(teacher_options.keys()),
                                           index=list(teacher_options.keys()).index(current_teacher))
            
            new_semester = st.text_input("Semestr:", value=assignment[4])
        
        new_note = st.text_area("Notatki:", value=assignment[5] or "")
        
        EditFormHelper.render_edit_delete_buttons(
            repos['course_assignments'], assignment[0],
            {
                'course_id': course_options[selected_course],
                'group_id': group_options[selected_group],
                'teacher_id': teacher_options[selected_teacher],
                'semester': new_semester,
                'note': new_note if new_note else None
            },
            'assignment_edit_success', 'assignment'
        )


# time slots

def edit_time_slots(repos):
    """edit time slots"""
    render_section_header("Edycja Slotów Czasowych", "⏰")
    
    _render_entity_list(
        repos, 'time_slots', ['ID', 'Start', 'End', 'Order'],
        lambda s, r: f"slot {s[3]}: {s[1]} - {s[2]}",
        _edit_timeslot_form,
        "⏰"
    )


def _edit_timeslot_form(slot, repos):
    """time slot edit form"""
    with st.form(f"edit_slot_{slot[0]}"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            new_start = st.time_input("Godzina rozpoczęcia:", value=slot[1])
        
        with col2:
            new_end = st.time_input("Godzina zakończenia:", value=slot[2])
        
        with col3:
            new_order = st.number_input("Numer slotu:", min_value=1, value=slot[3])
        
        EditFormHelper.render_edit_delete_buttons(
            repos['time_slots'], slot[0],
            {
                'start_time': new_start,
                'end_time': new_end,
                'slot_order': new_order
            },
            'timeslot_edit_success', f"slot {slot[3]}"
        )
