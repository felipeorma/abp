import streamlit as st

def show_navigation():
    st.sidebar.title("Navegación")
    return st.sidebar.radio(
        "Seleccionar módulo:",
        ("🏟️ Registro en Vivo", "📊 Panel Analítico"),
        index=0,
        key="nav_radio"
    )
