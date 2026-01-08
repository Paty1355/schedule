import streamlit as st

def render_section_header(title: str, icon: str = ""):
    """render section header"""
    full_title = f"{icon} {title}" if icon else title
    st.markdown(f'<div class="section-header">{full_title}</div>', unsafe_allow_html=True)


def render_info_box(title: str, content: str):
    """render info box"""
    st.markdown(f"""
    <div class="info-box">
        <h4>{title}</h4>
        <p>{content}</p>
    </div>
    """, unsafe_allow_html=True)


def render_success_box(message: str):
    """render success box"""
    st.markdown(f"""
    <div class="success-box">
        {message}
    </div>
    """, unsafe_allow_html=True)


def render_warning_box(message: str):
    """render warning box"""
    st.markdown(f"""
    <div class="warning-box">
        {message}
    </div>
    """, unsafe_allow_html=True)


def confirm_action(message: str, key: str) -> bool:
    """confirmation dialog for action"""
    return st.checkbox(message, key=key)
