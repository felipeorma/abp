import streamlit as st

def setup_config():
    st.set_page_config(
        layout="wide",
        page_icon="⚽",
        page_title="Set Piece Analytics Pro",
        initial_sidebar_state="expanded"
    )
    
    # Cargar estilos CSS
    with open("assets/estilos.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
