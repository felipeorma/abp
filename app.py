import streamlit as st
from modules.registro import registro_page

# Configuración inicial
st.set_page_config(
    layout="centered",
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

# Inicializar sesión si no existe
if "registro" not in st.session_state:
    st.session_state.registro = []

# Mostrar página seleccionada
if pagina == "🏟️ Registro en Vivo":
    registro_page()
else:
    st.write("Panel Analítico")  # Aquí deberías importar analitica_page()
