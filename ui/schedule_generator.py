import streamlit as st
from datetime import datetime, time, timedelta
from ui.components import render_section_header
from services.schedule_service import ScheduleService
from services.validation_service import ValidationService


def generate_schedule_ai(repos):
    """generate schedule using AI"""
    render_section_header("Automatyczne Generowanie Planu Zajęć", "🤖")
    
    st.markdown("""
    <div class="info-box">
    Ten moduł wykorzystuje algorytm genetyczny do automatycznego wygenerowania optymalnego planu zajęć 
    z uwzględnieniem wszystkich ograniczeń.
    </div>
    """, unsafe_allow_html=True)
    
    # check requirements
    course_assignments = repos['course_assignments'].get_all()
    rooms = repos['rooms'].get_all()
    
    if not course_assignments:
        st.error("❌ Brak przypisań przedmiotów! Najpierw dodaj przypisania.")
        st.info("Przejdź do zakładki: **Przedmioty i Zajęcia → Przypisania**")
        return
    
    if not rooms:
        st.error("❌ Brak sal! Najpierw dodaj sale.")
        return
    
    st.success(f"✅ System gotowy: {len(course_assignments)} przypisań, {len(rooms)} sal")
    
    # algorithm parameters
    st.subheader("⚙️ Parametry Algorytmu Genetycznego")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        population_size = st.number_input("Wielkość populacji", min_value=10, max_value=200, value=50)
    
    with col2:
        generations = st.number_input("Liczba generacji", min_value=10, max_value=500, value=100)
    
    with col3:
        mutation_rate = st.slider("Współczynnik mutacji", min_value=0.0, max_value=1.0, value=0.15)
    
    st.info("""
    **Algorytm automatycznie uwzględnia:**
    - ✅ Dopasowanie sal do typu zajęć (wykład → sala wykładowa, lab → laboratorium)
    - ✅ Minimalizację okien między zajęciami
    - ✅ Limit 11 godzin dziennie
    - ✅ Brak konfliktów czasowych
    - ✅ Równomierne rozkładanie zajęć
    """)
    
    if st.button("🚀 Generuj Plan Zajęć", type="primary", use_container_width=True):
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔄 Przygotowywanie danych...")
            progress_bar.progress(10)
            
            # use service
            schedule_service = ScheduleService(repos)
            
            status_text.text("🧬 Ewolucja rozwiązań...")
            progress_bar.progress(50)
            
            result = schedule_service.generate_schedule_with_ga({
                'population_size': population_size,
                'generations': generations,
                'mutation_rate': mutation_rate
            })
            
            if not result['success']:
                st.error(f"❌ Błąd: {result.get('error', 'Nieznany błąd')}")
                return
            
            status_text.text("💾 Zapisywanie...")
            progress_bar.progress(90)
            
            schedule_service.save_schedule_to_db(result['timetable'])
            
            progress_bar.progress(100)
            status_text.text("✅ Zakończono!")
            
            st.success(f"🎉 Plan wygenerowany! Fitness: {result['fitness']:.2f}")

            # recompute validation using the freshly saved schedule to expose real conflict counts
            try:
                assignments_snapshot = repos['assignments'].get_all()
                validation_service = ValidationService(repos)
                report = validation_service.validate_schedule(assignments_snapshot)
            except Exception as validation_error:
                report = result['validation_report']
                st.warning(f"⚠️ Nie udało się ponownie przeliczyć walidacji: {validation_error}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("📋 Zajęcia", len(result['timetable'].assignments))
            
            with col2:
                st.metric("⚠️ Konflikty", report['total_conflicts'])
            
            with col3:
                status = "OK" if report['is_valid'] else "Wymaga poprawy"
                st.metric("✅ Status", status)
            
            if report['is_valid']:
                st.success("✅ Plan jest poprawny!")
                st.balloons()
            else:
                st.warning("⚠️ Plan zawiera konflikty - sprawdź walidację")
        
        except Exception as e:
            st.error(f"❌ Błąd: {e}")
            import traceback
            with st.expander("🔍 Szczegóły"):
                st.code(traceback.format_exc())
