import streamlit as st
import pandas as pd
from utils.visualizaciones import plot_heatmap_registro

def registro_page():
    st.title("⚽ Registro y Heatmap de Balón Parado - Cavalry FC")
    
    if "registro" not in st.session_state:
        st.session_state.registro = []
    
    # Cargar datos estáticos
    jugadores_cavalry, equipos_cpl, zonas_coords = load_static_data()
    
    # Mostrar formulario
    registro_data = show_form(jugadores_cavalry, equipos_cpl, zonas_coords)
    
    # Procesar registro
    if registro_data:
        process_registration(registro_data)
    
    # Mostrar datos y visualizaciones
    show_data_and_visualizations(zonas_coords)

def load_static_data():
    jugadores = [...]  # Lista completa de jugadores
    equipos = [...]    # Lista completa de equipos
    zonas = pd.read_csv("assets/zonas.csv").set_index('Zona').to_dict('index')
    return jugadores, equipos, zonas

def show_form(jugadores, equipos, zonas):
    # Implementación completa del formulario
    # ...
    return registro_data  # Datos del formulario

def process_registration(data):
    st.session_state.registro.append(data)
    st.success("Acción registrada exitosamente!")
    st.balloons()

def show_data_and_visualizations(zonas):
    if st.session_state.registro:
        df = pd.DataFrame(st.session_state.registro)
        st.dataframe(df, use_container_width=True)
        
        # Filtros y visualizaciones
        # ...
        plot_heatmap_registro(filtered_df, zonas)
