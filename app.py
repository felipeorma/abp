# app.py
import streamlit as st
from modules.registro import registro_page
from modules.analitica import analitica_page
from utils.i18n import get_text

# Configuración de página (no cambiar)
st.set_page_config(
    page_title="Set Piece Analytics Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ruta CORREGIDA para el logo (asumiendo que está en raíz del repositorio)
LOGO_PATH = "Cavalry_FC_logo.svg"  # Archivo debe estar en mismo nivel que app.py

def main():
    # Configuración de idioma
    lang = "es"  # Valor inicial
    
    with st.sidebar:
        # Carga del logo con manejo de errores
        try:
            st.image(LOGO_PATH, width=200)
        except Exception as e:
            st.error(f"Error loading logo: {str(e)}")
            st.markdown("### ⚽ Set Piece Analytics Pro")  # Fallback textual
        
        # Selector de idioma mejorado
        lang_option = st.radio(
            "🌐 Idioma / Language",
            ("Español", "English"),
            index=0
        )
        lang = "es" if lang_option == "Español" else "en"
        
        # Navegación internacionalizada
        pagina = st.radio(
            get_text(lang, "select_module"),
            (
                get_text(lang, "live_registration"),
                get_text(lang, "analytics_panel")
            ),
            index=0
        )

    # Estado de sesión
    if "registro" not in st.session_state:
        st.session_state.registro = []

    # Navegación
    if pagina == get_text(lang, "live_registration"):
        registro_page(lang)
    else:
        analitica_page(lang)

if __name__ == "__main__":
    main()