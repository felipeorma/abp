# modules/analitica.py
import pandas as pd
import streamlit as st# modules/analitica.py
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from mplsoccer import VerticalPitch
from datetime import datetime
import requests
from io import BytesIO

# Configuración del logo SVG compatible
def setup_logo():
    logo_url = "https://raw.githubusercontent.com/felipeorma/abp/main/Cavalry_FC_logo.svg"
    st.sidebar.markdown(
        f'<div style="text-align: center;"><img src="{logo_url}" width="200"></div>',
        unsafe_allow_html=True
    )

# Carga de datos desde GitHub con validación robusta
def cargar_datos():
    try:
        # URL del CSV en GitHub
        url = "https://raw.githubusercontent.com/felipeorma/abp/main/master_abp.csv"
        
        # Cargar datos con timeout y codificación correcta
        df = pd.read_csv(url, encoding='utf-8')
        
        # Corregir nombre de columna con problemas de codificación
        df = df.rename(columns={'Tipo EjecuciÃ³n': 'Tipo Ejecución'})
        
        # Columnas obligatorias para el análisis (actualizadas)
        columnas_requeridas = [
            'Jornada', 'Rival', 'Periodo', 'Minuto', 'Acción', 'Equipo', 'Fecha',
            'Gol', 'Primer Contacto', 'Segundo Contacto', 'Tipo Ejecución', 
            'Zona Saque', 'Zona Remate', 'Ejecutor', 'Resultado'
        ]
        
        # Verificar estructura completa
        faltantes = [col for col in columnas_requeridas if col not in df.columns]
        if faltantes:
            st.error(f"🚨 Estructura incompleta. Faltan: {', '.join(faltantes)}")
            return pd.DataFrame()

        # Conversión de tipos de datos
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df['Minuto'] = pd.to_numeric(df['Minuto'], errors='coerce')
        
        # Normalización de valores
        df['Gol'] = df['Gol'].apply(lambda x: 'Sí' if str(x).lower() in ['sí', 'si', '1', 'true'] else 'No')
        
        # Limpieza de datos
        df = df.dropna(subset=['Zona Saque', 'Zona Remate', 'Ejecutor', 'Fecha'])
        
        return df

    except Exception as e:
        st.error(f"⛔ Error cargando datos: {str(e)}")
        return pd.DataFrame()

# Configuración de filtros interactivos
def configurar_filtros(df):
    with st.sidebar:
        st.header("🔍 Filtros Avanzados")
        
        # Filtro de jornadas
        jornadas = sorted(df['Jornada'].unique())
        jornadas_sel = st.multiselect(
            "Jornada",
            options=jornadas,
            default=jornadas
        )
        
        # Filtro de fechas dinámico
        fechas_disponibles = df[df['Jornada'].isin(jornadas_sel)]['Fecha'].unique()
        fechas_formateadas = [
            f"{fecha.strftime('%d/%m')} vs {df[df['Fecha'] == fecha]['Rival'].iloc[0]}" 
            for fecha in sorted(fechas_disponibles, reverse=True)
        ]
        
        fechas_sel = st.multiselect(
            "Partidos",
            options=fechas_formateadas,
            default=fechas_formateadas
        )
        
        # Mapeo de fechas seleccionadas
        fechas_a_filtrar = [
            fecha for i, fecha in enumerate(sorted(fechas_disponibles, reverse=True))
            if fechas_formateadas[i] in fechas_sel
        ] if fechas_sel else fechas_disponibles

        # Filtros adicionales
        col1, col2 = st.columns(2)
        with col1:
            condicion = st.multiselect(
                "Condición",
                options=df['Condición'].unique(),
                default=df['Condición'].unique()
            )
        with col2:
            equipos = st.multiselect(
                "Equipo",
                options=df['Equipo'].unique(),
                default=df['Equipo'].unique()
            )
            
        acciones = st.multiselect(
            "Acciones",
            options=df['Acción'].unique(),
            default=df['Acción'].unique()
        )
        
        jugadores = st.multiselect(
            "Jugadores",
            options=df['Ejecutor'].unique(),
            default=df['Ejecutor'].unique()
        )

        # Filtro temporal adaptativo
        min_min = int(df['Minuto'].min())
        max_min = int(df['Minuto'].max())
        rango_minutos = st.slider(
            "Rango de minutos",
            min_min, max_min,
            (min_min, max_min)
        )

    # Aplicar todos los filtros
    return df[
        (df['Jornada'].isin(jornadas_sel)) &
        (df['Fecha'].isin(fechas_a_filtrar)) &
        (df['Condición'].isin(condicion)) &
        (df['Equipo'].isin(equipos)) &
        (df['Acción'].isin(acciones)) &
        (df['Ejecutor'].isin(jugadores)) &
        (df['Minuto'].between(*rango_minutos))
    ]

# Visualización de KPIs mejorados
def mostrar_kpis_mejorados(df):
    cols = st.columns(5)
    
    # Logo pequeño
    with cols[0]:
        st.markdown(
            '<div style="text-align: center;"><img src="https://raw.githubusercontent.com/felipeorma/abp/main/Cavalry_FC_logo.svg" width="60"></div>',
            unsafe_allow_html=True
        )
    
    # Goles a favor (Cavalry FC)
    goles_favor = df[(df['Gol'] == 'Sí') & (df['Equipo'] == 'Cavalry FC')].shape[0]
    with cols[1]:
        st.metric("✅ Goles a favor", goles_favor, 
                help="Goles convertidos por Cavalry FC")
    
    # Goles en contra (Rival)
    goles_contra = df[(df['Gol'] == 'Sí') & (df['Equipo'] == 'Rival')].shape[0]
    with cols[2]:
        st.metric("❌ Goles en contra", goles_contra, 
                help="Goles concedidos al rival")
    
    # Efectividad ofensiva
    acciones_ofensivas = df[df['Equipo'] == 'Cavalry FC'].shape[0]
    with cols[3]:
        eficacia_of = (goles_favor / acciones_ofensivas * 100) if acciones_ofensivas > 0 else 0
        st.metric("🎯 Efectividad Ofensiva", f"{eficacia_of:.1f}%")
    
    # Efectividad defensiva
    acciones_defensivas = df[df['Equipo'] == 'Rival'].shape[0]
    with cols[4]:
        eficacia_def = (100 - (goles_contra / acciones_defensivas * 100)) if acciones_defensivas > 0 else 0
        st.metric("🛡️ Efectividad Defensiva", f"{eficacia_def:.1f}%")

# Sección de mapas de calor
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
    df_coords = df[coord_col].map(zonas_coords).dropna().apply(pd.Series)
    
    if df_coords.empty:
        st.warning(f"No hay datos válidos para {tipo}s")
        return
    
    df_coords.columns = ['x', 'y']
    
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
    pitch.kdeplot(
        df_coords['x'], df_coords['y'],
        ax=ax,
        cmap='Greens' if tipo == 'saque' else 'Reds',
        levels=100,
        fill=True,
        alpha=0.75,
        bw_adjust=0.65
    )
    ax.set_title(f"Densidad de {tipo.capitalize()}s", fontsize=16, pad=20)
    st.pyplot(fig)
    plt.close()

# Sección temporal
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
            title="Distribución temporal por acción",
            points="all"
        )
        st.plotly_chart(fig, use_container_width=True)

# Sección de efectividad mejorada
def generar_seccion_efectividad_mejorada(df):
    st.header("🎯 Efectividad Operativa")
    col1, col2 = st.columns(2)
    
    with col1:
        df_efectividad = df[df['Equipo'] == 'Cavalry FC'].groupby('Ejecutor').agg(
            Acciones=('Ejecutor', 'count'),
            Goles=('Gol', lambda x: (x == 'Sí').sum()),
            Efectividad=('Gol', lambda x: (x == 'Sí').mean() * 100)
        ).reset_index()
        
        fig = px.scatter(
            df_efectividad, 
            x='Acciones', y='Efectividad',
            size='Goles', color='Ejecutor',
            title="Efectividad por Jugador",
            hover_data=['Ejecutor', 'Acciones', 'Goles']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.sunburst(
            df, path=['Equipo', 'Acción', 'Resultado'],
            title="Flujo de Acciones y Resultados",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig, use_container_width=True)

# Sección de análisis de contactos (actualizada)
def generar_seccion_contactos(df):
    st.header("👣 Análisis de Contactos")
    col1, col2 = st.columns(2)
    
    with col1:
        # Combinar ambos contactos para análisis ofensivo
        contactos_of = pd.concat([
            df[df['Equipo'] == 'Cavalry FC']['Primer Contacto'],
            df[df['Equipo'] == 'Cavalry FC']['Segundo Contacto']
        ]).value_counts().reset_index()
        contactos_of.columns = ['Contacto', 'Cantidad']
        
        fig = px.pie(
            contactos_of, 
            names='Contacto', 
            values='Cantidad',
            title="Contactos Ofensivos",
            color_discrete_sequence=['#FF0000', '#000000']
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        # Combinar ambos contactos para análisis defensivo
        contactos_def = pd.concat([
            df[df['Equipo'] == 'Rival']['Primer Contacto'],
            df[df['Equipo'] == 'Rival']['Segundo Contacto']
        ]).value_counts().reset_index()
        contactos_def.columns = ['Contacto', 'Cantidad']
        
        fig = px.pie(
            contactos_def, 
            names='Contacto', 
            values='Cantidad',
            title="Contactos Defensivos",
            color_discrete_sequence=['#000000', '#FF0000']
        )
        st.plotly_chart(fig, use_container_width=True)

# Sección de tipos de acción (actualizada)
def generar_seccion_tipos_accion(df):
    st.header("📊 Tipos de Ejecución")
    
    df_acciones = df[df['Equipo'] == 'Cavalry FC']['Tipo Ejecución'].value_counts().reset_index()
    df_acciones.columns = ['Tipo', 'Cantidad']
    
    fig = px.bar(
        df_acciones,
        x='Tipo',
        y='Cantidad',
        color='Tipo',
        title="Distribución de Tipos de Ejecución Ofensiva",
        labels={'Cantidad': 'Número de acciones'},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig, use_container_width=True)

# Sección de mejores jugadores
def generar_seccion_mejores_jugadores(df):
    st.header("🏆 Mejores Jugadores")
    col1, col2 = st.columns(2)
    
    with col1:
        df_def = df[df['Acción'].isin(['Intercepción', 'Despeje', 'Entrada'])]
        top_def = df_def['Ejecutor'].value_counts().head(5).reset_index()
        top_def.columns = ['Jugador', 'Acciones']
        fig = px.bar(
            top_def,
            x='Jugador',
            y='Acciones',
            title="Top 5 Defensores",
            labels={'Acciones': 'Acciones defensivas'},
            color='Acciones',
            color_continuous_scale='reds'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        df_ataq = df[df['Acción'].isin(['Remate', 'Tiro'])]
        top_ataq = df_ataq['Ejecutor'].value_counts().head(5).reset_index()
        top_ataq.columns = ['Jugador', 'Acciones']
        fig = px.bar(
            top_ataq,
            x='Jugador',
            y='Acciones',
            title="Top 5 Rematadores",
            labels={'Acciones': 'Remates'},
            color='Acciones',
            color_continuous_scale='reds'
        )
        st.plotly_chart(fig, use_container_width=True)

# Configuración de descarga
def configurar_descarga(df):
    st.divider()
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📤 Exportar Dataset Filtrado",
        data=csv,
        file_name="analisis_tactico_cavalry.csv",
        mime="text/csv"
    )

# Función principal de la página
def analitica_page():
    setup_logo()
    st.title("⚽ Panel de Análisis Táctico - Cavalry FC")
    
    df = cargar_datos()
    if df.empty:
        st.warning("⚠️ No hay datos disponibles. Verifica la conexión o el archivo CSV.")
        return
    
    df_filtrado = configurar_filtros(df)
    
    if df_filtrado.empty:
        st.warning("🔍 No hay datos con los filtros seleccionados")
        return
    
    mostrar_kpis_mejorados(df_filtrado)
    generar_seccion_espacial(df_filtrado)
    generar_seccion_temporal(df_filtrado)
    generar_seccion_efectividad_mejorada(df_filtrado)
    generar_seccion_contactos(df_filtrado)
    generar_seccion_tipos_accion(df_filtrado)
    generar_seccion_mejores_jugadores(df_filtrado)
    configurar_descarga(df_filtrado)
