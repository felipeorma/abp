import streamlit as st
import pandas as pd
from utils.data_loader import load_github_data
from utils.visualizaciones import (
    plot_kpis,
    plot_heatmap_analitica,
    plot_barras_jugadores
)

def analitica_page():
    st.title("📈 Análisis Avanzado de Jugadas a Balón Parado")
    
    # Cargar datos
    df = load_github_data()
    
    if not df.empty:
        # Mostrar filtros
        filtered_df = apply_filters(df)
        
        # Mostrar KPIs
        plot_kpis(filtered_df)
        
        # Gráficos principales
        plot_barras_jugadores(filtered_df)
        plot_heatmap_analitica(filtered_df)

def apply_filters(df):
    # Implementación de filtros
    # ...
    return filtered_df
