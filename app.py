# app.py
import streamlit as st
from modules.registro import registro_page
from modules.analitica import analitica_page
from utils.i18n import get_text  # Nuevo import

# Configuración inicial ÚNICA de la página (se mantiene igual)
st.set_page_config(
    page_title="Set Piece Analytics Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

LOGO_URL = "https://upload.wikimedia.org/wikipedia/en/thumb/6/6a/Cavalry_FC_logo.svg/1200px-Cavalry_FC_logo.svg.png"

def main():
    # Configurar idioma (podría venir de una cookie/config más adelante)
    lang = "es"  # Default: español. Podemos hacerlo dinámico después
    
    with st.sidebar:
        st.image(LOGO_URL, width=200)
        
        # Selector de idioma
        lang = st.radio(
            "🌐 Idioma / Language",
            ("Español", "English"),
            index=0 if lang == "es" else 1
        )
        lang = "es" if lang == "Español" else "en"
        
        # Navegación traducida
        pagina = st.radio(
            get_text(lang, "select_module"),
            (
                get_text(lang, "live_registration"),
                get_text(lang, "analytics_panel")
            ),
            index=0
        )

    if "registro" not in st.session_state:
        st.session_state.registro = []

    if pagina == get_text(lang, "live_registration"):
        registro_page(lang)  # Pasamos el idioma al módulo
    else:
        analitica_page(lang)

if __name__ == "__main__":
    main()
