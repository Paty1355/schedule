import streamlit as st
from ui.components import render_section_header



def show_home(repos):
    """home page"""
    render_section_header("System Planowania Zajęć", "🎓")
    
    st.markdown("""
    <div class="info-box">
        <h4>👋 Witaj w Systemie Planowania Zajęć!</h4>
        <p>Kompleksowe narzędzie do automatycznego generowania i zarządzania planem zajęć 
        z wykorzystaniem algorytmów genetycznych.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # statistics
    st.markdown("### 📊 Statystyki Bazy Danych")
    
    try:
        stats = _get_database_statistics(repos)
        
        col1, col2, col3 = st.columns(3)
        
        items = list(stats.items())
        for idx, (label, value) in enumerate(items):
            with [col1, col2, col3][idx % 3]:
                st.metric(label, value)
    
    except Exception as e:
        st.error(f"❌ Błąd pobierania statystyk: {e}")
        import traceback
        with st.expander("🔍 Szczegóły błędu"):
            st.code(traceback.format_exc())
    
    # features
    st.markdown("---")
    st.markdown("### ✨ Główne Funkcje")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🏢 Zarządzanie Danymi**
        - Wydziały i Budynki
        - Sale Wykładowe
        - Grupy Studenckie
        - Prowadzący
        """)
    
    with col2:
        st.markdown("""
        **📖 Przedmioty i Zajęcia**
        - Przedmioty
        - Przypisania
        - Sloty Czasowe
        - Niedostępności
        """)
    
    with col3:
        st.markdown("""
        **🤖 Generowanie Planu**
        - Algorytm Genetyczny
        - Walidacja Planu
        - Eksport/Import
        - Podgląd Planu
        """)
    
    # quick start
    st.markdown("---")
    st.markdown("### 🚀 Szybki Start")
    
    st.markdown("""
    1. **Import danych** - Pobierz szablon Excel i wypełnij go danymi lub dodaj dane ręcznie
    2. **Generuj plan** - Użyj algorytmu genetycznego do automatycznego generowania planu
    3. **Waliduj** - Sprawdź czy plan nie zawiera konfliktów
    4. **Eksportuj** - Pobierz gotowy plan w formacie CSV lub Excel
    """)
    
    # tips
    st.markdown("---")
    st.markdown("### 💡 Wskazówki")
    
    st.info("""
    - **Rozpocznij od importu** - Najszybszy sposób na wprowadzenie danych
    - **Sprawdź typy sal** - Algorytm automatycznie dopasowuje sale do typu zajęć
    - **Użyj grup nadrzędnych** - Wykłady dla całego rocznika, laboratoria dla podgrup
    - **Waliduj często** - Sprawdzaj plan po każdej zmianie
    """)



def _get_database_statistics(repos) -> dict:
    """fetches statistics from database"""
    tables = {
        '🏢 Wydziały': 'departments',
        '🏛️ Budynki': 'buildings',
        '🚪 Sale': 'rooms',
        '👥 Grupy': 'groups',
        '👨‍🏫 Prowadzący': 'teachers',
        '📖 Przedmioty': 'courses',
        '📋 Przypisania': 'course_assignments',
        '📅 Wygenerowany plan': 'assignments'
    }
    
    stats = {}
    
    # fetch dbmanager from repos
    db_manager = repos['departments'].db_manager
    
    for label, table in tables.items():
        try:
            db_manager.cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = db_manager.cur.fetchone()[0]
            stats[label] = count
        except Exception as e:
            stats[label] = 0
    
    return stats
