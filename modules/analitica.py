# modules/analitica.py
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from mplsoccer import VerticalPitch
from datetime import datetime

# =============================================
# FUNCIONES BASE
# =============================================

def cargar_datos():
    try:
        url = "https://raw.githubusercontent.com/felipeorma/abp/main/master_abp.csv"
        df = pd.read_csv(url)
        
        # Renombrar columnas
        df = df.rename(columns={
            'Tipo Ejecución': 'Tipo_Acción',
            'Primer Contacto': 'Contacto',
            'Parte Cuerpo': 'Parte_Cuerpo'
        })

        # Validar estructura
        required_columns = [
            'Jornada', 'Fecha', 'Rival', 'Periodo', 'Minuto', 'Acción', 
            'Equipo', 'Ejecutor', 'Zona Saque', 'Zona Remate', 'Gol',
            'x_saque', 'y_saque', 'x_remate', 'y_remate', 'Tipo_Acción'
        ]
        
        if not all(col in df.columns for col in required_columns):
            st.error("Error en estructura del CSV")
            return pd.DataFrame()

        # Conversiones
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df['Minuto'] = pd.to_numeric(df['Minuto'], errors='coerce')
        df['Gol'] = df['Gol'].replace({'Sí': True, 'No': False})
        
        return df.dropna(subset=['Zona Saque', 'Zona Remate', 'Fecha'])

    except Exception as e:
        st.error(f"Error crítico: {str(e)}")
        return pd.DataFrame()

# =============================================
# COMPONENTES DE INTERFAZ
# =============================================

def configurar_filtros(df):
    with st.sidebar:
        st.header("⚙️ Filtros Tácticos")
        
        # 1. Selector de fechas (multiselect)
        fechas_disponibles = df['Fecha'].dt.strftime('%d/%m/%Y').sort_values(ascending=False).unique()
        fechas_sel = st.multiselect(
            "Fechas de partidos",
            options=fechas_disponibles,
            default=fechas_disponibles
        )
        
        # 2. Selector de equipo (radio buttons)
        equipo_sel = st.radio(
            "Equipo a analizar",
            options=['Cavalry FC', 'Rival'],
            index=0
        )
        
        # 3. Filtros adicionales
        acciones_sel = st.multiselect(
            "Tipo de acción",
            options=df['Acción'].unique(),
            default=df['Acción'].unique()
        )
        
        # 4. Rango de minutos
        min_min = int(df['Minuto'].min())
        max_min = int(df['Minuto'].max())
        rango_min = st.slider("Rango de minutos", min_min, max_min, (min_min, max_min))

    # Aplicar filtros (excepto equipo)
    df_filtrado = df[
        (df['Fecha'].dt.strftime('%d/%m/%Y').isin(fechas_sel)) &
        (df['Acción'].isin(acciones_sel)) &
        (df['Minuto'].between(*rango_min))
    ]
    
    return df_filtrado, equipo_sel

# =============================================
# MÓDULOS DE ANÁLISIS
# =============================================

def calcular_kpis(df, equipo_sel):
    contrincante = 'Rival' if equipo_sel == 'Cavalry FC' else 'Cavalry FC'
    
    # Datos del equipo seleccionado
    df_equipo = df[df['Equipo'] == equipo_sel]
    goles_favor = df_equipo['Gol'].sum()
    acciones_ofensivas = len(df_equipo)
    
    # Datos del contrincante
    df_rival = df[df['Equipo'] == contrincante]
    goles_contra = df_rival['Gol'].sum()
    acciones_defensivas = len(df_rival)
    
    # Cálculo de efectividades
    ef_ofensiva = (goles_favor / acciones_ofensivas * 100) if acciones_ofensivas > 0 else 0
    ef_defensiva = (1 - (goles_contra / acciones_defensivas)) * 100 if acciones_defensivas > 0 else 0
    
    return ef_ofensiva, ef_defensiva, goles_favor, goles_contra

def generar_mapa_calor(df, equipo, tipo):
    # Filtrar datos
    df_filtrado = df[df['Equipo'] == equipo]
    
    if tipo == 'saque':
        coord_x = 'x_saque'
        coord_y = 'y_saque'
        # Excluir penales solo para saques
        df_filtrado = df_filtrado[df_filtrado['Zona Saque'] != 'Penal']
    else:
        coord_x = 'x_remate'
        coord_y = 'y_remate'
    
    # Configurar pitch
    pitch = VerticalPitch(pitch_type='statsbomb', half=True, goal_type='box')
    fig, ax = plt.subplots(figsize=(10, 7))
    pitch.draw(ax=ax)
    
    # Generar heatmap
    if not df_filtrado.empty:
        pitch.kdeplot(
            df_filtrado[coord_x], 
            df_filtrado[coord_y],
            ax=ax,
            cmap='Reds' if tipo == 'remate' else 'Blues',
            levels=50,
            fill=True,
            alpha=0.6
        )
    ax.set_title(f"Mapa de {tipo.capitalize()}s - {equipo}", fontsize=14)
    st.pyplot(fig)
    plt.close()

def generar_graficos_contactos(df, equipo):
    df_equipo = df[df['Equipo'] == equipo]
    if not df_equipo.empty and 'Parte_Cuerpo' in df_equipo:
        fig = px.pie(
            df_equipo,
            names='Parte_Cuerpo',
            title=f"Contactos Corporales - {equipo}",
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        st.plotly_chart(fig, use_container_width=True)

# =============================================
# VISTA PRINCIPAL
# =============================================

def analitica_page():
    st.title("🔥 Panel Táctico Cavalry FC")
    
    # Cargar datos
    df = cargar_datos()
    if df.empty:
        st.warning("Base de datos no disponible")
        return
    
    # Configurar filtros
    df_filtrado, equipo_sel = configurar_filtros(df)
    contrincante = 'Rival' if equipo_sel == 'Cavalry FC' else 'Cavalry FC'
    
    # Calcular KPIs
    ef_of, ef_def, goles_favor, goles_contra = calcular_kpis(df_filtrado, equipo_sel)
    
    # Mostrar KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"Goles {equipo_sel}", goles_favor)
    with col2:
        st.metric(f"Efectividad Ofensiva", f"{ef_of:.1f}%")
    with col3:
        st.metric(f"Efectividad Defensiva", f"{ef_def:.1f}%")
    
    # Sección de mapas de calor
    st.header("🗺️ Análisis Espacial")
    col_map1, col_map2 = st.columns(2)
    with col_map1:
        generar_mapa_calor(df_filtrado, equipo_sel, 'saque')
    with col_map2:
        generar_mapa_calor(df_filtrado, equipo_sel, 'remate')
    
    # Sección de contactos
    st.header("👥 Análisis de Contactos")
    generar_graficos_contactos(df_filtrado, equipo_sel)
    
    # Sección adicional (gráficos previos)
    st.header("📊 Métricas Complementarias")
    df_equipo = df_filtrado[df_filtrado['Equipo'] == equipo_sel]
    if not df_equipo.empty:
        fig = px.histogram(
            df_equipo,
            x='Acción',
            color='Tipo_Acción',
            title="Distribución de Acciones"
        )
        st.plotly_chart(fig, use_container_width=True)
