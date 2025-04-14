import streamlit as st
from config import TABS  

def render_navbar(cart_count: int):
    """Render the navigation bar with cart count"""
    col1, col2 = st.columns([4, 1])

    current_tab = st.session_state.get("current_tab", "Home")
    current_index = TABS.index(current_tab) if current_tab in TABS else 0

    with col1:
        selected_tab = st.radio(
            "Navigation", 
            TABS,  # Use TABS from config
            index=current_index,
            horizontal=True,
            label_visibility="collapsed"
        )
    
    with col2:
        st.markdown(f"""
        <div style="text-align: right; margin-bottom: 20px;">
            <span style="font-size: 24px;">🛒</span>
            <span style="background-color: red; color: white; 
                     border-radius: 50%; padding: 2px 8px; 
                     font-size: 14px; position: relative; top: -10px;">
                {cart_count}
            </span>
        </div>
        """, unsafe_allow_html=True)

    return selected_tab