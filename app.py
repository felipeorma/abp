# app.py
import streamlit as st
from modules.registro import registro_page
from modules.analitica import analitica_page

# Configuración inicial ÚNICA de la página
st.set_page_config(
    page_title="Set Piece Analytics Pro",
    page_icon="⚽",
    layout="wide",  # Configuración única para toda la app
    initial_sidebar_state="expanded"
)

# URL correcta del logo
LOGO_URL = "https://upload.wikimedia.org/wikipedia/en/thumb/6/6a/Cavalry_FC_logo.svg/1200px-Cavalry_FC_logo.svg.png"

def main():
    # Barra lateral común
    with st.sidebar:
        st.image(LOGO_URL, width=200)
        pagina = st.radio(
            "Seleccionar módulo:",
            ("🏟️ Registro en Vivo", "📊 Panel Analítico"),
            index=0
        )

    # Gestión del estado de sesión
    if "registro" not in st.session_state:
        st.session_state.registro = []

    # Navegación entre páginas
    if pagina == "🏟️ Registro en Vivo":
        registro_page()
    else:
        analitica_page()

if __name__ == "__main__":
    main()
