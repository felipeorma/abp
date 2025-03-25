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
        df['Gol'] = df['Gol'].apply(lambda x: 'Sí' if str(x).lower() in ['sí', 'si', '1', 'true', 'yes'] else 'No')
        df['Equipo'] = df['Equipo'].str.strip()
        
        # Limpieza de datos
        df = df.dropna(subset=['Zona Saque', 'Zona Remate', 'Ejecutor', 'Fecha'])
        
        return df

    except Exception as e:
        st.error(f"⛔ Error cargando datos: {str(e)}")
        return pd.DataFrame()

def configurar_filtros(df):
    with st.sidebar:
        st.header("🔍 Filtros Avanzados")
        
        # Filtro de equipos con lógica invertida
        equipo_analisis = st.radio(
            "Equipo a analizar",
            options=['Cavalry FC', 'Rival'],
            index=0
        )
        
        # Filtro de jornadas
        jornadas = sorted(df['Jornada'].unique(), reverse=True)
        jornadas_sel = st.multiselect(
            "Jornadas",
            options=jornadas,
            default=jornadas[:3]
        )
        
        # Filtro de partidos mejorado
        partidos_disponibles = df[df['Jornada'].isin(jornadas_sel)]
        partidos = partidos_disponibles.drop_duplicates('Fecha').sort_values('Fecha', ascending=False)
        partidos_opciones = [
            f"J{jornada} - {fecha.strftime('%d/%m')} vs {rival}"
            for jornada, fecha, rival in zip(partidos['Jornada'], partidos['Fecha'], partidos['Rival'])
        ]
        
        partidos_sel = st.multiselect(
            "Seleccionar partidos",
            options=partidos_opciones,
            default=partidos_opciones[:1]
        )
        
        # Obtener fechas seleccionadas
        fechas_sel = []
        for opcion in partidos_sel:
            jornada = int(opcion.split(' - ')[0][1:])
            fecha_str = opcion.split(' vs ')[0].split(' - ')[1]
            fecha = datetime.strptime(fecha_str, '%d/%m').replace(year=datetime.now().year)
            fechas_sel.extend(partidos[(partidos['Jornada'] == jornada) & 
                                      (partidos['Fecha'].dt.strftime('%d/%m') == fecha_str)]['Fecha'].tolist())
        
        # Filtros adicionales
        acciones = st.multiselect(
            "Acciones",
            options=sorted(df['Acción'].unique()),
            default=sorted(df['Acción'].unique())[:3]
        )
        
        jugadores = st.multiselect(
            "Jugadores",
            options=sorted(df['Ejecutor'].unique()),
            default=sorted(df['Ejecutor'].unique())[:5]
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
    df_filtrado = df[
        (df['Equipo'] == equipo_analisis) &
        (df['Jornada'].isin(jornadas_sel)) &
        (df['Fecha'].isin(fechas_sel)) &
        (df['Acción'].isin(acciones)) &
        (df['Ejecutor'].isin(jugadores)) &
        (df['Minuto'].between(*rango_minutos))
    ]
    
    # Invertir lógica si se selecciona Rival
    if equipo_analisis == 'Rival':
        df_filtrado['Equipo'] = 'Cavalry FC'  # Para que las visualizaciones funcionen correctamente
    
    return df_filtrado

def mostrar_kpis_mejorados(df, equipo_analisis):
    cols = st.columns(4)
    
    # Cálculos dinámicos basados en equipo seleccionado
    goles_favor = df[df['Gol'] == 'Sí'].shape[0]
    acciones_totales = df.shape[0]
    efectividad = (goles_favor / acciones_totales * 100) if acciones_totales > 0 else 0
    
    with cols[0]:
        st.metric(f"⚽ Goles {equipo_analisis}", goles_favor)
    
    with cols[1]:
        st.metric(f"📊 Acciones totales", acciones_totales)
    
    with cols[2]:
        st.metric(f"🎯 Efectividad", f"{efectividad:.1f}%")
    
    with cols[3]:
        jugadores_top = df['Ejecutor'].value_counts().head(3).index.tolist()
        st.metric(
            "👥 Jugadores destacados", 
            ", ".join(jugadores_top) if jugadores_top else "N/A"
        )

def generar_mapa_calor(df, tipo='saque'):
    # Sistema de coordenadas mejorado
    zonas_coords = {
        1: (105, 40),   # Centro del área
        2: (105, 20),    # Izquierda del área
        3: (105, 60),    # Derecha del área
        4: (85, 30),     # Centro frontal área
        5: (85, 50),     # Derecha frontal área
        6: (70, 40),     # Centro medio campo ofensivo
        7: (50, 30),     # Centro medio campo
        8: (30, 40),     # Centro medio campo defensivo
        "Penal": (88, 40) # Punto penal
    }
    
    coord_col = 'Zona Saque' if tipo == 'saque' else 'Zona Remate'
    df_coords = df[coord_col].map(zonas_coords).dropna()
    
    if df_coords.empty:
        st.warning(f"No hay datos de {tipo}s en los filtros seleccionados")
        return
    
    # Convertir a coordenadas x, y
    xs, ys = zip(*df_coords)
    
    # Configuración del campo
    pitch = VerticalPitch(
        pitch_type='uefa',
        half=True,
        goal_type='box',
        pitch_color='#E8E8E8',
        line_color='#3B3B3B',
        linewidth=1.5
    )
    
    fig, ax = plt.subplots(figsize=(10, 7))
    pitch.draw(ax=ax)
    
    # Heatmap mejorado
    kdeplot = pitch.kdeplot(
        xs, ys,
        ax=ax,
        cmap='magma',
        levels=50,
        fill=True,
        alpha=0.7,
        bw_method=0.3
    )
    
    # Puntos de acción
    pitch.scatter(
        xs, ys,
        ax=ax,
        s=80,
        color='red',
        edgecolors='black',
        linewidth=1
    )
    
    ax.set_title(f"Mapa de calor de {tipo}s", fontsize=14, pad=15)
    st.pyplot(fig)
    plt.close()

def generar_seccion_espacial(df):
    st.header("🌍 Mapeo Táctico")
    col1, col2 = st.columns(2)
    
    with col1:
        generar_mapa_calor(df, tipo='saque')
    with col2:
        generar_mapa_calor(df, tipo='remate')

def generar_seccion_temporal(df):
    st.header("⏳ Evolución Temporal")
    
    # Gráfico de acciones por minuto
    fig = px.histogram(
        df, 
        x='Minuto',
        color='Acción',
        nbins=30,
        title="Acciones por minuto de juego",
        labels={'count': 'Número de acciones'},
        category_orders={'Acción': df['Acción'].value_counts().index.tolist()}
    )
    fig.update_layout(barmode='stack', xaxis_title='Minuto', yaxis_title='Acciones')
    st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico de acciones por jornada
    fig2 = px.bar(
        df.groupby(['Jornada', 'Acción']).size().reset_index(name='Count'),
        x='Jornada',
        y='Count',
        color='Acción',
        title="Acciones por jornada",
        labels={'Count': 'Número de acciones'}
    )
    fig2.update_layout(xaxis_title='Jornada', yaxis_title='Acciones')
    st.plotly_chart(fig2, use_container_width=True)

def generar_seccion_efectividad(df):
    st.header("🎯 Efectividad por Jugador")
    
    # Calcular métricas por jugador
    df_efectividad = df.groupby('Ejecutor').agg(
        Acciones=('Acción', 'count'),
        Goles=('Gol', lambda x: (x == 'Sí').sum()),
        Efectividad=('Gol', lambda x: (x == 'Sí').mean() * 100)
    ).sort_values('Goles', ascending=False).reset_index()
    
    # Gráfico de efectividad
    fig = px.scatter(
        df_efectividad,
        x='Acciones',
        y='Efectividad',
        size='Goles',
        color='Ejecutor',
        hover_name='Ejecutor',
        title="Efectividad por jugador (tamaño = goles)",
        labels={
            'Acciones': 'Total de acciones',
            'Efectividad': 'Porcentaje de efectividad',
            'Goles': 'Goles marcados'
        }
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabla detallada
    st.subheader("Detalle por jugador")
    st.dataframe(
        df_efectividad.style
            .background_gradient(cmap='Blues', subset=['Acciones'])
            .background_gradient(cmap='Greens', subset=['Goles'])
            .format({'Efectividad': '{:.1f}%'}),
        height=400
    )

def generar_seccion_contactos(df):
    st.header("👣 Análisis de Contactos")
    
    # Combinar ambos contactos
    contactos = pd.concat([
        df['Primer Contacto'].rename('Contacto'),
        df['Segundo Contacto'].rename('Contacto')
    ]).dropna()
    
    if not contactos.empty:
        # Gráfico de distribución
        fig = px.pie(
            contactos.value_counts().reset_index(name='Count'),
            names='Contacto',
            values='Count',
            title="Distribución de contactos",
            hole=0.3
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No hay datos de contactos con los filtros seleccionados")

def generar_seccion_tipos_accion(df):
    st.header("📊 Tipos de Ejecución")
    
    df_tipos = df['Tipo Ejecución'].value_counts().reset_index(name='Count')
    
    fig = px.bar(
        df_tipos,
        x='Count',
        y='Tipo Ejecución',
        orientation='h',
        title="Distribución de tipos de ejecución",
        labels={'Count': 'Número de acciones'},
        color='Count',
        color_continuous_scale='Teal'
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

def configurar_descarga(df):
    st.divider()
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📤 Exportar Dataset Filtrado",
        data=csv,
        file_name="analisis_tactico.csv",
        mime="text/csv",
        help="Descargar los datos actualmente filtrados en formato CSV"
    )

def analitica_page():
    st.title("📊 Panel de Análisis Táctico")
    
    with st.spinner("Cargando datos..."):
        df = cargar_datos()
        if df.empty:
            st.error("No se pudieron cargar los datos. Por favor verifica la conexión.")
            return
    
    df_filtrado = configurar_filtros(df)
    
    if df_filtrado.empty:
        st.warning("No hay datos con los filtros seleccionados. Ajusta los filtros e intenta nuevamente.")
        return
    
    equipo_analisis = 'Cavalry FC' if 'Cavalry FC' in df_filtrado['Equipo'].unique() else 'Rival'
    
    st.subheader(f"Análisis para {equipo_analisis}")
    mostrar_kpis_mejorados(df_filtrado, equipo_analisis)
    
    with st.expander("Mapas Tácticos", expanded=True):
        generar_seccion_espacial(df_filtrado)
    
    with st.expander("Evolución Temporal"):
        generar_seccion_temporal(df_filtrado)
    
    with st.expander("Efectividad"):
        generar_seccion_efectividad(df_filtrado)
    
    with st.expander("Análisis de Contactos"):
        generar_seccion_contactos(df_filtrado)
    
    with st.expander("Tipos de Ejecución"):
        generar_seccion_tipos_accion(df_filtrado)
    
    configurar_descarga(df_filtrado)
