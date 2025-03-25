# modules/analitica.py
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from mplsoccer import VerticalPitch
from datetime import datetime

def cargar_datos():
    """Carga y prepara los datos desde el repositorio GitHub"""
    try:
        url = "https://raw.githubusercontent.com/felipeorma/abp/main/master_abp.csv"
        df = pd.read_csv(url, encoding='utf-8')
        
        # Corrección de nombres de columnas
        df = df.rename(columns={
            'Tipo EjecuciÃ³n': 'Tipo Ejecución',
            'CondiciÃ³n': 'Condición'
        })
        
        # Validación de estructura
        columnas_requeridas = [
            'Jornada', 'Rival', 'Periodo', 'Minuto', 'Acción', 'Equipo', 'Fecha',
            'Gol', 'Primer Contacto', 'Segundo Contacto', 'Tipo Ejecución',
            'Zona Saque', 'Zona Remate', 'Ejecutor', 'Resultado', 'Condición'
        ]
        
        faltantes = [col for col in columnas_requeridas if col not in df.columns]
        if faltantes:
            st.error(f"🚨 Columnas faltantes: {', '.join(faltantes)}")
            return pd.DataFrame()

        # Limpieza y normalización
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df['Minuto'] = pd.to_numeric(df['Minuto'], errors='coerce')
        df['Gol'] = df['Gol'].replace({'Si': 'Sí', 'Yes': 'Sí'}).str.strip().fillna('No')
        df['Equipo'] = df['Equipo'].str.strip()
        
        return df.dropna(subset=['Zona Saque', 'Zona Remate', 'Ejecutor', 'Fecha'])

    except Exception as e:
        st.error(f"⛔ Error al cargar datos: {str(e)}")
        return pd.DataFrame()

def configurar_filtros(df):
    """Configura los filtros interactivos en la barra lateral"""
    with st.sidebar:
        st.header("⚙️ Parámetros de Análisis")
        
        # Filtro de equipo principal
        equipo_analisis = st.radio(
            "Equipo a analizar",
            options=['Cavalry FC', 'Rival'],
            index=0,
            help="Seleccione si desea analizar al Cavalry FC o al equipo rival"
        )
        
        # Filtro de jornadas con ordenamiento descendente
        jornadas = sorted(df['Jornada'].unique(), reverse=True)
        jornadas_sel = st.multiselect(
            "Jornadas",
            options=jornadas,
            default=jornadas[:3],
            help="Seleccione una o más jornadas para analizar"
        )
        
        # Filtro avanzado de partidos
        partidos_disponibles = df[df['Jornada'].isin(jornadas_sel)]
        partidos = partidos_disponibles.drop_duplicates('Fecha').sort_values('Fecha', ascending=False)
        partidos_opciones = [
            f"J{jornada} - {fecha.strftime('%d/%m')} vs {rival}"
            for jornada, fecha, rival in zip(partidos['Jornada'], partidos['Fecha'], partidos['Rival'])
        ]
        
        partidos_sel = st.multiselect(
            "Partidos específicos",
            options=partidos_opciones,
            default=partidos_opciones[:1],
            help="Seleccione partidos individuales para un análisis detallado"
        )
        
        # Obtener fechas seleccionadas
        fechas_sel = []
        for opcion in partidos_sel:
            jornada = int(opcion.split(' - ')[0][1:])
            fecha_str = opcion.split(' vs ')[0].split(' - ')[1]
            fecha = datetime.strptime(fecha_str, '%d/%m').replace(year=datetime.now().year)
            fechas_sel.extend(partidos[(partidos['Jornada'] == jornada) & 
                                      (partidos['Fecha'].dt.strftime('%d/%m') == fecha_str)]['Fecha'].tolist())
        
        # Filtros de acciones y jugadores
        acciones = st.multiselect(
            "Tipos de acción",
            options=sorted(df['Acción'].unique()),
            default=['Remate', 'Pase', 'Centro'],
            help="Filtre por tipos específicos de acciones"
        )
        
        jugadores = st.multiselect(
            "Jugadores",
            options=sorted(df['Ejecutor'].unique()),
            default=sorted(df['Ejecutor'].unique())[:5],
            help="Seleccione jugadores específicos para analizar"
        )

        # Filtro de rango de minutos
        min_min = int(df['Minuto'].min())
        max_min = int(df['Minuto'].max())
        rango_minutos = st.slider(
            "Rango de minutos",
            min_min, max_min,
            (min_min, max_min),
            help="Seleccione el rango de minutos del partido a analizar"
        )

    # Aplicar filtros
    df_filtrado = df[
        (df['Equipo'] == equipo_analisis) &
        (df['Jornada'].isin(jornadas_sel)) &
        (df['Fecha'].isin(fechas_sel)) &
        (df['Acción'].isin(acciones)) &
        (df['Ejecutor'].isin(jugadores)) &
        (df['Minuto'].between(*rango_minutos))
    ]
    
    # Ajustar para análisis del rival
    if equipo_analisis == 'Rival':
        df_filtrado = df_filtrado.copy()
        df_filtrado['Equipo'] = 'Cavalry FC'  # Para consistencia en visualizaciones
    
    return df_filtrado, equipo_analisis

def mostrar_metricas_clave(df, equipo_analisis):
    """Muestra las métricas principales en la parte superior del dashboard"""
    cols = st.columns(4)
    
    # Cálculo de métricas
    goles = df[df['Gol'] == 'Sí'].shape[0]
    acciones = df.shape[0]
    efectividad = (goles / acciones * 100) if acciones > 0 else 0
    jugadores_destacados = df['Ejecutor'].value_counts().head(3).index.tolist()
    
    with cols[0]:
        st.metric(f"⚽ Goles {equipo_analisis}", goles)
    
    with cols[1]:
        st.metric("📊 Acciones totales", acciones)
    
    with cols[2]:
        st.metric("🎯 Efectividad", f"{efectividad:.1f}%")
    
    with cols[3]:
        st.metric(
            "👥 Jugadores destacados", 
            ", ".join(jugadores_destacados) if jugadores_destacados else "N/A"
        )

def generar_mapa_calor(df, tipo='saque'):
    """Genera mapas de calor para saques o remates"""
    # Sistema de coordenadas optimizado
    zonas_coords = {
        1: (105, 40), 2: (105, 20), 3: (105, 60), 
        4: (85, 30), 5: (85, 50), 6: (70, 40),
        7: (50, 30), 8: (30, 40), "Penal": (88, 40)
    }
    
    coord_col = 'Zona Saque' if tipo == 'saque' else 'Zona Remate'
    df_coords = df[coord_col].map(zonas_coords).dropna()
    
    if df_coords.empty:
        st.warning(f"No hay datos de {tipo}s con los filtros actuales")
        return
    
    xs, ys = zip(*df_coords)
    
    # Configuración del campo
    pitch = VerticalPitch(
        pitch_type='uefa',
        half=True,
        goal_type='box',
        pitch_color='#22312b',
        line_color='#c7d5cc',
        linewidth=1.5
    )
    
    fig, ax = plt.subplots(figsize=(10, 7))
    pitch.draw(ax=ax)
    
    # Heatmap con contornos
    pitch.kdeplot(
        xs, ys,
        ax=ax,
        cmap='viridis',
        levels=30,
        fill=True,
        alpha=0.6,
        bw_method=0.3
    )
    
    # Puntos individuales
    pitch.scatter(
        xs, ys,
        ax=ax,
        s=50,
        color='red',
        edgecolors='white',
        linewidth=0.5
    )
    
    ax.set_title(f"Distribución de {tipo}s", fontsize=14, pad=15)
    st.pyplot(fig)
    plt.close()

def visualizar_distribucion_temporal(df):
    """Muestra la distribución temporal de las acciones"""
    st.header("⏳ Distribución Temporal")
    
    tabs = st.tabs(["Por minuto", "Por jornada"])
    
    with tabs[0]:
        fig = px.histogram(
            df,
            x='Minuto',
            color='Acción',
            nbins=30,
            title="Acciones por minuto de juego",
            labels={'count': 'Acciones'},
            category_orders={'Acción': df['Acción'].value_counts().index.tolist()}
        )
        fig.update_layout(barmode='stack', xaxis_title='Minuto', yaxis_title='Acciones')
        st.plotly_chart(fig, use_container_width=True)
    
    with tabs[1]:
        fig = px.bar(
            df.groupby(['Jornada', 'Acción']).size().reset_index(name='Count'),
            x='Jornada',
            y='Count',
            color='Acción',
            title="Acciones por jornada",
            labels={'Count': 'Acciones'}
        )
        fig.update_layout(xaxis_title='Jornada', yaxis_title='Acciones')
        st.plotly_chart(fig, use_container_width=True)

def analizar_efectividad_jugadores(df):
    """Analiza y visualiza la efectividad de los jugadores"""
    st.header("🎯 Efectividad por Jugador")
    
    df_efectividad = df.groupby('Ejecutor').agg(
        Acciones=('Acción', 'count'),
        Goles=('Gol', lambda x: (x == 'Sí').sum()),
        Efectividad=('Gol', lambda x: (x == 'Sí').mean() * 100)
    ).sort_values('Goles', ascending=False).reset_index()
    
    cols = st.columns([3, 2])
    
    with cols[0]:
        fig = px.bar(
            df_efectividad.head(10),
            x='Ejecutor',
            y=['Goles', 'Acciones'],
            title="Top 10 Jugadores",
            labels={'value': 'Cantidad', 'variable': 'Métrica'},
            barmode='group',
            color_discrete_sequence=['#4ECDC4', '#FF6B6B']
        )
        fig.update_layout(xaxis={'categoryorder': 'total descending'})
        st.plotly_chart(fig, use_container_width=True)
    
    with cols[1]:
        st.dataframe(
            df_efectividad.style
                .background_gradient(cmap='Blues', subset=['Acciones'])
                .background_gradient(cmap='Greens', subset=['Goles'])
                .format({'Efectividad': '{:.1f}%'}),
            height=500
        )

def visualizar_tipos_ejecucion(df):
    """Muestra la distribución de tipos de ejecución"""
    st.header("📊 Tipos de Ejecución")
    
    df_tipos = df['Tipo Ejecución'].value_counts().reset_index(name='Count')
    
    fig = px.bar(
        df_tipos,
        x='Count',
        y='Tipo Ejecución',
        orientation='h',
        title="Distribución por tipo de ejecución",
        labels={'Count': 'Acciones'},
        color='Count',
        color_continuous_scale='Teal'
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

def analizar_contactos(df):
    """Analiza y visualiza los contactos del balón"""
    st.header("👣 Análisis de Contactos")
    
    contactos = pd.concat([
        df['Primer Contacto'].rename('Contacto'),
        df['Segundo Contacto'].rename('Contacto')
    ]).dropna()
    
    if not contactos.empty:
        cols = st.columns(2)
        
        with cols[0]:
            fig = px.pie(
                contactos.value_counts().reset_index(name='Count'),
                names='Contacto',
                values='Count',
                title="Distribución de contactos",
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with cols[1]:
            st.dataframe(
                contactos.value_counts().reset_index(name='Conteo'),
                height=300
            )
    else:
        st.warning("No hay datos de contactos con los filtros actuales")

def configurar_descarga(df):
    """Configura el botón de descarga de datos"""
    st.divider()
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "💾 Descargar datos filtrados",
        data=csv,
        file_name="analisis_tactico.csv",
        mime="text/csv",
        help="Descargue los datos actualmente filtrados en formato CSV"
    )

def main():
    """Función principal que orquesta el dashboard"""
    st.set_page_config(layout="wide", page_title="Análisis Táctico")
    st.title("📊 Panel de Análisis Táctico")
    
    # Carga de datos
    with st.spinner("Cargando datos..."):
        df = cargar_datos()
        if df.empty:
            st.error("No se pudieron cargar los datos. Verifique la conexión o el formato del archivo.")
            return
    
    # Configuración de filtros
    df_filtrado, equipo_analisis = configurar_filtros(df)
    
    if df_filtrado.empty:
        st.warning("No hay datos con los filtros seleccionados. Ajuste los parámetros e intente nuevamente.")
        return
    
    # Visualización del dashboard
    st.subheader(f"Análisis para {equipo_analisis}")
    mostrar_metricas_clave(df_filtrado, equipo_analisis)
    
    with st.expander("🗺️ Mapas Tácticos", expanded=True):
        generar_seccion_espacial(df_filtrado)
    
    with st.expander("⏳ Análisis Temporal"):
        visualizar_distribucion_temporal(df_filtrado)
    
    with st.expander("🎯 Efectividad"):
        analizar_efectividad_jugadores(df_filtrado)
    
    with st.expander("📊 Tipos de Ejecución"):
        visualizar_tipos_ejecucion(df_filtrado)
    
    with st.expander("👣 Contactos"):
        analizar_contactos(df_filtrado)
    
    configurar_descarga(df_filtrado)

if __name__ == "__main__":
    main()
