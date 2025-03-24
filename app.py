import streamlit as st
from modules.navigation import show_navigation
from modules.registro import registro_page
from modules.analitica import analitica_page
from config import setup_config

# Configuración inicial
setup_config()

# Navegación
page = show_navigation()

# Mostrar página seleccionada
if page == "registro":
    registro_page()
else:
    analitica_page()
