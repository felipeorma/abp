# app.py (Archivo principal)
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import VerticalPitch
from modules.registro import formulario_registro, guardar_registro
from modules.analitica import generar_heatmaps, mostrar_estadisticas
from utils.data_loader import cargar_datos_iniciales

def main():
    # Configuración inicial
    st.set_page_config(layout="centered", page_icon="⚽")
    st.title("⚽ Plataforma de Análisis Táctico - Cavalry FC")
    
    # Cargar datos iniciales
    jugadores, equipos, zonas_coords = cargar_datos_iniciales()
    
    # Sección de registro
    datos_registro = formulario_registro(jugadores, equipos, zonas_coords)
    if st.button("Registrar Acción"):
        guardar_registro(datos_registro)
    
    # Sección de visualización
    if st.session_state.registro:
        df = pd.DataFrame(st.session_state.registro)
        generar_heatmaps(df, zonas_coords)
        mostrar_estadisticas(df)
        
if __name__ == "__main__":
    main()
