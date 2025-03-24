# modules/analitica.py
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from mplsoccer import VerticalPitch

def analitica_page():
    st.set_page_config(layout="wide")
    st.title("⚽ Panel de Análisis Táctico Profesional")
    
    # Cargar datos
    try:
        df = load_data()
        if df.empty:
            st.error("El dataset está vacío")
            return
    except Exception as e:
        st.error(f"Error cargando datos: {str(e)}")
        return

    # Sidebar con filtros
    df_filtered = setup_filters(df)
    
    # Sección de KPI
    display_kpis(df_filtered)
    
    # Análisis espacial
    st.header("Análisis Espacial")
    spatial_tab1, spatial_tab2 = st.tabs(["🗺️ Heatmaps", "📍 Zonas Clave"])
    with spatial_tab1:
        generate_heatmaps(df_filtered)
    with spatial_tab2:
        generate_zones_analysis(df_filtered)
    
    # Análisis temporal
    st.header("⏳ Análisis Temporal")
    temporal_col1, temporal_col2 = st.columns(2)
    with temporal_col1:
        plot_timeline(df_filtered)
    with temporal_col2:
        plot_action_evolution(df_filtered)
    
    # Análisis de efectividad
    st.header("🎯 Análisis de Efectividad")
    effectiveness_col1, effectiveness_col2 = st.columns(2)
    with effectiveness_col1:
        plot_success_rates(df_filtered)
    with effectiveness_col2:
        plot_player_contribution(df_filtered)
    
    # Descarga de datos
    st.divider()
    setup_data_download(df_filtered)

def load_data():
    url = "https://raw.githubusercontent.com/felipeorma/abp/refs/heads/main/master_abp.csv"
    df = pd.read_csv(url)
    
    # Limpieza básica
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    df['Periodo'] = df['Periodo'].str.upper()
    
    return df

def setup_filters(df):
    with st.sidebar:
        st.header("🔍 Filtros Avanzados")
        
        # Filtros temporales
        min_date = df['Fecha'].min().date()
        max_date = df['Fecha'].max().date()
        date_range = st.date_input("Rango de fechas", [min_date, max_date])
        
        # Filtros categóricos
        selected_teams = st.multiselect("Equipos", df['Equipo'].unique(), default=df['Equipo'].unique())
        selected_players = st.multiselect("Jugadores", df['Ejecutor'].unique(), default=df['Ejecutor'].unique())
        action_types = st.multiselect("Tipos de acción", df['Acción'].unique(), default=df['Acción'].unique())
        
        # Filtros tácticos
        st.subheader("Filtros Tácticos")
        col1, col2 = st.columns(2)
        with col1:
            strategies = st.multiselect("Estrategias", df['Estrategia'].unique(), default=df['Estrategia'].unique())
        with col2:
            results = st.multiselect("Resultados", df['Resultado'].unique(), default=df['Resultado'].unique())
    
    # Aplicar filtros
    mask = (
        df['Equipo'].isin(selected_teams) &
        df['Ejecutor'].isin(selected_players) &
        df['Acción'].isin(action_types) &
        df['Estrategia'].isin(strategies) &
        df['Resultado'].isin(results) &
        (df['Fecha'].dt.date >= date_range[0]) &
        (df['Fecha'].dt.date <= date_range[1])
    )
    
    return df[mask]

def display_kpis(df):
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        total_actions = df.shape[0]
        st.metric("Acciones Registradas", total_actions)
    
    with kpi2:
        goals = df[df['Gol'] == 'Sí'].shape[0]
        st.metric("Goles Convertidos", goals)
    
    with kpi3:
        efficiency = (goals / total_actions * 100) if total_actions > 0 else 0
        st.metric("Efectividad (%)", f"{efficiency:.1f}%")
    
    with kpi4:
        avg_time = df['Minuto'].mean()
        st.metric("Minuto Promedio", f"{avg_time:.1f}'")

def generate_heatmaps(df):
    zonas_coords = {
        1: (120, 0), 2: (120, 80), 3: (93, 9), 4: (93, 71),
        5: (114, 30), 6: (114, 50), 7: (114, 40), 8: (111, 15),
        9: (111, 65), 10: (105, 35), 11: (105, 45), 12: (105, 25),
        13: (105, 55), 14: (93, 29), 15: (93, 51), 16: (72, 20),
        17: (72, 60), "Penal": (108, 40)
    }
    
    # Procesamiento seguro de coordenadas
    plot_df = df.copy()
    plot_df['x_saque'] = plot_df['Zona Saque'].map(lambda z: zonas_coords.get(z, (None, None))[0].astype(float)
    plot_df['y_saque'] = plot_df['Zona Saque'].map(lambda z: zonas_coords.get(z, (None, None))[1].astype(float)
    plot_df = plot_df.dropna(subset=['x_saque', 'y_saque'])
    
    # Configuración del pitch
    pitch = VerticalPitch(
        pitch_type='statsbomb',
        pitch_color='#1d3649',
        line_color='#dee6ea',
        half=True,
        goal_type='box',
        linewidth=1.2
    )
    
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch.draw(ax=ax)
    
    # Parámetros profesionales
    kde_args = {
        'cmap': 'plasma',
        'levels': 200,
        'fill': True,
        'alpha': 0.7,
        'bw_adjust': 0.15,
        'thresh': 0.05
    }
    
    # Heatmap de densidad
    pitch.kdeplot(
        plot_df['x_saque'],
        plot_df['y_saque'],
        ax=ax,
        **kde_args
    )
    
    # Configuración estética
    ax.set_title('Distribución Espacial de Acciones Ofensivas', 
                color='white', 
                fontsize=16, 
                pad=20)
    ax.set_facecolor('#1d3649')
    
    st.pyplot(fig)

def generate_zones_analysis(df):
    zone_counts = df.groupby('Zona Remate')['Gol'].agg(['count', lambda x: (x == 'Sí').sum()])
    zone_counts.columns = ['Acciones', 'Goles']
    zone_counts['Efectividad'] = (zone_counts['Goles'] / zone_counts['Acciones'] * 100).round(1)
    zone_counts = zone_counts.sort_values('Efectividad', ascending=False)
    
    fig = px.bar(
        zone_counts,
        x=zone_counts.index.astype(str),
        y='Efectividad',
        color='Acciones',
        title='Efectividad por Zona de Remate',
        labels={'x': 'Zona', 'y': 'Efectividad (%)'},
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_timeline(df):
    timeline = df.groupby(pd.Grouper(key='Fecha', freq='W'))['Gol'].count().reset_index()
    fig = px.line(
        timeline,
        x='Fecha',
        y='Gol',
        title='Evolución Temporal de Acciones Ofensivas',
        labels={'Gol': 'Acciones por Semana'}
    )
    fig.update_layout(
        xaxis_title='Fecha',
        yaxis_title='Número de Acciones',
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_action_evolution(df):
    period_actions = df.groupby(['Periodo', 'Acción']).size().unstack().fillna(0)
    fig = px.bar(
        period_actions,
        barmode='group',
        title='Distribución de Acciones por Periodo',
        labels={'value': 'Cantidad', 'Periodo': 'Periodo'}
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_success_rates(df):
    success_rates = df.groupby('Acción').apply(
        lambda x: pd.Series({
            'Éxito': (x['Resultado'] == 'Gol').sum(),
            'Total': x.shape[0]
        })
    ).reset_index()
    success_rates['Tasa'] = (success_rates['Éxito'] / success_rates['Total'] * 100).round(1)
    
    fig = px.scatter(
        success_rates,
        x='Total',
        y='Tasa',
        size='Éxito',
        color='Acción',
        title='Efectividad por Tipo de Acción',
        labels={'Total': 'Acciones Totales', 'Tasa': '% de Éxito'}
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_player_contribution(df):
    top_players = df.groupby('Ejecutor').agg(
        Acciones=('Ejecutor', 'count'),
        Goles=('Gol', lambda x: (x == 'Sí').sum())
    ).nlargest(10, 'Acciones')
    
    fig = px.bar(
        top_players,
        x=top_players.index,
        y=['Acciones', 'Goles'],
        title='Top 10 Jugadores: Acciones vs Goles',
        labels={'value': 'Cantidad', 'variable': 'Métrica'}
    )
    st.plotly_chart(fig, use_container_width=True)

def setup_data_download(df):
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Dataset Filtrado",
        data=csv,
        file_name='analisis_tactico.csv',
        mime='text/csv',
        help="Descarga los datos actualmente filtrados en formato CSV"
    )
