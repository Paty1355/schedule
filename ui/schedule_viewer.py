import streamlit as st
import pandas as pd
from ui.components import render_section_header
from services.schedule_view_service import ScheduleViewService
from app_config.constants import (
    WEEKDAY_LABELS_PL, 
    WEEK_PARITY_LABELS_PL,
    COURSE_TYPE_LABELS_PL,
    ROOM_TYPE_LABELS_PL
)



def view_schedules(repos):
    """preview of schedules"""
    render_section_header("Podgląd Planów Zajęć", "📅")
    
    # department filter
    departments = repos['departments'].get_all()
    selected_dept_id = None
    
    if departments:
        dept_options = {"Wszystkie wydziały": None}
        dept_options.update({f"{d[1]} - {d[2]}": d[0] for d in departments})
        selected_dept_key = st.selectbox("🏢 Filtruj po wydziale:", options=list(dept_options.keys()))
        selected_dept_id = dept_options[selected_dept_key]
        
        if selected_dept_id:
            st.info(f"📌 Wyświetlane są tylko dane dla wydziału: **{selected_dept_key}**")
    else:
        selected_dept_id = None
    
    # view type selection
    view_type = st.radio(
        "Wybierz widok:",
        ["Pełny plan", "Plan dla grupy", "Plan dla prowadzącego", "Plan dla sali"],
        horizontal=True
    )
    
    # use service
    schedule_service = ScheduleViewService(repos)
    
    if view_type == "Pełny plan":
        _display_full_schedule(schedule_service, selected_dept_id)
    
    elif view_type == "Plan dla grupy":
        _display_group_schedule(repos, schedule_service, selected_dept_id)
    
    elif view_type == "Plan dla prowadzącego":
        _display_teacher_schedule(repos, schedule_service, selected_dept_id)
    
    elif view_type == "Plan dla sali":
        _display_room_schedule(repos, schedule_service, selected_dept_id)



def _display_full_schedule(schedule_service: ScheduleViewService, dept_id: int = None):
    """displays full schedule"""
    schedule = schedule_service.get_full_schedule(department_id=dept_id)
    
    if schedule:
        st.success(f"📊 Łącznie {len(schedule)} zajęć w systemie")
        
        df_data = []
        for s in schedule:
            df_data.append({
                'Dzień': s['weekday_pl'],
                'Godzina': s['timeslot'],
                'Przedmiot': s['course_name'],
                'Typ': COURSE_TYPE_LABELS_PL.get(s['course_type'], s['course_type']),
                'Grupa': s['group_code'],
                'Prowadzący': s['teacher_name'],
                'Sala': s['room_code'],
                'Parzystość': WEEK_PARITY_LABELS_PL.get(s['parity'], s['parity']),
                'Notatki': s['note'] if s['note'] else '-'
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # download button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Pobierz pełny plan jako CSV",
            data=csv,
            file_name="pelny_plan_zajec.csv",
            mime="text/csv"
        )
    else:
        st.warning("⚠️ Brak zajęć w systemie")


def _display_group_schedule(repos, schedule_service: ScheduleViewService, dept_id: int = None):
    """displays schedule for group"""
    groups = repos['groups'].get_all()
    
    if dept_id:
        groups = [g for g in groups if g[3] == dept_id]
    
    if not groups:
        st.warning("⚠️ Brak grup w systemie")
        return
    
    group_options = {f"{g[1]} - {g[2]}": g[0] for g in groups}
    selected_group_key = st.selectbox("👥 Wybierz grupę:", list(group_options.keys()))
    group_id = group_options[selected_group_key]
    
    schedule = schedule_service.get_group_schedule(group_id)
    
    if schedule:
        st.success(f"📅 Znaleziono {len(schedule)} zajęć")
        
        df_data = []
        for s in schedule:
            df_data.append({
                'Dzień': s['weekday_pl'],
                'Godzina': s['timeslot'],
                'Przedmiot': s['course_name'],
                'Typ': COURSE_TYPE_LABELS_PL.get(s['course_type'], s['course_type']),
                'Prowadzący': s['teacher_name'],
                'Sala': s['room_code'],
                'Źródło': '📢 Wykład wspólny' if s['is_from_parent'] else '👥 Zajęcia grupy',
                'Parzystość': WEEK_PARITY_LABELS_PL.get(s['parity'], s['parity']),
                'Notatki': s['note'] if s['note'] else '-'
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("""
        **Legenda:**
        - 📢 **Wykład wspólny** - zajęcia dla całego rocznika
        - 👥 **Zajęcia grupy** - laboratoria/ćwiczenia dla tej grupy
        """)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Pobierz jako CSV",
            data=csv,
            file_name=f"plan_{selected_group_key.replace(' ', '_')}.csv",
            mime="text/csv"
        )
    else:
        st.info("ℹ️ Brak zajęć dla wybranej grupy")



def _display_teacher_schedule(repos, schedule_service: ScheduleViewService, dept_id: int = None):
    """displays schedule for teacher"""
    teachers = repos['teachers'].get_all()
    
    if dept_id:
        teachers = [t for t in teachers if t[3] == dept_id]
    
    if not teachers:
        st.warning("⚠️ Brak prowadzących w systemie")
        return
    
    teacher_options = {f"{t[1]} {t[2]}": t[0] for t in teachers}
    selected_teacher = st.selectbox("👨‍🏫 Wybierz prowadzącego:", list(teacher_options.keys()))
    teacher_id = teacher_options[selected_teacher]
    
    schedule = schedule_service.get_teacher_schedule(teacher_id)
    
    if schedule:
        st.success(f"📅 Znaleziono {len(schedule)} zajęć")
        
        df_data = []
        for s in schedule:
            df_data.append({
                'Dzień': s['weekday_pl'],
                'Godzina': s['timeslot'],
                'Przedmiot': s['course_name'],
                'Typ': COURSE_TYPE_LABELS_PL.get(s['course_type'], s['course_type']),
                'Grupa': f"{s['group_code']} - {s['group_name']}",
                'Sala': s['room_code'],
                'Parzystość': WEEK_PARITY_LABELS_PL.get(s['parity'], s['parity']),
                'Notatki': s['note'] if s['note'] else '-'
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Pobierz jako CSV",
            data=csv,
            file_name=f"plan_{selected_teacher.replace(' ', '_')}.csv",
            mime="text/csv"
        )
    else:
        st.info("ℹ️ Brak zajęć dla wybranego prowadzącego")



def _display_room_schedule(repos, schedule_service: ScheduleViewService, dept_id: int = None):
    """displays schedule for room"""
    rooms = repos['rooms'].get_all()
    
    if dept_id:
        dept_buildings = [b[0] for b in repos['buildings'].get_all() if b[3] == dept_id]
        rooms = [r for r in rooms if r[1] in dept_buildings]
    
    if not rooms:
        st.warning("⚠️ Brak sal w systemie")
        return
    
    # add room type to name
    room_options = {}
    for r in rooms:
        room_type_pl = ROOM_TYPE_LABELS_PL.get(r[5], r[5])
        room_options[f"{r[2]} - {r[3] or r[0]} ({room_type_pl})"] = r[0]
    
    selected_room_key = st.selectbox("🚪 Wybierz salę:", list(room_options.keys()))
    room_id = room_options[selected_room_key]
    
    schedule = schedule_service.get_room_schedule(room_id)
    
    if schedule:
        st.success(f"📅 Znaleziono {len(schedule)} zajęć")
        
        df_data = []
        for s in schedule:
            df_data.append({
                'Dzień': s['weekday_pl'],
                'Godzina': s['timeslot'],
                'Przedmiot': s['course_name'],
                'Typ': COURSE_TYPE_LABELS_PL.get(s['course_type'], s['course_type']),
                'Grupa': f"{s['group_code']} - {s['group_name']}",
                'Prowadzący': s['teacher_name'],
                'Parzystość': WEEK_PARITY_LABELS_PL.get(s['parity'], s['parity']),
                'Notatki': s['note'] if s['note'] else '-'
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Pobierz jako CSV",
            data=csv,
            file_name=f"plan_sala_{selected_room_key.split('-')[0].strip()}.csv",
            mime="text/csv"
        )
    else:
        st.info("ℹ️ Brak zajęć dla wybranej sali")
