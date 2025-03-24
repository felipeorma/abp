import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_github_data

def analitica_page():
    st.title("📈 Análisis Avanzado de Jugadas a Balón Parado")
    
    # Cargar datos
    df = load_github_data()
    
    if not df.empty:
        # Filtros
        st.sidebar.header("🔍 Filtros Avanzados")
        jugador_filtro = st.sidebar.multiselect("Filtrar por jugador", df['Ejecutor'].unique())
        resultado_filtro = st.sidebar.multiselect("Filtrar por resultado", df['Resultado'].unique())
        
        # Aplicar filtros
        filtered_df = df.copy()
        if jugador_filtro:
            filtered_df = filtered_df[filtered_df['Ejecutor'].isin(jugador_filtro)]
        if resultado_filtro:
            filtered_df = filtered_df[filtered_df['Resultado'].isin(resultado_filtro)]
        
        # KPIs
        mostrar_kpis(filtered_df)
        
        # Gráficos
        mostrar_heatmaps(filtered_df)
        mostrar_rankings(filtered_df)
        
def mostrar_kpis(df):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Acciones Totales", len(df))
    with col2:
        st.metric("Tasa de Éxito", f"{df['Gol'].eq('Sí').mean()*100:.1f}%")
    with col3:
        st.metric("Estrategias Exitosas", df['Estrategia'].eq('Sí').sum())
    with col4:
        st.metric("Goles Totales", df['Gol'].eq('Sí').sum())

def mostrar_heatmaps(df):
    st.header("🔥 Heatmaps Tácticos")
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.density_heatmap(
            df, x='x_saque', y='y_saque',
            nbinsx=20, nbinsy=20,
            title="Distribución de Saques"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.density_heatmap(
            df, x='x_remate', y='y_remate',
            nbinsx=20, nbinsy=20,
            title="Zonas de Remate"
        )
        st.plotly_chart(fig, use_container_width=True)

def mostrar_rankings(df):
    st.header("🏅 Rankings de Jugadores")
    stats = df.groupby('Ejecutor').agg(
        Acciones=('Acción', 'count'),
        Goles=('Gol', lambda x: sum(x == 'Sí')),
        Estrategias=('Estrategia', lambda x: sum(x == 'Sí'))
    ).reset_index()
    
    tabs = st.tabs(["Acciones", "Goles", "Estrategias"])
    with tabs[0]:
        fig = px.bar(
            stats.nlargest(10, 'Acciones'),
            x='Ejecutor', y='Acciones',
            title="Top 10 por Acciones"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[1]:
        fig = px.bar(
            stats.nlargest(10, 'Goles'),
            x='Ejecutor', y='Goles',
            title="Top 10 por Goles"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[2]:
        fig = px.bar(
            stats.nlargest(10, 'Estrategias'),
            x='Ejecutor', y='Estrategias',
            title="Top 10 por Estrategias"
        )
        st.plotly_chart(fig, use_container_width=True)
