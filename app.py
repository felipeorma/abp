import streamlit as st
from modules.registro import registro_page
from modules.analitica import analitica_page
from modules.heatmaps import heatmaps_page
from utils.i18n import get_text

# Configuración de página
st.set_page_config(
    page_title="Cavalry FC Analytics Pro",
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

    pagina_idx = opciones_navegacion.index(pagina)

    # 🔐 Autenticación solo para Live Registration
    if pagina_idx == 0:
        if "auth_ok" not in st.session_state:
            st.session_state.auth_ok = False

        if not st.session_state.auth_ok:
            st.subheader("🔐 Ingresar código de acceso")
            code_input = st.text_input("Código:", type="password")
            if st.button("Ingresar"):
                if code_input == "CAV2025":  # Cambia aquí tu código de acceso
                    st.success("✅ Acceso autorizado")
                    st.session_state.auth_ok = True
                else:
                    st.error("❌ Código incorrecto")
            return  # No permite ver la página hasta ingresar el código

        registro_page(lang)

    elif pagina_idx == 1:
        analitica_page(lang)

    elif pagina_idx == 2:
        heatmaps_page(lang)

if __name__ == "__main__":
    main()

