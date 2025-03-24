import streamlit as st
import pandas as pd
from utils.data_loader import load_github_data
from utils.visualizaciones import plot_kpis, plot_barras_jugadores, plot_heatmap_analitica

def analitica_page():
    st.title("📈 Análisis Avanzado de Jugadas a Balón Parado")
    
    df = load_github_data()
    if not df.empty:
        filtered_df = aplicar_filtros(df)
        plot_kpis(filtered_df)
        plot_barras_jugadores(filtered_df)
        plot_heatmap_analitica(filtered_df)

def aplicar_filtros(df):
    st.sidebar.header("🔍 Filtros Avanzados")
    
    # Filtro temporal
    if 'Fecha' in df.columns:
        fecha_min = df['Fecha'].min().date()
        fecha_max = df['Fecha'].max().date()
        rango_fechas = st.sidebar.date_input(
            "Rango de fechas",
            value=(fecha_min, fecha_max),
            min_value=fecha_min,
            max_value=fecha_max
        )
    
    # Otros filtros
    jugadores = st.sidebar.multiselect(
        "Filtrar por jugador",
        options=df['Ejecutor'].unique()
    )
    
    return df if not jugadores else df[df['Ejecutor'].isin(jugadores)]
