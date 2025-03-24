import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_github_data

def analitica_page():
    st.title("📊 Panel Analítico Avanzado")
    
    # Cargar datos desde GitHub
    try:
        url = "https://raw.githubusercontent.com/felipeorma/abp/refs/heads/main/master_abp.csv"
        df = pd.read_csv(url)
        df = df.dropna(subset=['Zona Saque', 'Zona Remate'])
    except Exception as e:
        st.error(f"Error cargando datos: {str(e)}")
        return

    # Sección de Filtros
    with st.sidebar.expander("🔍 FILTROS AVANZADOS", expanded=True):
        # Filtros temporales
        jornadas = st.multiselect(
            "Jornadas",
            options=df['Jornada'].unique(),
            default=df['Jornada'].unique()
        )
        
        # Filtros de equipo
        equipos = st.multiselect(
            "Equipos",
            options=df['Equipo'].unique(),
            default=df['Equipo'].unique()
        )
        
        # Filtros tácticos
        tipo_accion = st.multiselect(
            "Tipo de acción",
            options=df['Acción'].unique(),
            default=df['Acción'].unique()
        )
        
        # Filtro de resultado
        resultados = st.multiselect(
            "Resultados",
            options=df['Resultado'].unique(),
            default=df['Resultado'].unique()
        )

    # Aplicar filtros
    filtered_df = df[
        (df['Jornada'].isin(jornadas)) &
        (df['Equipo'].isin(equipos)) &
        (df['Acción'].isin(tipo_accion)) &
        (df['Resultado'].isin(resultados))
    ]

    # Mostrar estadísticas rápidas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Acciones", filtered_df.shape[0])
    with col2:
        goles = filtered_df[filtered_df['Gol'] == 'Sí'].shape[0]
        st.metric("Goles Marcados", goles)
    with col3:
        eficiencia = (goles / filtered_df.shape[0]) * 100 if filtered_df.shape[0] > 0 else 0
        st.metric("Eficiencia (%)", f"{eficiencia:.1f}%")

    # Sección de Heatmaps
    st.header("Análisis Espacial")
    generar_heatmaps_analitica(filtered_df)

    # Análisis adicional
    st.header("📈 Métricas Clave")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribución de Resultados")
        fig = px.pie(filtered_df, names='Resultado', hole=0.3)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Acciones por Jugador")
        top_jugadores = filtered_df['Ejecutor'].value_counts().head(5)
        st.bar_chart(top_jugadores)

def generar_heatmaps_analitica(df):
    zonas_coords = {
        1: (120, 0), 2: (120, 80), 3: (93, 9), 4: (93, 71),
        5: (114, 30), 6: (114, 50), 7: (114, 40), 8: (111, 15),
        9: (111, 65), 10: (105, 35), 11: (105, 45), 12: (105, 25),
        13: (105, 55), 14: (93, 29), 15: (93, 51), 16: (72, 20),
        17: (72, 60), "Penal": (108, 40)
    }

    # Procesamiento de coordenadas
    df = df.copy()
    df["coords_saque"] = df["Zona Saque"].map(zonas_coords)
    df["coords_remate"] = df["Zona Remate"].map(zonas_coords)
    
    df[["x_saque", "y_saque"]] = pd.DataFrame(df["coords_saque"].tolist(), index=df.index)
    df[["x_remate", "y_remate"]] = pd.DataFrame(df["coords_remate"].tolist(), index=df.index)

    # Configuración de visualización mejorada
    pitch = VerticalPitch(
        pitch_type='statsbomb',
        pitch_color='grass',
        line_color='white',
        half=True,
        goal_type='box',
        linewidth=1.2
    )

    # Parámetros optimizados para análisis
    heatmap_params = {
        'cmap': 'YlGnBu',
        'levels': 150,
        'fill': True,
        'alpha': 0.8,
        'bw_adjust': 0.1,
        'thresh': 0.05,
        'zorder': 2
    }

    # Heatmaps interactivos
    tab1, tab2 = st.tabs(["🗺️ Heatmap de Saques", "🎯 Heatmap de Remates"])
    
    with tab1:
        fig, ax = plt.subplots(figsize=(12, 8))
        pitch.draw(ax=ax)
        pitch.kdeplot(df['x_saque'], df['y_saque'], ax=ax, **heatmap_params)
        ax.set_title("Distribución de Saques", fontsize=16, pad=15)
        st.pyplot(fig)
    
    with tab2:
        fig, ax = plt.subplots(figsize=(12, 8))
        pitch.draw(ax=ax)
        pitch.kdeplot(df['x_remate'], df['y_remate'], ax=ax, **heatmap_params)
        ax.set_title("Zonas de Remate", fontsize=16, pad=15)
        st.pyplot(fig)
