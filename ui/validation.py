import streamlit as st
import pandas as pd
from ui.components import render_section_header
from services.validation_service import ValidationService
from app_config.constants import (
    WEEKDAY_LABELS_PL,
    WEEKDAY_OPTIONS_PL,
    WEEKDAY_PL_TO_EN,
    WEEK_PARITY_OPTIONS,
    WEEK_PARITY_LABELS_PL
)


# helper functions

def select_department(repos, label="🏢 Filtruj po wydziale:"):
    """helper for department selection - returns (dept_id, dept_name)"""
    departments = repos['departments'].get_all()
    if not departments:
        return None, None
    
    options = {"Wszystkie wydziały": None}
    options.update({f"{d[1]} - {d[2]}": d[0] for d in departments})
    
    selected = st.selectbox(label, list(options.keys()))
    dept_id = options[selected]
    
    if dept_id:
        st.info(f"📌 Filtr aktywny: **{selected}**")
    
    return dept_id, selected


def filter_assignments_by_dept(assignments, dept_id, repos):
    """filters assignments by department"""
    if not dept_id:
        return assignments
    
    filtered = []
    for a in assignments:
        ca = repos['course_assignments'].get_by_id('id', a[1])
        if ca:
            group = repos['groups'].get_by_id('id', ca[2])
            if group and group[3] == dept_id:
                filtered.append(a)
    
    return filtered


def get_room_options(repos, dept_id=None):
    """returns dict {label: room_id} for selectbox"""
    rooms = repos['rooms'].get_all()
    
    if dept_id:
        dept_buildings = [b[0] for b in repos['buildings'].get_all() if b[3] == dept_id]
        rooms = [r for r in rooms if r[1] in dept_buildings]
    
    return {f"{r[2]} - {r[3] or ''}": r[0] for r in rooms}


def get_ca_options(repos, dept_id=None):
    """returns dict {label: ca_id} for course assignments"""
    course_assignments = repos['course_assignments'].get_all()
    
    if dept_id:
        course_assignments = [
            ca for ca in course_assignments
            if repos['groups'].get_by_id('id', ca[2])[3] == dept_id
        ]
    
    options = {}
    for ca in course_assignments:
        course = repos['courses'].get_by_id('id', ca[1])
        group = repos['groups'].get_by_id('id', ca[2])
        teacher = repos['teachers'].get_by_id('id', ca[3])
        
        if all([course, group, teacher]):
            label = f"{course[2]} | {group[2]} | {teacher[1]} {teacher[2]}"
            options[label] = ca[0]
    
    return options


# validation 

def validate_schedule(repos):
    """schedule validation"""
    render_section_header("Walidacja Planu", "🔍")
    
    dept_id, dept_name = select_department(repos)
    assignments = repos['assignments'].get_all()
    
    if not assignments:
        st.warning("⚠️ Brak planu do walidacji")
        return
    
    assignments = filter_assignments_by_dept(assignments, dept_id, repos)
    
    if not assignments:
        st.warning(f"⚠️ Brak zajęć dla wybranego wydziału")
        return
    
    st.info(f"📊 Walidacja {len(assignments)} zajęć...")
    
    if st.button("🔍 Przeprowadź walidację", type="primary"):
        _run_validation(repos, assignments)


def _run_validation(repos, assignments):
    """run validation and display results"""
    try:
        validation_service = ValidationService(repos)
        report = validation_service.validate_schedule(assignments)
        
        st.markdown("### 📋 Wyniki walidacji")
        _show_validation_metrics(report)
        
        if not report['is_valid']:
            with st.expander("🔍 Szczegóły konfliktów", expanded=True):
                _display_conflicts(report['conflicts'])
        else:
            st.success("✅ Plan jest poprawny - brak konfliktów!")
            st.balloons()
    
    except Exception as e:
        st.error(f"❌ Błąd walidacji: {e}")


def _show_validation_metrics(report):
    """display validation metrics"""
    conflicts = report['conflicts']
    
    col1, col2, col3 = st.columns(3)
    
    col1.metric("❌ Konflikty nauczycieli", len(conflicts['teacher']))
    col1.metric("❌ Konflikty grup", len(conflicts['group']))
    
    col2.metric("❌ Konflikty sal", len(conflicts['room']))
    col2.metric("⚠️ Naruszenia pojemności", len(conflicts['capacity']))
    
    col3.metric("⚠️ Niedopasowanie typu sali", len(conflicts['room_type']))
    col3.metric("📊 Łącznie problemów", report['total_conflicts'])


def _display_conflicts(conflicts):
    """display conflict details"""
    conflict_labels = {
        'teacher': "👨‍🏫 Konflikty nauczycieli",
        'group': "👥 Konflikty grup",
        'room': "🚪 Konflikty sal",
        'capacity': "📊 Naruszenia pojemności",
        'room_type': "🏢 Niedopasowanie typu sali"
    }
    
    for key, label in conflict_labels.items():
        if conflicts[key]:
            st.markdown(f"**{label}:**")
            for c in conflicts[key][:10]:
                st.text(f"• {c}")
            if len(conflicts[key]) > 10:
                st.text(f"... i {len(conflicts[key]) - 10} więcej")


# manual editing 

def manual_schedule_edit(repos):
    """manual schedule editing"""
    render_section_header("Edycja Manualna Planu", "✍️")
    
    dept_id, dept_name = select_department(repos, "🏢 Filtruj edycję po wydziale:")
    assignments = repos['assignments'].get_all()
    
    if not assignments:
        st.warning("⚠️ Brak planu do edycji")
        return
    
    assignments = filter_assignments_by_dept(assignments, dept_id, repos)
    
    if not assignments:
        st.warning(f"⚠️ Brak zajęć dla wybranego wydziału")
        return
    
    st.info(f"📊 W systemie jest {len(assignments)} zajęć do edycji")
    
    mode = st.radio(
        "Wybierz operację:",
        ["📝 Edytuj zajęcia", "🗑️ Usuń zajęcia", "➕ Dodaj zajęcia"],
        horizontal=True
    )
    
    st.markdown("---")
    
    if mode == "📝 Edytuj zajęcia":
        _edit_assignment_mode(repos, dept_id)
    elif mode == "🗑️ Usuń zajęcia":
        _delete_assignment_mode(repos)
    else:
        _add_assignment_mode(repos, dept_id)


# editing - edit mode

def _edit_assignment_mode(repos, dept_id):
    """editing assignments mode"""
    st.subheader("Wybierz zajęcia do edycji")
    
    schedule = repos['assignments'].get_full_schedule()
    
    if not schedule:
        st.warning("Brak zajęć w planie")
        return
    
    assignment_options = _build_assignment_options(schedule)
    selected = st.selectbox("Wybierz zajęcia:", list(assignment_options.keys()))
    
    if not selected:
        return
    
    assignment = assignment_options[selected]
    
    st.markdown("---")
    st.markdown("### 🔧 Edytuj wybrane zajęcia")
    
    new_data = _show_assignment_edit_form(repos, assignment, dept_id)
    
    if st.button("💾 Zapisz zmiany", type="primary"):
        _save_assignment_changes(repos, assignment['id'], new_data)


def _build_assignment_options(schedule):
    """builds options for assignment selection"""
    options = {}
    for s in schedule:
        # s[8]=start_time, s[9]=end_time, s[10]=weekday, s[2]=course_name, s[13]=group_code, s[6]=room_code
        label = f"{s[10]} | {s[8]}-{s[9]} | {s[2]} | {s[13]} | {s[6]}"
        options[label] = {
            'id': s[0],
            'room_code': s[6],
            'weekday': s[10],
            'start_time': s[8],
            'end_time': s[9],
            'week_parity': s[11],
            'note': s[12]
        }
    return options


def _show_assignment_edit_form(repos, assignment, dept_id):
    """assignment editing form - returns new data"""
    col1, col2 = st.columns(2)
    
    with col1:
        # room
        room_options = get_room_options(repos, dept_id)
        new_room_id = st.selectbox("Sala:", list(room_options.keys()))
        
        # weekday
        current_day_pl = WEEKDAY_LABELS_PL.get(assignment['weekday'].lower(), 'Poniedziałek')
        current_day_idx = WEEKDAY_OPTIONS_PL.index(current_day_pl)
        
        new_day_pl = st.selectbox("Dzień:", WEEKDAY_OPTIONS_PL, index=current_day_idx)
        new_weekday = WEEKDAY_PL_TO_EN[new_day_pl] 
    
    with col2:
        # time
        new_start_time = st.time_input("Godzina rozpoczęcia:", value=assignment['start_time'])
        new_end_time = st.time_input("Godzina zakończenia:", value=assignment['end_time'])
        
        # parity
        current_parity_pl = WEEK_PARITY_LABELS_PL.get(assignment['week_parity'], 'Oba')
        parity_keys = list(WEEK_PARITY_OPTIONS.keys())
        current_parity_idx = next((i for i, k in enumerate(parity_keys) 
                                  if WEEK_PARITY_OPTIONS[k] == assignment['week_parity']), 0)
        
        new_parity_label = st.selectbox("Parzystość:", parity_keys, index=current_parity_idx)
        new_parity = WEEK_PARITY_OPTIONS[new_parity_label]
    
    new_note = st.text_area("Notatka:", value=assignment['note'] or "")
    
    return {
        'room_id': room_options[new_room_id],
        'weekday': new_weekday,
        'start_time': new_start_time,
        'end_time': new_end_time,
        'week_parity': new_parity,
        'note': new_note or None
    }


def _save_assignment_changes(repos, assignment_id, new_data):
    """save changes in assignments"""
    try:
        repos['assignments'].update('id', assignment_id, new_data)
        st.success("✅ Zajęcia zaktualizowane!")
        st.rerun()
    except Exception as e:
        st.error(f"❌ Błąd: {e}")


# editing - delete mode

def _delete_assignment_mode(repos):
    """delete assignments mode"""
    st.subheader("Usuń zajęcia z planu")
    
    schedule = repos['assignments'].get_full_schedule()
    
    if not schedule:
        st.warning("Brak zajęć w planie")
        return
    
    df = _create_schedule_dataframe(schedule)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    max_id = int(df['ID'].max())
    assignment_id = int(st.number_input(
        "Podaj ID zajęć do usunięcia:", min_value=1, max_value=max_id, step=1
    ))

    confirm = st.checkbox("✅ Potwierdź usunięcie")

    if st.button("🗑️ Usuń", type="secondary"):
        if confirm:
            _delete_assignment(repos, assignment_id)
        else:
            st.warning("Zaznacz potwierdzenie, aby usunąć zajęcia")


def _create_schedule_dataframe(schedule):
    """creates dataframe from schedule"""
    data = [{
        'ID': s[0],
        'Dzień': WEEKDAY_LABELS_PL.get(s[10], s[10]),
        'Godzina': f"{str(s[8]).rsplit(':', 1)[0]}-{str(s[9]).rsplit(':', 1)[0]}",
        'Przedmiot': s[2],
        'Grupa': s[13],
        'Sala': s[6],
        'Parzystość': s[11]
    } for s in schedule]
    
    return pd.DataFrame(data)


def _delete_assignment(repos, assignment_id):
    """delete assignments"""
    try:
        repos['assignments'].delete('id', assignment_id)
        st.success("✅ Zajęcia usunięte!")
        st.rerun()
    except Exception as e:
        st.error(f"❌ Błąd: {e}")


# editing - add mode

def _add_assignment_mode(repos, dept_id):
    """add new assignments mode"""
    st.subheader("Dodaj nowe zajęcia do planu")
    
    with st.form("add_assignment", clear_on_submit=True):
        new_assignment = _show_add_assignment_form(repos, dept_id)
        
        if st.form_submit_button("➕ Dodaj zajęcia", type="primary"):
            _save_new_assignment(repos, new_assignment)


def _show_add_assignment_form(repos, dept_id):
    """adding assignments form - returns data"""
    col1, col2 = st.columns(2)
    
    with col1:
        # course assignment
        ca_options = get_ca_options(repos, dept_id)
        if not ca_options:
            st.error("Brak przypisań przedmiotów!")
            st.stop()
        
        selected_ca = st.selectbox("Przedmiot + Grupa + Prowadzący:", list(ca_options.keys()))
        ca_id = ca_options[selected_ca]
        
        # room
        room_options = get_room_options(repos, dept_id)
        selected_room = st.selectbox("Sala:", list(room_options.keys()))
        room_id = room_options[selected_room]
        
        # weekday
        selected_day_pl = st.selectbox("Dzień:", WEEKDAY_OPTIONS_PL)
        weekday = WEEKDAY_PL_TO_EN[selected_day_pl]
    
    with col2:
        # time
        start_time = st.time_input("Godzina rozpoczęcia:")
        end_time = st.time_input("Godzina zakończenia:")
        
        # parity
        selected_parity = st.selectbox("Parzystość:", list(WEEK_PARITY_OPTIONS.keys()))
        parity = WEEK_PARITY_OPTIONS[selected_parity]
        
        note = st.text_area("Notatka (opcjonalnie):")
    
    return {
        'course_assignment_id': ca_id,
        'room_id': room_id,
        'weekday': weekday,
        'start_time': start_time,
        'end_time': end_time,
        'week_parity': parity,
        'note': note or None
    }


def _save_new_assignment(repos, assignment_data):
    """save new assignments"""
    try:
        repos['assignments'].insert(assignment_data)
        st.success("✅ Zajęcia dodane!")
        st.rerun()
    except Exception as e:
        st.error(f"❌ Błąd: {e}")
