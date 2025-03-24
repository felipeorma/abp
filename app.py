import streamlit as st
from modules.registro import registro_page
from modules.analitica import analitica_page

# Configuración inicial
st.set_page_config(
    layout="wide",
    page_icon="⚽",
    page_title="Set Piece Analytics Pro",
    initial_sidebar_state="expanded"
)

# Cargar estilos CSS
with open("assets/estilos.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Navegación
pagina = st.sidebar.radio(
    "Seleccionar módulo:",
    ("🏟️ Registro en Vivo", "📊 Panel Analítico"),
    index=0
)

# Mostrar página seleccionada
if "registro" not in st.session_state:
    st.session_state.registro = []

if pagina == "🏟️ Registro en Vivo":
    registro_page()
else:
    analitica_page()
