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
    mostrar_ranking_parte_cuerpo(df_filtrado)

def cargar_datos():
    # Cargar datos desde GitHub
    url = "https://raw.githubusercontent.com/felipeorma/abp/refs/heads/main/master_abp.csv"
    df = pd.read_csv(url)
    
    # Convertir y formatear fechas
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    df = df.dropna(subset=['Fecha'])
    df['Fecha_Str'] = df['Fecha'].dt.strftime('%Y-%m-%d')  # Nuevo campo formateado
    
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
        
        # Diccionario de abreviaciones para equipos
        ABREVIACIONES = {
            "York United FC": "YOR",
            "Vancouver FC": "VAN",
            "Pacific FC": "PAC",
            "Atlético Ottawa": "OTT",
            "Forge FC": "FOR",
            "HFX Wanderers FC": "HFX",
            "Valour FC": "VAL"
        }
        
        # Procesar fechas y partidos
        df = df.sort_values('Fecha', ascending=False)
        df['Fecha_str'] = df['Fecha'].dt.strftime('%d %b')  # Formato: 15 Mar
        df['Rival_abr'] = df['Rival'].map(ABREVIACIONES).fillna(df['Rival'])
        df['Partido'] = df.apply(lambda x: f"{x['Fecha_str']} vs {x['Rival_abr']}", axis=1)
        
        # Selector compacto de partidos
        partidos_seleccionados = st.multiselect(
            "Seleccionar partidos:",
            options=df['Partido'].unique(),
            default=df['Partido'].unique(),
            format_func=lambda x: x,
            help="Selecciona uno o múltiples partidos (ordenados del más reciente)"
        )
        
        # Filtros principales en columnas compactas
        col1, col2 = st.columns(2)
        with col1:
            jornadas = st.multiselect(
                "Jornada:",
                options=df['Jornada'].unique(),
                default=df['Jornada'].unique()
            )
        with col2:
            condicion = st.multiselect(
                "Condición:",
                options=df['Condición'].unique(),
                default=df['Condición'].unique()
            )

        # Filtros secundarios
        col3, col4 = st.columns(2)
        with col3:
            acciones = st.multiselect(
                "Acciones:",
                options=df['Acción'].unique(),
                default=df['Acción'].unique()
            )
        with col4:
            jugadores = st.multiselect(
                "Jugadores:",
                options=df['Ejecutor'].unique(),
                default=df['Ejecutor'].unique()
            )

        # Slider compacto
        min_min, max_min = int(df['Minuto'].min()), int(df['Minuto'].max())
        rango_minutos = st.slider(
            "Minutos:",
            min_min, max_min,
            (min_min, max_min)
        )
        
    # Aplicar filtros
    return df[
        (df['Partido'].isin(partidos_seleccionados)) &
        (df['Jornada'].isin(jornadas)) &
        (df['Condición'].isin(condicion)) &
        (df['Acción'].isin(acciones)) &
        (df['Ejecutor'].isin(jugadores)) &
        (df['Minuto'].between(*rango_minutos))
    ]

def mostrar_kpis(df):
    cols = st.columns(5)  # Cambiamos de 4 a 5 columnas para meter la nueva métrica
    
    with cols[0]:
        st.metric("📈 Acciones registradas", df.shape[0])
    
    goles_favor = df[(df['Gol'] == 'Sí') & (df['Equipo'] == 'Cavalry FC')].shape[0]
    with cols[1]:
        st.metric("✅ Goles a favor", goles_favor, 
                 help="Goles convertidos por Cavalry FC")
    
    goles_contra = df[(df['Gol'] == 'Sí') & (df['Equipo'] != 'Cavalry FC')].shape[0]

    with cols[2]:
        st.metric("❌ Goles en contra", goles_contra, 
                 help="Goles concedidos al rival")
    
    eficacia = (goles_favor / df.shape[0] * 100) if df.shape[0] > 0 else 0
    with cols[3]:
        st.metric("🎯 Efectividad ofensiva", f"{eficacia:.1f}%",
                 help="Porcentaje de acciones que terminaron en gol a favor")
    
    eficacia_def = 100 - (goles_contra / df.shape[0] * 100) if df.shape[0] > 0 else 0
    with cols[4]:
        st.metric("🛡️ Efectividad defensiva", f"{eficacia_def:.1f}%",
                 help="Porcentaje de acciones que NO terminaron en gol en contra")

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

        # ✔️ Mejora visual: fondo + bordes en puntos
        fig.update_traces(marker=dict(line=dict(width=1, color='black')))
        fig.update_layout(
            plot_bgcolor='#F9F9F9',
            paper_bgcolor='#F9F9F9'
        )

        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Agrupar por Acción y Resultado
        df_sun = df.groupby(['Acción', 'Resultado']).size().reset_index(name='Cantidad')
        df_sun = df_sun[df_sun['Resultado'].notna()]  # quitar nulos

        total = df_sun['Cantidad'].sum()
        df_sun['Porcentaje'] = df_sun['Cantidad'] / total * 100

        # Agregar totales por Acción para nodos raíz
        df_accion = df_sun.groupby('Acción')['Cantidad'].sum().reset_index()
        df_accion['Resultado'] = 'Total'
        df_accion['Porcentaje'] = df_accion['Cantidad'] / total * 100

        # Unir y asegurar porcentaje
        df_sunburst = pd.concat([df_sun, df_accion], ignore_index=True)
        df_sunburst['Porcentaje'] = df_sunburst['Porcentaje'].fillna(0)

        fig = px.sunburst(
            df_sunburst,
            path=['Acción', 'Resultado'],
            values='Cantidad',
            title="Composición de Resultados por Acción",
            branchvalues='total',
            custom_data=['Cantidad', 'Porcentaje']
        )

        fig.update_traces(
            hovertemplate='<b>%{label}</b><br>' +
                          'Cantidad: %{customdata[0]}<br>' +
                          'Porcentaje: %{customdata[1]:.1f}%<extra></extra>'
        )

        st.plotly_chart(fig, use_container_width=True)


def mostrar_ranking_parte_cuerpo(df):
    st.header("🏅 Ranking por Parte del Cuerpo")

    # Clasificamos ofensiva/defensiva
    ACCIONES_OFENSIVAS = ['Córner', 'Tiro libre', 'Saque lateral', 'Penal', 'Centro', 'Remate']
    df['Tipo Acción'] = df['Acción'].apply(lambda x: 'Ofensiva' if x in ACCIONES_OFENSIVAS else 'Defensiva')

    # Colores personalizados
    color_map = {
        'Cabeza': '#00C2A0',
        'Pierna': '#FF5A5F',
        'Otro': '#4B4B4B'
    }

    for tipo in ['Ofensiva', 'Defensiva']:
        df_tipo = df[(df['Tipo Acción'] == tipo) & (df['Parte Cuerpo'].notna())]

        # Agrupamos por jugador y parte del cuerpo
        df_ranking = df_tipo.groupby(['Ejecutor', 'Parte Cuerpo']).size().reset_index(name='Cantidad')

        # Total por jugador para ordenar
        total_jugadores = df_ranking.groupby('Ejecutor')['Cantidad'].sum().sort_values(ascending=False)
        df_ranking['Ejecutor'] = pd.Categorical(df_ranking['Ejecutor'], categories=total_jugadores.index, ordered=True)

        st.subheader(f"{'⚔️' if tipo == 'Ofensiva' else '🛡️'} Acciones {tipo}s")

        fig = px.bar(
    df_ranking,
    x='Cantidad',
    y='Ejecutor',
    color='Parte Cuerpo',
    orientation='h',
    text='Cantidad',
    title=f"Jugadores con más acciones {tipo.lower()}s por parte del cuerpo",
    labels={'Cantidad': 'Acciones', 'Ejecutor': 'Jugador'},
    color_discrete_map=color_map,
    category_orders={'Ejecutor': total_jugadores.index.tolist()}
        )
        fig.update_layout(barmode='stack')
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

