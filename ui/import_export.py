import streamlit as st
from datetime import datetime
from ui.components import render_section_header
from services.import_export_service import ImportExportService


def import_export_data(repos):
    """import and export data"""
    render_section_header("Import i Eksport Danych", "💾")
    
    tab1, tab2, tab3 = st.tabs(["📥 Import Planu", "📤 Eksport Danych", "📋 Szablon Excel"])
    
    with tab1:
        _import_tab(repos)
    
    with tab2:
        _export_tab(repos)
    
    with tab3:
        _template_tab(repos)


def _import_tab(repos):
    """import tab"""
    st.subheader("📥 Import danych z pliku Excel")
    
    st.markdown("""
    <div class="info-box">
        <h4>📖 Instrukcja importu</h4>
        <ol>
            <li>Pobierz szablon Excel z zakładki "Szablon Excel"</li>
            <li>Wypełnij dane w odpowiednich arkuszach</li>
            <li>Wgraj wypełniony plik poniżej</li>
            <li>System automatycznie zaimportuje dane do bazy</li>
        </ol>
        <p><strong>⚠️ Uwaga:</strong> Duplikaty będą automatycznie pomijane</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Wybierz plik Excel (.xlsx)", type=['xlsx'])
    
    if uploaded_file is not None:
        try:
            st.info(f"📂 Wczytano plik: **{uploaded_file.name}**")
            
            if st.button("🚀 Rozpocznij import", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("🔄 Importowanie danych...")
                progress_bar.progress(10)
                
                # use service
                import_service = ImportExportService(repos)
                result = import_service.import_from_excel(uploaded_file)
                
                progress_bar.progress(100)
                
                if result['success']:
                    st.success("✅ Import zakończony pomyślnie!")
                    
                    # show statistics
                    st.markdown("### 📊 Statystyki importu")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**✅ Dodane:**")
                        for key, data in result['stats'].items():
                            if data['added'] > 0:
                                st.text(f"• {key.capitalize()}: {data['added']}")
                    
                    with col2:
                        st.markdown("**⏭️ Pominięte:**")
                        for key, data in result['stats'].items():
                            if data['skipped'] > 0:
                                st.text(f"• {key.capitalize()}: {data['skipped']}")
                    
                    # show errors
                    if result['errors']:
                        with st.expander(f"⚠️ Błędy ({len(result['errors'])})", expanded=False):
                            for error in result['errors']:
                                st.text(f"• {error}")
                    
                    st.balloons()
                else:
                    st.error(f"❌ Błąd importu: {result['errors'][0] if result['errors'] else 'Nieznany błąd'}")
        
        except Exception as e:
            st.error(f"❌ Błąd wczytywania pliku: {e}")
            import traceback
            with st.expander("🔍 Szczegóły"):
                st.code(traceback.format_exc())


def _export_tab(repos):
    """export tab"""
    st.subheader("📤 Eksport danych")
    
    st.markdown("""
    <div class="info-box">
        <h4>💾 Eksport wszystkich danych</h4>
        <p>Pobierz kopię wszystkich danych z bazy w formacie Excel. 
        Możesz później użyć tego pliku do importu.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📥 Eksportuj wszystkie dane", type="primary"):
        try:
            # Use service
            export_service = ImportExportService(repos)
            output = export_service.export_all_data()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"plan_zajec_backup_{timestamp}.xlsx"
            
            st.download_button(
                label="⬇️ Pobierz plik Excel",
                data=output,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            st.success("✅ Plik gotowy do pobrania!")
        
        except Exception as e:
            st.error(f"❌ Błąd eksportu: {e}")
            import traceback
            with st.expander("🔍 Szczegóły"):
                st.code(traceback.format_exc())


def _template_tab(repos):
    """template tab"""
    st.subheader("📋 Szablony Excel do importu")
    
    st.markdown("""
    <div class="info-box">
        <h4>✨ Wybierz typ szablonu</h4>
        <p><strong>📊 Szablon z przykładowymi danymi</strong> - zawiera realistyczne dane dla 4 kierunków studiów do testów</p>
        <p><strong>📝 Pusty szablon</strong> - tylko struktura arkuszy z nagłówkami do wypełnienia własnymi danymi</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Z przykładowymi danymi")
        if st.button("📥 Generuj szablon z danymi", type="primary", key="template_with_data"):
            try:
                from ui.template_generator import generate_template
                output = generate_template()
                
                st.download_button(
                    label="⬇️ Pobierz szablon z danymi",
                    data=output,
                    file_name="szablon_plan_zajec_z_danymi.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_with_data"
                )
                st.success("✅ Szablon gotowy!")
                
                st.markdown("""
                **📦 Zawartość:**
                - 4 wydziały
                - 5 budynków
                - 56 sal
                - 6 slotów czasowych
                - 25 grup
                - 23 prowadzących
                - 39 przedmiotów
                - 52 przypisań
                """)
            
            except Exception as e:
                st.error(f"❌ Błąd: {e}")
    
    with col2:
        st.markdown("### 📝 Pusty szablon")
        if st.button("📥 Generuj pusty szablon", type="secondary", key="template_empty"):
            try:
                from ui.template_generator import generate_empty_template
                output = generate_empty_template()
                
                st.download_button(
                    label="⬇️ Pobierz pusty szablon",
                    data=output,
                    file_name="szablon_plan_zajec_pusty.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="download_empty"
                )
                st.success("✅ Pusty szablon gotowy!")
                
                st.markdown("""
                **📦 Zawartość:**
                - Wszystkie wymagane arkusze
                - Tylko nagłówki kolumn
                - Gotowe do wypełnienia
                - Jeden przykładowy wiersz w każdym arkuszu
                """)
            
            except Exception as e:
                st.error(f"❌ Błąd: {e}")
    
    st.markdown("---")
    
    # manual
    st.markdown("""
    ### 📖 Instrukcja wypełniania:
    
    **Arkusze (w kolejności):**
    1. **Wydzialy** - `kod`, `nazwa`
    2. **Budynki** - `nazwa`, `adres`, `kod_wydzialu`
    3. **Sale** - `kod`, `nazwa`, `nazwa_budynku`, `pojemnosc`, `typ`, `notatki`
    4. **SlotyGodzinowe** - `od` (HH:MM), `do` (HH:MM), `numer`
    5. **Grupy** - `kod`, `nazwa`, `kod_wydzialu`, `liczba_studentow`, `parent_kod`
    6. **Prowadzacy** - `imie`, `nazwisko`, `kod_wydzialu`
    7. **Przedmioty** - `kod`, `nazwa`, `kod_wydzialu`, `typ`, `godziny_semestr`
    8. **Przypisania** - `kod_przedmiotu`, `kod_grupy`, `prowadzacy`, `semestr`
    
    ---
    
    **🚪 Typy sal:**
    - `lecture_hall` - sala wykładowa
    - `classroom` - sala ćwiczeniowa
    - `auditorium` - audytorium
    - `computer_lab` - laboratorium komputerowe
    - `chemistry_lab` - laboratorium chemiczne
    - `physics_lab` - laboratorium fizyczne
    - `biology_lab` - laboratorium biologiczne
    - `language_lab` - laboratorium językowe
    - `seminar_room` - sala seminaryjna
    - `workshop` - warsztat
    - `gym` - sala gimnastyczna
    - `other` - inna
    
    **📖 Typy przedmiotów:**
    - `lecture` - wykład
    - `exercise` - ćwiczenia
    - `seminar` - seminarium
    - `project` - projekt
    - `computer_lab` - laboratorium komputerowe
    - `chemistry_lab` - laboratorium chemiczne
    - `physics_lab` - laboratorium fizyczne
    - `biology_lab` - laboratorium biologiczne
    - `language_lab` - laboratorium językowe
    - `workshop` - warsztat
    - `gym_class` - zajęcia sportowe (WF)
    - `other` - inne
    """)
