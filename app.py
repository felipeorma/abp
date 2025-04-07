import streamlit as st
from modules.registro import registro_page
from modules.analitica import analitica_page
from modules.heatmaps import heatmaps_page
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
    lang = "es"

    with st.sidebar:
        try:
            st.image(LOGO_PATH, width=200)
        except Exception as e:
            st.error(get_text(lang, "logo_error").format(error=str(e)))

        # Selector de idioma
        lang = "es" if st.radio(
            "🌐 Idioma / Language",
            ["Español", "English"],
            index=0
        ) == "Español" else "en"

        # Navegación
        opciones_navegacion = [
            get_text(lang, "live_registration"),
            get_text(lang, "analytics_panel"),
            get_text(lang, "heatmaps_tab")
        ]

        pagina = st.radio(
            get_text(lang, "select_module"),
            opciones_navegacion,
            index=0
        )

    # Gestión del estado de sesión
    st.session_state.setdefault("registro", [])
    st.session_state.setdefault("auth", False)  # Nuevo estado para autenticación

    # Navegación
    pagina_idx = opciones_navegacion.index(pagina)

    if pagina_idx == 0:  # Live Registration
        if not st.session_state.auth:
            st.subheader("🔐 Acceso Restringido - Solo personal autorizado")
            codigo = st.text_input("Ingrese el código de acceso:", type="password", key="access_code")
            
            if st.button("Verificar código"):
                if codigo == "CAV2025":  # Código personalizable
                    st.session_state.auth = True
                    st.experimental_rerun()
                else:
                    st.error("Código incorrecto, intente nuevamente")
            return  # Bloquear acceso hasta código correcto
        
        registro_page(lang)
    
    elif pagina_idx == 1:  # Analytics Panel
        analitica_page(lang)
    
    elif pagina_idx == 2:  # Heatmaps
        heatmaps_page()

if __name__ == "__main__":
    main()
