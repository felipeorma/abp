# app.py
import streamlit as st
from modules.registro import registro_page
from modules.analitica import analitica_page
from utils.i18n import get_text

# Configuración de página
st.set_page_config(
    page_title="Set Piece Analytics Pro",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

LOGO_PATH = "Cavalry_FC_logo.svg"

def main():
    lang = "es"  # Valor por defecto
    
    with st.sidebar:
        # Logo con manejo de errores
        try:
            st.image(LOGO_PATH, width=200)
        except Exception as e:
            st.error(get_text(lang, "logo_error").format(error=str(e)))
            st.markdown(f"### ⚽ {get_text(lang, 'app_title')}")
        
        # Selector de idioma
        lang_option = st.radio(
            "🌐 Idioma / Language",
            ("Español", "English"),
            index=0
        )
        lang = "es" if lang_option == "Español" else "en"
        
        # Opciones de navegación con valores internos en español
        nav_options = [
            (get_text(lang, "live_registration"), "registro"),
            (get_text(lang, "analytics_panel"), "analitica")
        ]
        
        # Mostrar opciones traducidas pero mantener lógica en español
        pagina_label = st.radio(
            get_text(lang, "select_module"),
            options=[option[0] for option in nav_options],
            index=0
        )
        
        # Obtener el valor interno correspondiente
        pagina = [option[1] for option in nav_options if option[0] == pagina_label][0]

    # Inicializar estado de sesión
    if "registro" not in st.session_state:
        st.session_state.registro = []

    # Navegación basada en valores internos
    if pagina == "registro":
        registro_page(lang)
    else:
        analitica_page(lang)

if __name__ == "__main__":
    main()
