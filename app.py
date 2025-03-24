import streamlit as st
from modules.registro import registro_page
from modules.analitica import analitica_page

# Configuración inicial de la aplicación
def main():
    st.set_page_config(
        layout="centered",
        page_icon="⚽",
        page_title="Set Piece Analytics Pro",
        initial_sidebar_state="expanded"
    )

    # Cargar estilos CSS personalizados
    with open("assets/estilos.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Barra lateral de navegación
    with st.sidebar:
        st.image("https://github.com/felipeorma/abp/blob/main/logo_cavalry.png?raw=true", 
                width=200)
        pagina = st.radio(
            "Seleccionar módulo:",
            ("🏟️ Registro en Vivo", "📊 Panel Analítico"),
            index=0
        )

    # Inicializar estado de sesión para el registro
    if "registro" not in st.session_state:
        st.session_state.registro = []

    # Mostrar página seleccionada
    if pagina == "🏟️ Registro en Vivo":
        registro_page()
    else:
        analitica_page()

    # Pie de página profesional
    st.divider()
    with st.container():
        col1, col2, col3 = st.columns([2,1,2])
        with col2:
            st.caption("© 2024 Cavalry FC - Todos los derechos reservados")
            st.caption("Desarrollado por: [Felipe Ormazabal]")

if __name__ == "__main__":
    main()
