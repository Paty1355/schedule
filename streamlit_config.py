import streamlit as st

def setup_page_config():
    """configure streamlit page"""
    st.set_page_config(
        page_title="System Planu Zajęć",
        page_icon="📅",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def load_custom_css():
    """load custom css"""
    st.markdown("""
    <style>
    /* section headers */
    .section-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* info boxes */
    .info-box {
        background-color: #e3f2fd !important;
        border-left: 5px solid #2196f3;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        color: #1565c0 !important;
    }
    
    .info-box h4 {
        margin-top: 0;
        color: #0d47a1 !important;
    }
    
    .info-box p,
    .info-box li,
    .info-box ol,
    .info-box strong {
        color: #1565c0 !important;
    }
    
    .success-box {
        background-color: #e8f5e9 !important;
        border-left: 5px solid #4caf50;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        color: #2e7d32 !important;
    }
    
    .warning-box {
        background-color: #fff3e0 !important;
        border-left: 5px solid #ff9800;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        color: #e65100 !important;
    }
    
    /* sidebar - main background */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
    }
    
    /* sidebar - all texts */
    section[data-testid="stSidebar"] * {
        color: #1f2937 !important;
    }
    
    /* sidebar - radio buttons */
    section[data-testid="stSidebar"] .stRadio > label,
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    /* sidebar - selectbox - fix background and text */
    section[data-testid="stSidebar"] .stSelectbox label {
        color: #000000 !important;
        font-weight: 500 !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] {
        background-color: #ffffff !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    /* sidebar - selectbox dropdown (expanded list) */
    [data-baseweb="popover"] {
        background-color: #ffffff !important;
    }
    
    [data-baseweb="popover"] ul {
        background-color: #ffffff !important;
    }
    
    [data-baseweb="popover"] li {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    
    [data-baseweb="popover"] li:hover {
        background-color: #e3f2fd !important;
        color: #000000 !important;
    }
    
    /* sidebar - markdown */
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #000000 !important;
    }
    
    /* sidebar - caption */
    section[data-testid="stSidebar"] .stCaption {
        color: #6b7280 !important;
    }
    
    /* sidebar - expander */
    section[data-testid="stSidebar"] details summary {
        color: #000000 !important;
        background-color: #e5e7eb !important;
    }
    
    /* tables */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* dataframe - force text colors */
    .stDataFrame table tbody tr td {
        color: #000000 !important;
    }
    
    .stDataFrame table thead tr th {
        color: #000000 !important;
        background-color: #f1f5f9 !important;
    }
    
    /* buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
    }
    
    /* metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: bold;
    }
    
    /* main content */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
