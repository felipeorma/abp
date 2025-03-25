# modules/analitica.py
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from mplsoccer import VerticalPitch
from datetime import datetime
import requests
from io import BytesIO

# =============================================
# FUNCIONES BASE
# =============================================

def cargar_datos():
    try:
        url = "https://raw.githubusercontent.com/felipeorma/abp/main/master_abp.csv"
        df = pd.read_csv(url)
        
        # Renombrar columnas problemáticas
        df = df.rename(columns={
            'Tipo Ejecución': 'Tipo Acción',
            'Primer Contacto': 'Contacto',
            'Parte Cuerpo': 'Parte_Cuerpo'
        })

        # Validar estructura del CSV
        columnas_requeridas = [
            'Jornada', 'Rival', 'Periodo', 'Minuto', 'Acción', 'Equipo', 'Fecha',
            'Gol', 'Contacto', 'Tipo Acción', 'Zona Saque', 'Zona Remate', 'Ejecutor',
            'x_saque', 'y_saque', 'x_remate', 'y_remate', 'Parte_Cuerpo'
        ]
        
        faltantes = [col for col in columnas_requeridas if col not in df.columns]
        if faltantes:
            st.error(f"🚨 Error en estructura del CSV. Faltan: {', '.join(faltantes)}")
            return pd.DataFrame()

        # Conversiones y limpieza
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df['Minuto'] = pd.to_numeric(df['Minuto'], errors='coerce')
        df['Gol'] = df['Gol'].apply(lambda x: 'Sí' if str(x).lower() in ['sí', 'si', '1', 'true'] else 'No')
        
        return df.dropna(subset=['Zona Saque', 'Zona Remate', 'Ejecutor', 'Fecha'])

    except Exception as e:
        st.error(f"⛔ Error crítico: {str(e)}")
        return pd.DataFrame()

# =============================================
# COMPONENTES DE INTERFAZ
# =============================================

def configurar_filtros(df):
    with st.sidebar:
        st.header("🔍 Filtros Tácticos")
        
        # Filtro de fechas compacto
        fechas_disponibles = df['Fecha'].dt.strftime('%d/%m/%Y').sort_values(ascending=False).unique()
        fechas_sel = st.multiselect(
            "Fechas de partidos",
            options=fechas_disponibles,
            default=fechas_disponibles,
            help="Selecciona uno o múltiples partidos"
        )
        
        # Filtros principales en columnas
        col1, col2 = st.columns(2)
        with col1:
            equipos = st.multiselect(
                "Equipo analizado",
                options=df['Equipo'].unique(),
                default=['Cavalry FC', 'Rival']
            )
        with col2:
            acciones = st.multiselect(
                "Tipo de acción",
                options=df['Acción'].unique(),
                default=df['Acción'].unique()
            )

        # Filtros secundarios
        jugadores = st.multiselect(
            "Jugadores clave",
            options=df['Ejecutor'].unique(),
            default=df['Ejecutor'].unique()
        )

        # Rango temporal adaptativo
        min_min = int(df['Minuto'].min())
        max_min = int(df['Minuto'].max())
        rango_minutos = st.slider(
            "Minutos clave del partido",
            min_min, max_min,
            (min_min, max_min)
        )

    return df[
        (df['Fecha'].dt.strftime('%d/%m/%Y').isin(fechas_sel)) &
        (df['Equipo'].isin(equipos)) &
        (df['Acción'].isin(acciones)) &
        (df['Ejecutor'].isin(jugadores)) &
        (df['Minuto'].between(*rango_minutos))
    ]

# =============================================
# MÓDULOS DE VISUALIZACIÓN
# =============================================

def mostrar_kpis_estrategicos(df):
    cols = st.columns(4)
    
    # Dinámica de equipos
    equipo_analizado = 'Rival' if 'Rival' in df['Equipo'].unique() else 'Cavalry FC'
    contrario = 'Cavalry FC' if equipo_analizado == 'Rival' else 'Rival'
    
    with cols[0]:
        goles_favor = df[(df['Gol'] == 'Sí') & (df['Equipo'] == equipo_analizado)].shape[0]
        st.metric(f"✅ Goles {equipo_analizado}", goles_favor)
    
    with cols[1]:
        goles_contra = df[(df['Gol'] == 'Sí') & (df['Equipo'] == contrario)].shape[0]
        st.metric(f"❌ Goles {contrario}", goles_contra)
    
    with cols[2]:
        acciones_ofensivas = df[df['Equipo'] == equipo_analizado].shape[0]
        eficacia = (goles_favor / acciones_ofensivas * 100) if acciones_ofensivas > 0 else 0
        st.metric("🎯 Efectividad Ofensiva", f"{eficacia:.1f}%")
    
    with cols[3]:
        contactos = df['Parte_Cuerpo'].nunique()
        st.metric("👥 Diversidad de Contactos", contactos)

def generar_mapa_calor(df, tipo='saque'):
    zonas_coords = {
        1: (120, 0), 2: (120, 80), 3: (93, 9), 4: (93, 71),
        5: (114, 30), 6: (114, 50), 7: (114, 40), 8: (111, 15),
        9: (111, 65), 10: (105, 35), 11: (105, 45), 12: (105, 25),
        13: (105, 55), 14: (93, 29), 15: (93, 51), 16: (72, 20),
        17: (72, 60), "Penal": (108, 40)
    }
    
    # Configurar coordenadas según tipo
    coord_x = 'x_saque' if tipo == 'saque' else 'x_remate'
    coord_y = 'y_saque' if tipo == 'saque' else 'y_remate'
    
    df_coords = df[[coord_x, coord_y]].dropna()
    df_coords.columns = ['x', 'y']
    
    if df_coords.empty:
        st.warning(f"⚠️ Sin datos para {tipo}s")
        return

    # Configurar visualización profesional
    pitch = VerticalPitch(
        pitch_type='statsbomb',
        pitch_color='grass',
        line_color='white',
        half=True
    )
    
    fig, ax = plt.subplots(figsize=(10, 7))
    pitch.draw(ax=ax)
    
    # Heatmap mejorado
    pitch.kdeplot(
        df_coords['x'], df_coords['y'],
        ax=ax,
        cmap='plasma' if tipo == 'saque' else 'viridis',
        levels=50,
        fill=True,
        alpha=0.8
    )
    
    ax.set_title(f"Mapa de Calor - {tipo.capitalize()}s", fontsize=14, pad=15)
    st.pyplot(fig)
    plt.close()

def analizar_contactos(df):
    st.header("👣 Análisis de Contactos Corporales")
    
    if 'Parte_Cuerpo' not in df.columns:
        st.warning("Datos de contacto no disponibles")
        return
    
    # Datos para Cavalry FC
    df_cavalry = df[df['Equipo'] == 'Cavalry FC']
    contactos_cavalry = df_cavalry['Parte_Cuerpo'].value_counts().reset_index()
    
    # Datos para Rival
    df_rival = df[df['Equipo'] == 'Rival']
    contactos_rival = df_rival['Parte_Cuerpo'].value_counts().reset_index()
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(
            contactos_cavalry,
            names='Parte_Cuerpo',
            values='count',
            title="Contactos Cavalry FC",
            color_discrete_sequence=px.colors.sequential.Reds
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(
            contactos_rival,
            names='Parte_Cuerpo',
            values='count',
            title="Contactos Rival",
            color_discrete_sequence=px.colors.sequential.Blues
        )
        st.plotly_chart(fig, use_container_width=True)

def ranking_jugadores(df):
    st.header("🏅 Ranking de Influencia")
    
    # Calcular métricas combinadas
    df_ranking = df.groupby(['Equipo', 'Ejecutor']).agg(
        Acciones=('Acción', 'count'),
        Goles=('Gol', lambda x: (x == 'Sí').sum()),
        Contactos=('Parte_Cuerpo', 'nunique')
    ).reset_index()
    
    # Crear score táctico
    df_ranking['Score'] = (df_ranking['Acciones'] * 0.3) + (df_ranking['Goles'] * 0.5) + (df_ranking['Contactos'] * 0.2)
    df_ranking = df_ranking.sort_values('Score', ascending=False).head(15)
    
    # Visualización interactiva
    fig = px.scatter(
        df_ranking,
        x='Acciones',
        y='Goles',
        size='Score',
        color='Equipo',
        hover_name='Ejecutor',
        title="Influencia por Jugador",
        labels={'Acciones': 'Acciones Totales', 'Goles': 'Goles Directos'},
        color_discrete_map={'Cavalry FC': '#FF0000', 'Rival': '#0000FF'}
    )
    st.plotly_chart(fig, use_container_width=True)

# =============================================
# FUNCIÓN PRINCIPAL
# =============================================

def analitica_page():
    st.title("⚔️ Análisis Táctico Cavalry FC")
    
    # Cargar datos
    df = cargar_datos()
    if df.empty:
        st.warning("Base de datos no disponible. Verificar conexión o datos.")
        return
    
    # Aplicar filtros
    df_filtrado = configurar_filtros(df)
    if df_filtrado.empty:
        st.warning("No hay registros con los filtros seleccionados")
        return
    
    # Sección de KPIs
    mostrar_kpis_estrategicos(df_filtrado)
    
    # Sección de mapas de calor
    st.header("🔥 Mapeo de Zonas Clave")
    col1, col2 = st.columns(2)
    with col1:
        generar_mapa_calor(df_filtrado, 'saque')
    with col2:
        generar_mapa_calor(df_filtrado, 'remate')
    
    # Sección de análisis táctico
    analizar_contactos(df_filtrado)
    
    # Ranking de jugadores
    ranking_jugadores(df_filtrado)
    
    # Descarga de datos
    st.divider()
    csv = df_filtrado.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Exportar Datos Filtrados",
        data=csv,
        file_name="analisis_tactico.csv",
        mime="text/csv",
        help="Descarga los datos actualmente filtrados en formato CSV"
    )
