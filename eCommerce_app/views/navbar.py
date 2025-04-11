import streamlit as st
from config import TABS  

def render_navbar(cart_count: int):
    """Render the navigation bar with cart count"""
    col1, col2 = st.columns([4, 1])
    with col1:
        st.session_state.current_tab = st.radio(
            "Navigation", 
            TABS,  # Use TABS from config
            index=TABS.index(st.session_state.current_tab),
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