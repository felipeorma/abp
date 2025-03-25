# modules/analitica.py
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from mplsoccer import VerticalPitch
from datetime import datetime

def analitica_page():
    st.title("⚽ Panel de Análisis Táctico Profesional")
    
    try:
        df = cargar_datos()
        if df.empty:
            st.warning("¡Base de datos vacía! Registra acciones en el módulo de Registro")
            return
    except Exception as e:
        st.error(f"Error crítico: {str(e)}")
        return

    df_filtrado = configurar_filtros(df)
    mostrar_kpis(df_filtrado)
    generar_seccion_espacial(df_filtrado)
    generar_seccion_temporal(df_filtrado)
    generar_seccion_efectividad(df_filtrado)
    configurar_descarga(df_filtrado)

def cargar_datos():
    # Cargar datos desde GitHub
    url = "https://raw.githubusercontent.com/felipeorma/abp/refs/heads/main/master_abp.csv"
    df = pd.read_csv(url)
    
    # Convertir y validar fecha
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    df = df.dropna(subset=['Fecha'])
    
    # Validar estructura del CSV
    columnas_requeridas = ['Jornada', 'Rival', 'Periodo', 'Minuto', 'Acción', 'Equipo', 'Fecha']
    if not all(col in df.columns for col in columnas_requeridas):
        st.error("Estructura inválida del CSV")
        return pd.DataFrame()
    
    # Limpieza de datos
    df['Minuto'] = pd.to_numeric(df['Minuto'], errors='coerce')
    return df.dropna(subset=['Zona Saque', 'Zona Remate', 'Ejecutor'])

def configurar_filtros(df):
    with st.sidebar:
        st.header("🔍 Filtros Avanzados")
        
        # Filtro de fechas
        min_date = df['Fecha'].min().date()
        max_date = df['Fecha'].max().date()
        selected_dates = st.date_input(
            "Rango de fechas",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Manejar selección de rango
        if len(selected_dates) == 2:
            start_date, end_date = selected_dates
        else:
            start_date = end_date = selected_dates[0]

        # Filtros principales
        col1, col2 = st.columns(2)
        with col1:
            jornadas = st.multiselect(
                "Jornadas",
                options=df['Jornada'].unique(),
                default=df['Jornada'].unique()
            )
        with col2:
            condicion = st.multiselect(
                "Local/Visitante",
                options=df['Condición'].unique(),
                default=df['Condición'].unique()
            )
        
        # Filtros tácticos
        col3, col4 = st.columns(2)
        with col3:
            equipos = st.multiselect(
                "Equipos", 
                options=df['Equipo'].unique(),
                default=df['Equipo'].unique()
            )
        with col4:
            rivals = st.multiselect(
                "Rivales",
                options=df['Rival'].unique(),
                default=df['Rival'].unique()
            )

        # Filtros adicionales
        jugadores = st.multiselect(
            "Jugadores",
            options=df['Ejecutor'].unique(),
            default=df['Ejecutor'].unique()
        )
        
        acciones = st.multiselect(
            "Tipos de acción",
            options=df['Acción'].unique(),
            default=df['Acción'].unique()
        )
        
        # Filtro temporal
        min_minuto = int(df['Minuto'].min())
        max_minuto = int(df['Minuto'].max())
        rango_minutos = st.slider(
            "Rango de minutos (partido)",
            min_minuto, max_minuto,
            (min_minuto, max_minuto)
        )

    return df[
        (df['Jornada'].isin(jornadas)) &
        (df['Condición'].isin(condicion)) &
        (df['Equipo'].isin(equipos)) &
        (df['Rival'].isin(rivals)) &
        (df['Ejecutor'].isin(jugadores)) &
        (df['Acción'].isin(acciones)) &
        (df['Minuto'].between(*rango_minutos)) &
        (df['Fecha'].dt.date >= start_date) &
        (df['Fecha'].dt.date <= end_date)
    ]

def mostrar_kpis(df):
    cols = st.columns(4)
    
    with cols[0]:
        st.metric("📈 Acciones registradas", df.shape[0])
    
    # Goles a favor (Cavalry FC)
    goles_favor = df[(df['Gol'] == 'Sí') & (df['Equipo'] == 'Cavalry FC')].shape[0]
    with cols[1]:
        st.metric("✅ Goles a favor", goles_favor, 
                 help="Goles convertidos por Cavalry FC",
                 delta_color="off")
    
    # Goles en contra (Rival)
    goles_contra = df[(df['Gol'] == 'Sí') & (df['Equipo'] == 'Rival')].shape[0]
    with cols[2]:
        st.metric("❌ Goles en contra", goles_contra, 
                 help="Goles concedidos al rival",
                 delta_color="off")
    
    # Efectividad basada en goles a favor
    with cols[3]:
        eficacia = (goles_favor / df.shape[0] * 100) if df.shape[0] > 0 else 0
        st.metric("🎯 Efectividad", f"{eficacia:.1f}%")

def generar_seccion_espacial(df):
    st.header("🌍 Mapeo Táctico")
    col1, col2 = st.columns(2)
    
    with col1:
        generar_mapa_calor(df, tipo='saque')
    with col2:
        generar_mapa_calor(df, tipo='remate')

def generar_mapa_calor(df, tipo='saque'):
    zonas_coords = {
        1: (120, 0), 2: (120, 80), 3: (93, 9), 4: (93, 71),
        5: (114, 30), 6: (114, 50), 7: (114, 40), 8: (111, 15),
        9: (111, 65), 10: (105, 35), 11: (105, 45), 12: (105, 25),
        13: (105, 55), 14: (93, 29), 15: (93, 51), 16: (72, 20),
        17: (72, 60), "Penal": (108, 40)
    }
    
    coord_col = 'Zona Saque' if tipo == 'saque' else 'Zona Remate'
    
    # Convertir zonas y filtrar válidas
    df_temp = df.copy()
    df_temp[coord_col] = df_temp[coord_col].apply(
        lambda x: int(x) if str(x).isdigit() else x
    )
    df_coords = df_temp[coord_col].map(zonas_coords).dropna().apply(pd.Series)
    
    if df_coords.empty:
        st.warning(f"No hay datos válidos para {tipo}s")
        return
    
    df_coords.columns = ['x', 'y']
    
    # Configuración profesional del pitch
    pitch = VerticalPitch(
        pitch_type='statsbomb',
        pitch_color='grass',
        line_color='white',
        linewidth=1.2,
        half=True,
        goal_type='box'
    )
    
    fig, ax = plt.subplots(figsize=(12, 8))
    pitch.draw(ax=ax)
    
    # Parámetros clave para heatmaps
    pitch.kdeplot(
        df_coords['x'], df_coords['y'],
        ax=ax,
        cmap='Greens' if tipo == 'saque' else 'Reds',
        levels=100,
        fill=True,
        alpha=0.75,
        bw_adjust=0.65,
        zorder=2
    )
    
    # Título profesional
    ax.set_title(f"Densidad de {tipo.capitalize()}s", 
                fontsize=16, 
                pad=20,
                fontweight='bold')
    
    st.pyplot(fig)
    plt.close()

def generar_seccion_temporal(df):
    st.header("⏳ Evolución Temporal")
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.histogram(
            df, x='Jornada', color='Periodo',
            title="Acciones por Jornada",
            labels={'count': 'Acciones'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        fig = px.box(
            df, x='Acción', y='Minuto',
            color='Equipo', 
            title="Distribución de minutos por acción",
            points="all"
        )
        st.plotly_chart(fig, use_container_width=True)

def generar_seccion_efectividad(df):
    st.header("🎯 Efectividad Operativa")
    col1, col2 = st.columns(2)
    
    with col1:
        df_efectividad = df.groupby('Ejecutor').agg(
            Acciones=('Ejecutor', 'count'),
            Goles=('Gol', lambda x: (x == 'Sí').sum())
        ).reset_index()
        fig = px.scatter(
            df_efectividad, 
            x='Acciones', y='Goles',
            size='Goles', color='Ejecutor',
            title="Relación Acciones-Goles por Jugador"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.sunburst(
            df, path=['Acción', 'Resultado'],
            title="Composición de Resultados por Acción"
        )
        st.plotly_chart(fig, use_container_width=True)

def configurar_descarga(df):
    st.divider()
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📤 Exportar Dataset Filtrado",
        data=csv,
        file_name="analisis_tactico.csv",
        mime="text/csv",
        help="Descarga los datos actualmente filtrados en formato CSV"
    )
