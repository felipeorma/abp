# modules/analitica.py
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from mplsoccer import VerticalPitch

def analitica_page():
    st.title("⚽ Panel de Análisis Táctico Profesional")
    
    try:
        df = cargar_datos()
        if df.empty:
            st.warning("No se encontraron datos en el repositorio. Verifica la conexión o el formato del CSV.")
            return
    except Exception as e:
        st.error(f"Error cargando datos: {str(e)}")
        return

    df_filtrado = configurar_filtros(df)
    mostrar_kpis(df_filtrado)
    generar_seccion_espacial(df_filtrado)
    generar_seccion_temporal(df_filtrado)
    generar_seccion_efectividad(df_filtrado)
    configurar_descarga(df_filtrado)

def cargar_datos():
    # Cargar datos directamente desde GitHub
    url = "https://raw.githubusercontent.com/felipeorma/abp/refs/heads/main/master_abp.csv"
    df = pd.read_csv(url)
    
    # Convertir tipos de datos y limpiar
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    df['Minuto'] = pd.to_numeric(df['Minuto'], errors='coerce')
    
    # Mantener solo registros completos
    return df.dropna(subset=['Zona Saque', 'Zona Remate', 'Ejecutor'])

def configurar_filtros(df):
    with st.sidebar:
        st.header("🔍 Filtros Avanzados")
        
        # Filtro de fechas
        date_col1, date_col2 = st.columns(2)
        with date_col1:
            fecha_min = st.date_input("Fecha inicial", value=df['Fecha'].min().date())
        with date_col2:
            fecha_max = st.date_input("Fecha final", value=df['Fecha'].max().date())
        
        # Selectores múltiples
        equipos = st.multiselect(
            "Equipos", 
            options=df['Equipo'].unique(),
            default=df['Equipo'].unique()
        )
        
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

    return df[
        (df['Equipo'].isin(equipos)) &
        (df['Ejecutor'].isin(jugadores)) &
        (df['Acción'].isin(acciones)) &
        (df['Fecha'].dt.date >= fecha_min) &
        (df['Fecha'].dt.date <= fecha_max)
    ]

def mostrar_kpis(df):
    cols = st.columns(4)
    with cols[0]:
        st.metric("Acciones registradas", df.shape[0])
    with cols[1]:
        goles = df[df['Gol'] == 'Sí'].shape[0]
        st.metric("Goles convertidos", goles)
    with cols[2]:
        eficacia = (goles/df.shape[0]*100) if df.shape[0] > 0 else 0
        st.metric("Eficacia (%)", f"{eficacia:.1f}%")
    with cols[3]:
        st.metric("Jugadores únicos", df['Ejecutor'].nunique())

def generar_seccion_espacial(df):
    st.header("🌍 Análisis Espacial")
    
    with st.spinner("Generando heatmaps..."):
        fig1, fig2 = generar_heatmaps(df)
        
    col1, col2 = st.columns(2)
    with col1:
        st.pyplot(fig1)
        st.caption("Heatmap de zonas de saque")
    with col2:
        st.pyplot(fig2)
        st.caption("Heatmap de zonas de remate")

def generar_heatmaps(df):
    zonas_coords = {
        1: (120, 0), 2: (120, 80), 3: (93, 9), 4: (93, 71),
        5: (114, 30), 6: (114, 50), 7: (114, 40), 8: (111, 15),
        9: (111, 65), 10: (105, 35), 11: (105, 45), 12: (105, 25),
        13: (105, 55), 14: (93, 29), 15: (93, 51), 16: (72, 20),
        17: (72, 60), "Penal": (108, 40)
    }
    
    # Corrección clave del error de sintaxis
    df = df.copy()
    df['x_saque'] = df['Zona Saque'].map(lambda z: zonas_coords.get(z, (None, None))[0])
    df['y_saque'] = df['Zona Saque'].map(lambda z: zonas_coords.get(z, (None, None))[1])
    df['x_remate'] = df['Zona Remate'].map(lambda z: zonas_coords.get(z, (None, None))[0])
    df['y_remate'] = df['Zona Remate'].map(lambda z: zonas_coords.get(z, (None, None))[1])
    
    df = df.dropna(subset=['x_saque', 'y_saque', 'x_remate', 'y_remate'])

    pitch = VerticalPitch(
        pitch_type='statsbomb',
        pitch_color='grass',
        line_color='white',
        half=True,
        goal_type='box'
    )

    # Heatmap de saques
    fig1, ax1 = plt.subplots(figsize=(12, 8))
    pitch.draw(ax1)
    pitch.kdeplot(
        df['x_saque'], df['y_saque'],
        ax=ax1, cmap='Greens', levels=100, alpha=0.7, bw_adjust=0.1
    )
    ax1.set_title("Distribución de Saques", fontsize=16)

    # Heatmap de remates
    fig2, ax2 = plt.subplots(figsize=(12, 8))
    pitch.draw(ax2)
    pitch.kdeplot(
        df['x_remate'], df['y_remate'],
        ax=ax2, cmap='Reds', levels=100, alpha=0.7, bw_adjust=0.1
    )
    ax2.set_title("Zonas de Remate", fontsize=16)

    return fig1, fig2

def generar_seccion_temporal(df):
    st.header("⏳ Análisis Temporal")
    
    # Evolución temporal
    timeline = df.resample('W', on='Fecha').size()
    fig1 = px.line(
        timeline, 
        title="Acciones por semana",
        labels={'value': 'Número de acciones'}
    )
    
    # Distribución por periodos
    fig2 = px.histogram(
        df, x='Periodo', color='Acción',
        title="Distribución por periodo",
        barmode='group'
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)

def generar_seccion_efectividad(df):
    st.header("🎯 Análisis de Efectividad")
    
    # Efectividad por zona
    efectividad_zona = df.groupby('Zona Remate')['Gol'].agg(['count', 'mean'])
    fig1 = px.bar(
        efectividad_zona, 
        x=efectividad_zona.index,
        y='mean',
        color='count',
        title="Efectividad por zona de remate"
    )
    
    # Top jugadores
    top_jugadores = df.groupby('Ejecutor').agg(
        Acciones=('Ejecutor', 'count'),
        Goles=('Gol', lambda x: (x == 'Sí').sum())
    ).nlargest(10, 'Acciones')
    fig2 = px.bar(
        top_jugadores,
        x=top_jugadores.index,
        y=['Acciones', 'Goles'],
        title="Top 10 jugadores"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig1, use_container_width=True)
    with col2:
        st.plotly_chart(fig2, use_container_width=True)

def configurar_descarga(df):
    st.divider()
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Descargar datos filtrados",
        data=csv,
        file_name="analisis_tactico.csv",
        mime="text/csv"
    )
