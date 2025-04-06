import streamlit as st
from modules.registro import registro_page
from modules.analitica import analitica_page
from modules.heatmaps import heatmaps_page
from utils.i18n import get_text

def main():
    st.set_page_config(
        page_title="Cavalry FC Analytics Pro",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Configuración inicial
    lang = "es"
    logo_path = "https://upload.wikimedia.org/wikipedia/en/thumb/4/47/Cavalry_FC.svg/1200px-Cavalry_FC.svg.png"
    
    # Sidebar principal
    with st.sidebar:
        st.image(logo_path, width=200)
        lang = "es" if st.radio("🌐 Idioma", ["Español", "English"]) == "Español" else "en"
        
        # Navegación
        opciones = {
            "live": get_text(lang, "live_registration"),
            "analytics": get_text(lang, "analytics_panel"),
            "heatmaps": get_text(lang, "heatmaps_tab")
        }
        pagina = st.radio(get_text(lang, "select_module"), list(opciones.values()))
    
    # Gestión de autenticación
    if opciones.inv(pagina) == "live" and not st.session_state.get("auth"):
        handle_authentication(lang)
        return
    
    # Routing de páginas
    page_mapper = {
        opciones["live"]: lambda: registro_page(lang),
        opciones["analytics"]: lambda: analitica_page(lang),
        opciones["heatmaps"]: lambda: heatmaps_page(lang)
    }
    page_mapper[pagina]()

def handle_authentication(lang):
    st.subheader(get_text(lang, "auth_header"))
    code = st.text_input(get_text(lang, "auth_code"), type="password")
    if st.button(get_text(lang, "auth_button")):
        if code == "CAV2025":
            st.session_state.auth = True
            st.experimental_rerun()
        else:
            st.error(get_text(lang, "auth_error"))

if __name__ == "__main__":
    main()
