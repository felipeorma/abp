import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from mplsoccer import VerticalPitch
import requests
from io import StringIO

# Configuración inicial
st.set_page_config(layout="wide", page_icon="⚽", page_title="Set Piece Analytics Pro")

# URL del archivo maestro en GitHub (actualizar con tu URL)
GITHUB_RAW_URL = "https://raw.githubusercontent.com/tu_usuario/tu_repositorio/main/master_abp.csv"

# Función para cargar datos desde GitHub con caché
@st.cache_data(ttl=3600)  # Actualiza cada hora
def load_github_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return pd.read_csv(StringIO(response.text))
    except Exception as e:
        st.error(f"Error cargando datos: {str(e)}")
        return pd.DataFrame()

# Cargar datos
df = load_github_data(GITHUB_RAW_URL)

if not df.empty:
    # ========== PREPROCESAMIENTO ==========
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    df['Minuto'] = pd.to_numeric(df['Minuto'], errors='coerce')
    
    # ========== SIDEBAR FILTROS ==========
    st.sidebar.header("🔍 Parámetros de Análisis")
    
    # Filtro temporal
    min_date = df['Fecha'].min().date()
    max_date = df['Fecha'].max().date()
    selected_dates = st.sidebar.date_input(
        "Rango de fechas",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Filtros múltiples
    selected_competition = st.sidebar.multiselect("Competición", df['Competición'].unique())
    selected_opponent = st.sidebar.multiselect("Oponente", df['Rival'].unique())
    selected_player = st.sidebar.multiselect("Jugador clave", df['Ejecutor'].unique())
    
    # ========== APLICAR FILTROS ==========
    filtered_df = df.copy()
    
    # Filtro de fechas
    if len(selected_dates) == 2:
        start_date, end_date = selected_dates
        filtered_df = filtered_df[
            (filtered_df['Fecha'].dt.date >= start_date) &
            (filtered_df['Fecha'].dt.date <= end_date)
        ]
    
    # Aplicar otros filtros
    filter_params = {
        'Competición': selected_competition,
        'Rival': selected_opponent,
        'Ejecutor': selected_player
    }
    
    for col, values in filter_params.items():
        if values:
            filtered_df = filtered_df[filtered_df[col].isin(values)]

    # ========== KPI HEADER ==========
    st.header("📊 Métricas Clave")
    col1, col2, col3, col4 = st.columns(4)
    
    kpis = {
        "Acciones Totales": len(filtered_df),
        "Tasa de Éxito": f"{filtered_df['Gol'].eq('Sí').mean()*100:.1f}%",
        "xG Promedio": f"{filtered_df['xG'].mean():.2f}",
        "Eficiencia Estratégica": f"{filtered_df['Estrategia'].eq('Sí').mean()*100:.1f}%"
    }
    
    for col, (kpi, value) in zip([col1, col2, col3, col4], kpis.items()):
        with col:
            st.metric(kpi, value)

    # ========== ANÁLISIS TÁCTICO ==========
    st.header("🔥 Heatmaps Tácticos")
    col1, col2 = st.columns(2)
    
    with col1:
        pitch = VerticalPitch(pitch_type='statsbomb', half=True)
        fig, ax = pitch.draw()
        try:
            pitch.kdeplot(
                filtered_df['x_saque'], filtered_df['y_saque'],
                ax=ax, cmap='Greens', levels=50, alpha=0.7
            )
            ax.set_title("Distribución de Saques", fontsize=14, pad=20)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Error generando heatmap de saques: {str(e)}")
    
    with col2:
        pitch = VerticalPitch(pitch_type='statsbomb', half=True)
        fig, ax = pitch.draw()
        try:
            pitch.kdeplot(
                filtered_df['x_remate'], filtered_df['y_remate'],
                ax=ax, cmap='Reds', levels=50, alpha=0.7
            )
            ax.set_title("Zonas de Remate", fontsize=14, pad=20)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Error generando heatmap de remates: {str(e)}")

    # ========== RANKINGS DE JUGADORES ==========
    st.header("🏅 Rankings de Jugadores")
    
    if not filtered_df.empty:
        player_stats = filtered_df.groupby('Ejecutor').agg(
            Acciones=('Acción', 'count'),
            Goles=('Gol', lambda x: sum(x == 'Sí')),
            xG=('xG', 'sum'),
            Precisión=('Precisión', 'mean')
        ).reset_index()
        
        # Top 5 en diferentes métricas
        metrics = {
            'Goles': ('Goles Directos', 'Viridis'),
            'xG': ('xG Generado', 'Plasma'),
            'Precisión': ('Precisión (%)', 'Rainbow')
        }
        
        cols = st.columns(3)
        for (metric, (title, color)), col in zip(metrics.items(), cols):
            with col:
                top_players = player_stats.nlargest(5, metric)
                fig = px.bar(
                    top_players,
                    x='Ejecutor',
                    y=metric,
                    title=title,
                    color=metric,
                    color_continuous_scale=color
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar rankings")

    # ========== ANÁLISIS DE OPONENTES ==========
    st.header("🆚 Análisis de Oponentes")
    
    if not filtered_df.empty:
        opponent_analysis = filtered_df.groupby('Rival').agg(
            Acciones_Contra=('Acción', 'count'),
            Goles_Recibidos=('Gol', lambda x: sum(x == 'Sí')),
            Zona_Peligrosa=('Zona Remate', lambda x: x.mode()[0])
        ).reset_index()
        
        fig = px.treemap(
            opponent_analysis,
            path=['Rival'],
            values='Acciones_Contra',
            color='Goles_Recibidos',
            color_continuous_scale='Reds',
            title='Vulnerabilidad Defensiva por Oponente'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tabla interactiva
        st.subheader("Tabla Detallada de Oponentes")
        st.dataframe(
            opponent_analysis.sort_values('Goles_Recibidos', ascending=False),
            column_config={
                "Rival": "Oponente",
                "Acciones_Contra": st.column_config.NumberColumn("Acciones Contra"),
                "Goles_Recibidos": st.column_config.NumberColumn("Goles Recibidos"),
                "Zona_Peligrosa": st.column_config.TextColumn("Zona Más Peligrosa")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.warning("No hay datos para análisis de oponentes")

    # ========== SEGMENTACIÓN TEMPORAL ==========
    st.header("⏳ Evolución Temporal")
    
    time_analysis = filtered_df.resample('W', on='Fecha').agg({
        'Acción': 'count',
        'Gol': lambda x: sum(x == 'Sí'),
        'xG': 'sum'
    }).reset_index()
    
    fig = px.line(
        time_analysis,
        x='Fecha',
        y=['Acción', 'Gol', 'xG'],
        title="Tendencias Semanales",
        labels={'value': 'Cantidad', 'variable': 'Métrica'},
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("No se pudo cargar el dataset desde GitHub. Verifica la URL del archivo.")

# Estilos CSS personalizados
st.markdown("""
<style>
    .stMetric {background-color: #f8f9fa; border-radius: 10px; padding: 20px;}
    .stMetric label {font-size: 1.2rem!important; color: #2c3e50!important;}
    .stPlotlyChart {border: 1px solid #e0e0e0; border-radius: 10px;}
    .stHeader {color: #2c3e50;}
</style>
""", unsafe_allow_html=True)