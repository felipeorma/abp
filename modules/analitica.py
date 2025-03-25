# modules/analitica.py
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from mplsoccer import VerticalPitch
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO

# Configuración inicial del logo
def setup_logo():
    # Usar versión PNG del logo directamente
    logo_url = "https://raw.githubusercontent.com/felipeorma/abp/refs/heads/main/Cavalry_FC_logo.svg"
    
    try:
        response = requests.get(logo_url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        logo = Image.open(BytesIO(response.content))
        st.sidebar.image(logo, width=200)
    except Exception as e:
        st.error(f"Error cargando logo: {str(e)}")
        st.sidebar.markdown("[Logo Cavalry FC](https://raw.githubusercontent.com/felipeorma/abp/refs/heads/main/Cavalry_FC_logo.svg)")

def analitica_page():
    setup_logo()
    st.title("⚽ Panel de Análisis Táctico Profesional - Cavalry FC")
    
    try:
        df = cargar_datos()
        if df.empty:
            st.warning("¡Base de datos vacía! Registra acciones en el módulo de Registro")
            return
    except Exception as e:
        st.error(f"Error crítico: {str(e)}")
        return

    df_filtrado = configurar_filtros(df)
    mostrar_kpis_mejorados(df_filtrado)
    generar_seccion_espacial(df_filtrado)
    generar_seccion_temporal(df_filtrado)
    generar_seccion_efectividad_mejorada(df_filtrado)
    generar_seccion_contactos(df_filtrado)
    generar_seccion_tipos_accion(df_filtrado)
    generar_seccion_mejores_jugadores(df_filtrado)
    configurar_descarga(df_filtrado)

def cargar_datos():
    # Cargar datos desde GitHub
    url = "https://raw.githubusercontent.com/felipeorma/abp/refs/heads/main/master_abp.csv"
    df = pd.read_csv(url)
    
    # Convertir y formatear fechas
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    df = df.dropna(subset=['Fecha'])
    df['Fecha_Str'] = df['Fecha'].dt.strftime('%Y-%m-%d')  # Nuevo campo formateado
    
    # Validar estructura del CSV
    columnas_requeridas = ['Jornada', 'Rival', 'Periodo', 'Minuto', 'Acción', 'Equipo', 'Fecha', 'Gol', 'Contacto', 'Tipo Acción']
    if not all(col in df.columns for col in columnas_requeridas):
        st.error("Estructura inválida del CSV: faltan columnas clave")
        return pd.DataFrame()
    
    # Limpieza de datos
    df['Minuto'] = pd.to_numeric(df['Minuto'], errors='coerce')
    df = df.dropna(subset=['Zona Saque', 'Zona Remate', 'Ejecutor'])
    
    # Asegurar que 'Gol' esté en formato correcto
    df['Gol'] = df['Gol'].apply(lambda x: 'Sí' if str(x).lower() in ['sí', 'si', '1', 'true'] else 'No')
    
    return df

def configurar_filtros(df):
    with st.sidebar:
        st.header("🔍 Filtros Avanzados")
        
        # 1. FILTRO DE JORNADA (PRIMERO)
        todas_jornadas = sorted(df['Jornada'].unique())
        jornadas_seleccionadas = st.multiselect(
            "Jornada",
            options=todas_jornadas,
            default=todas_jornadas,
            help="Filtra por jornadas específicas"
        )
        
        # Filtrar DF base por jornadas seleccionadas
        df_filtrado_base = df[df['Jornada'].isin(jornadas_seleccionadas)] if jornadas_seleccionadas else df
        
        # 2. FILTRO DE FECHAS (DEPENDE DE JORNADA)
        if not df_filtrado_base.empty:
            fechas_ordenadas = df_filtrado_base.sort_values('Fecha', ascending=False)['Fecha'].unique()
            fechas_formateadas = [
                f"{fecha.strftime('%d/%m')} vs {df_filtrado_base[df_filtrado_base['Fecha'] == fecha]['Rival'].iloc[0]}" 
                for fecha in fechas_ordenadas
            ]
        else:
            fechas_ordenadas = []
            fechas_formateadas = []
            
        opciones_fechas = ["Todos los partidos"] + fechas_formateadas
        fechas_seleccionadas = st.multiselect(
            "Partidos por fecha",
            options=opciones_fechas,
            default=["Todos los partidos"],
            help="Selecciona partidos específicos"
        )
        
        # Mapear fechas seleccionadas
        if "Todos los partidos" in fechas_seleccionadas:
            fechas_a_filtrar = fechas_ordenadas
        else:
            fechas_a_filtrar = [
                fechas_ordenadas[i] 
                for i, f in enumerate(fechas_formateadas) 
                if f in fechas_seleccionadas
            ]

        # 3. OTROS FILTROS (DEPENDEN DE JORNADA Y FECHA)
        df_filtrado_intermedio = df_filtrado_base[df_filtrado_base['Fecha'].isin(fechas_a_filtrar)] if fechas_a_filtrar else df_filtrado_base
        
        col1, col2 = st.columns(2)
        with col1:
            condicion = st.multiselect(
                "Condición",
                options=df_filtrado_intermedio['Condición'].unique(),
                default=df_filtrado_intermedio['Condición'].unique()
            )
        with col2:
            equipos = st.multiselect(
                "Equipo", 
                options=df_filtrado_intermedio['Equipo'].unique(),
                default=df_filtrado_intermedio['Equipo'].unique()
            )
            
        acciones = st.multiselect(
            "Acciones",
            options=df_filtrado_intermedio['Acción'].unique(),
            default=df_filtrado_intermedio['Acción'].unique()
        )
        
        jugadores = st.multiselect(
            "Jugadores",
            options=df_filtrado_intermedio['Ejecutor'].unique(),
            default=df_filtrado_intermedio['Ejecutor'].unique()
        )

        # 4. FILTRO TEMPORAL (DEPENDE DE DATOS FILTRADOS)
        if not df_filtrado_intermedio.empty:
            min_min = int(df_filtrado_intermedio['Minuto'].min())
            max_min = int(df_filtrado_intermedio['Minuto'].max())
        else:
            min_min, max_min = 0, 90
            
        rango_minutos = st.slider(
            "Minutos del partido",
            min_min, max_min,
            (min_min, max_min)
        )

    # APLICAR TODOS LOS FILTROS JUNTOS
    return df[
        (df['Jornada'].isin(jornadas_seleccionadas)) &
        (df['Fecha'].isin(fechas_a_filtrar)) &
        (df['Condición'].isin(condicion)) &
        (df['Equipo'].isin(equipos)) &
        (df['Acción'].isin(acciones)) &
        (df['Ejecutor'].isin(jugadores)) &
        (df['Minuto'].between(*rango_minutos))
    ]

def mostrar_kpis_mejorados(df):
    cols = st.columns(5)
    
    # Logo pequeño
    with cols[0]:
        logo_url = "https://upload.wikimedia.org/wikipedia/en/thumb/4/4c/Cavalry_FC_logo.svg/1200px-Cavalry_FC_logo.svg.png"
        st.image(logo_url, width=80)
    
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

def generar_seccion_efectividad_mejorada(df):
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
            title="Relación Acciones-Goles por Jugador",
            hover_data=['Ejecutor', 'Acciones', 'Goles']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.sunburst(
            df, path=['Acción', 'Resultado'],
            title="Composición de Resultados por Acción",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig, use_container_width=True)

def generar_seccion_contactos(df):
    st.header("👣 Análisis de Contactos")
    
    # Filtrar solo acciones ofensivas del Cavalry
    df_ofensivo = df[df['Equipo'] == 'Cavalry FC']
    
    # Calcular métricas
    primer_contacto_of = df_ofensivo[df_ofensivo['Contacto'] == 'Primer contacto'].shape[0]
    segundo_contacto_of = df_ofensivo[df_ofensivo['Contacto'] == 'Segundo contacto'].shape[0]
    total_ofensivo = df_ofensivo.shape[0]
    
    # Filtrar acciones defensivas del Cavalry (contra el rival)
    df_defensivo = df[df['Equipo'] == 'Rival']
    primer_contacto_def = df_defensivo[df_defensivo['Contacto'] == 'Primer contacto'].shape[0]
    segundo_contacto_def = df_defensivo[df_defensivo['Contacto'] == 'Segundo contacto'].shape[0]
    total_defensivo = df_defensivo.shape[0]
    
    # Mostrar en columnas
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Ofensivo (Cavalry FC)")
        fig = px.pie(
            names=['Primer contacto', 'Segundo contacto'],
            values=[primer_contacto_of, segundo_contacto_of],
            title="Distribución de contactos ofensivos",
            color_discrete_sequence=['#FF0000', '#000000']  # Rojo y negro del Cavalry
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("Defensivo (vs Rival)")
        fig = px.pie(
            names=['Primer contacto', 'Segundo contacto'],
            values=[primer_contacto_def, segundo_contacto_def],
            title="Distribución de contactos defensivos",
            color_discrete_sequence=['#000000', '#FF0000']
        )
        st.plotly_chart(fig, use_container_width=True)

def generar_seccion_tipos_accion(df):
    st.header("📊 Tipos de Acción")
    
    # Filtrar solo acciones del Cavalry
    df_cavalry = df[df['Equipo'] == 'Cavalry FC']
    
    # Calcular tipos de acción
    tipos_accion = df_cavalry['Tipo Acción'].value_counts().reset_index()
    tipos_accion.columns = ['Tipo', 'Cantidad']
    
    # Mostrar gráfico
    fig = px.bar(
        tipos_accion,
        x='Tipo',
        y='Cantidad',
        color='Tipo',
        title="Distribución de tipos de acción ofensiva",
        labels={'Cantidad': 'Número de acciones', 'Tipo': 'Tipo de acción'},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    st.plotly_chart(fig, use_container_width=True)

def generar_seccion_mejores_jugadores(df):
    st.header("🏆 Mejores Jugadores")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Mejores Defensores")
        df_defensores = df[df['Acción'].isin(['Intercepción', 'Despeje', 'Entrada'])]
        mejores_def = df_defensores['Ejecutor'].value_counts().head(5).reset_index()
        mejores_def.columns = ['Jugador', 'Acciones defensivas']
        
        fig = px.bar(
            mejores_def,
            x='Jugador',
            y='Acciones defensivas',
            color='Acciones defensivas',
            title="Top 5 defensores por acciones defensivas",
            color_continuous_scale='reds'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Mejores Rematadores")
        df_rematadores = df[df['Acción'].isin(['Remate', 'Tiro'])]
        mejores_rem = df_rematadores['Ejecutor'].value_counts().head(5).reset_index()
        mejores_rem.columns = ['Jugador', 'Remates']
        
        fig = px.bar(
            mejores_rem,
            x='Jugador',
            y='Remates',
            color='Remates',
            title="Top 5 rematadores por cantidad de remates",
            color_continuous_scale='reds'
        )
        st.plotly_chart(fig, use_container_width=True)

def configurar_descarga(df):
    st.divider()
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📤 Exportar Dataset Filtrado",
        data=csv,
        file_name="analisis_tactico_cavalry.csv",
        mime="text/csv",
        help="Descarga los datos actualmente filtrados en formato CSV"
    )
