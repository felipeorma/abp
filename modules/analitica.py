# modules/analitica.py
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from mplsoccer import VerticalPitch
from datetime import datetime
import requests
from io import BytesIO

def cargar_datos():
    try:
        url = "https://raw.githubusercontent.com/felipeorma/abp/main/master_abp.csv"
        df = pd.read_csv(url)
        
        # Renombrar columnas para estandarizar
        df = df.rename(columns={
            'Tipo Ejecución': 'Tipo Acción',
            'Primer Contacto': 'Contacto',
            'Parte Cuerpo': 'Parte_Cuerpo'
        })
        
        # Columnas obligatorias
        columnas_requeridas = [
            'Jornada', 'Rival', 'Periodo', 'Minuto', 'Acción', 'Equipo', 'Fecha',
            'Gol', 'Contacto', 'Tipo Acción', 'Zona Saque', 'Zona Remate', 'Ejecutor', 'Parte_Cuerpo'
        ]
        
        # Verificar estructura
        faltantes = [col for col in columnas_requeridas if col not in df.columns]
        if faltantes:
            st.error(f"Columnas faltantes: {', '.join(faltantes)}")
            return pd.DataFrame()

        # Conversión de tipos de datos
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df['Minuto'] = pd.to_numeric(df['Minuto'], errors='coerce')
        df['Gol'] = df['Gol'].apply(lambda x: 'Sí' if str(x).lower() in ['sí', 'si', '1', 'true'] else 'No')
        
        return df.dropna(subset=['Zona Saque', 'Zona Remate', 'Ejecutor', 'Fecha'])
    
    except Exception as e:
        st.error(f"Error cargando datos: {str(e)}")
        return pd.DataFrame()

def configurar_filtros(df):
    with st.sidebar:
        st.header("🔍 Filtros Avanzados")
        
        # Filtro de fechas compacto
        fechas_disponibles = df['Fecha'].dt.strftime('%Y-%m-%d').sort_values(ascending=False).unique()
        fechas_sel = st.multiselect(
            "Seleccionar fechas",
            options=fechas_disponibles,
            default=fechas_disponibles,
            help="Selecciona una o varias fechas"
        )
        
        # Filtros principales en columnas
        col1, col2 = st.columns(2)
        with col1:
            equipos = st.multiselect(
                "Equipo",
                options=df['Equipo'].unique(),
                default=['Cavalry FC', 'Rival']
            )
        with col2:
            acciones = st.multiselect(
                "Acciones",
                options=df['Acción'].unique(),
                default=df['Acción'].unique()
            )
            
        # Filtros secundarios
        jugadores = st.multiselect(
            "Jugadores",
            options=df['Ejecutor'].unique(),
            default=df['Ejecutor'].unique()
        )
        
        # Rango de minutos
        min_min = int(df['Minuto'].min())
        max_min = int(df['Minuto'].max())
        rango_minutos = st.slider(
            "Rango de minutos",
            min_min, max_min,
            (min_min, max_min)
        )

    return df[
        (df['Fecha'].dt.strftime('%Y-%m-%d').isin(fechas_sel)) &
        (df['Equipo'].isin(equipos)) &
        (df['Acción'].isin(acciones)) &
        (df['Ejecutor'].isin(jugadores)) &
        (df['Minuto'].between(*rango_minutos))
    ]

def mostrar_kpis_mejorados(df):
    cols = st.columns(4)
    
    # Goles a favor del equipo seleccionado
    equipo_seleccionado = 'Rival' if 'Rival' in df['Equipo'].unique() else 'Cavalry FC'
    goles_favor = df[(df['Gol'] == 'Sí') & (df['Equipo'] == equipo_seleccionado)].shape[0]
    with cols[0]:
        st.metric(f"✅ Goles a favor ({equipo_seleccionado})", goles_favor)
    
    # Goles en contra (opuesto al equipo seleccionado)
    equipo_contrario = 'Cavalry FC' if equipo_seleccionado == 'Rival' else 'Rival'
    goles_contra = df[(df['Gol'] == 'Sí') & (df['Equipo'] == equipo_contrario)].shape[0]
    with cols[1]:
        st.metric(f"❌ Goles en contra ({equipo_contrario})", goles_contra)
    
    # Efectividad
    acciones_totales = df[df['Equipo'] == equipo_seleccionado].shape[0]
    with cols[2]:
        eficacia = (goles_favor / acciones_totales * 100) if acciones_totales > 0 else 0
        st.metric("🎯 Efectividad", f"{eficacia:.1f}%")
    
    # Contactos totales
    with cols[3]:
        contactos = df['Parte_Cuerpo'].count()
        st.metric("👣 Contactos", contactos)

def generar_seccion_espacial(df):
    st.header("🌍 Mapeo Táctico")
    
    if df.empty:
        st.warning("No hay datos para generar mapas de calor")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Zonas de Saque")
        generar_mapa_calor(df, tipo='saque')
    
    with col2:
        st.subheader("Zonas de Remate")
        generar_mapa_calor(df, tipo='remate')

def generar_mapa_calor(df, tipo='saque'):
    zonas_coords = {
        1: (120, 0), 2: (120, 80), 3: (93, 9), 4: (93, 71),
        5: (114, 30), 6: (114, 50), 7: (114, 40), 8: (111, 15),
        9: (111, 65), 10: (105, 35), 11: (105, 45), 12: (105, 25),
        13: (105, 55), 14: (93, 29), 15: (93, 51), 16: (72, 20),
        17: (72, 60), "Penal": (108, 40)
    }
    
    coord_col = 'x_saque' if tipo == 'saque' else 'x_remate'
    y_col = 'y_saque' if tipo == 'saque' else 'y_remate'
    
    # Crear DataFrame con coordenadas
    df_coords = df[[coord_col, y_col]].dropna()
    df_coords.columns = ['x', 'y']
    
    if df_coords.empty:
        st.warning(f"No hay datos válidos para {tipo}s")
        return
    
    # Configurar el campo
    pitch = VerticalPitch(pitch_type='statsbomb', half=True, goal_type='box')
    fig, ax = plt.subplots(figsize=(10, 7))
    pitch.draw(ax=ax)
    
    # Heatmap
    pitch.kdeplot(
        df_coords['x'], df_coords['y'],
        ax=ax,
        cmap='Greens' if tipo == 'saque' else 'Reds',
        levels=100,
        fill=True,
        alpha=0.7
    )
    
    st.pyplot(fig)
    plt.close()

def generar_seccion_mejores_jugadores(df):
    st.header("🏆 Mejores Jugadores por Contactos")
    
    if 'Parte_Cuerpo' not in df.columns:
        st.warning("No hay datos de contactos disponibles")
        return
    
    # Contar contactos por jugador
    df_contactos = df.groupby(['Equipo', 'Ejecutor'])['Parte_Cuerpo'].count().reset_index()
    df_contactos = df_contactos.sort_values('Parte_Cuerpo', ascending=False).head(10)
    
    fig = px.bar(
        df_contactos,
        x='Ejecutor',
        y='Parte_Cuerpo',
        color='Equipo',
        title="Top 10 Jugadores por Contactos",
        labels={'Parte_Cuerpo': 'Número de contactos', 'Ejecutor': 'Jugador'},
        color_discrete_map={'Cavalry FC': '#FF0000', 'Rival': '#000000'}
    )
    st.plotly_chart(fig, use_container_width=True)

def analitica_page():
    st.title("⚽ Panel de Análisis Táctico")
    
    df = cargar_datos()
    if df.empty:
        st.warning("No hay datos disponibles. Verifica la conexión o el archivo CSV.")
        return
    
    df_filtrado = configurar_filtros(df)
    
    if df_filtrado.empty:
        st.warning("No hay datos con los filtros seleccionados")
        return
    
    mostrar_kpis_mejorados(df_filtrado)
    generar_seccion_espacial(df_filtrado)
    generar_seccion_mejores_jugadores(df_filtrado)
