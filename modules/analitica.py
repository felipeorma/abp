import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from mplsoccer import VerticalPitch
from datetime import datetime
import requests
from io import BytesIO

# Carga de datos desde GitHub con validación robusta
def cargar_datos():
    try:
        url = "https://raw.githubusercontent.com/felipeorma/abp/main/master_abp.csv"
        df = pd.read_csv(url)

        # Conversión de tipos
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df['Minuto'] = pd.to_numeric(df['Minuto'], errors='coerce')
        df['Gol'] = df['Gol'].apply(lambda x: 'Sí' if str(x).lower() in ['sí', 'si', '1', 'true'] else 'No')

        # Eliminar datos incompletos claves
        df = df.dropna(subset=['Zona Saque', 'Zona Remate', 'Ejecutor', 'Fecha'])

        return df

    except Exception as e:
        st.error(f"⛔ Error cargando datos: {str(e)}")
        return pd.DataFrame()

# Filtros
def configurar_filtros(df):
    with st.sidebar:
        st.header("🔍 Filtros Avanzados")

        jornadas = sorted(df['Jornada'].unique())
        jornadas_sel = st.multiselect("Jornada", options=jornadas, default=jornadas)

        fechas_disponibles = df[df['Jornada'].isin(jornadas_sel)]['Fecha'].unique()
        fechas_formateadas = [
            f"{fecha.strftime('%d/%m')} vs {df[df['Fecha'] == fecha]['Rival'].iloc[0]}" 
            for fecha in sorted(fechas_disponibles, reverse=True)
        ]
        fechas_sel = st.multiselect("Partidos", options=fechas_formateadas, default=fechas_formateadas)

        fechas_a_filtrar = [
            fecha for i, fecha in enumerate(sorted(fechas_disponibles, reverse=True))
            if fechas_formateadas[i] in fechas_sel
        ] if fechas_sel else fechas_disponibles

        col1, col2 = st.columns(2)
        with col1:
            condicion = st.multiselect("Condición", options=df['Condición'].unique(), default=df['Condición'].unique())
        with col2:
            equipos = st.multiselect("Equipo", options=df['Equipo'].unique(), default=df['Equipo'].unique())

        acciones = st.multiselect("Acciones", options=df['Acción'].unique(), default=df['Acción'].unique())
        jugadores = st.multiselect("Jugadores", options=df['Ejecutor'].unique(), default=df['Ejecutor'].unique())

        min_min = int(df['Minuto'].min())
        max_min = int(df['Minuto'].max())
        rango_minutos = st.slider("Rango de minutos", min_min, max_min, (min_min, max_min))

    return df[
        (df['Jornada'].isin(jornadas_sel)) &
        (df['Fecha'].isin(fechas_a_filtrar)) &
        (df['Condición'].isin(condicion)) &
        (df['Equipo'].isin(equipos)) &
        (df['Acción'].isin(acciones)) &
        (df['Ejecutor'].isin(jugadores)) &
        (df['Minuto'].between(*rango_minutos))
    ]

# KPIs
def mostrar_kpis(df):
    cols = st.columns(4)

    goles_favor = df[(df['Gol'] == 'Sí') & (df['Equipo'] == 'Cavalry FC')].shape[0]
    with cols[0]:
        st.metric("✅ Goles a favor", goles_favor)

    goles_contra = df[(df['Gol'] == 'Sí') & (df['Equipo'] == 'Rival')].shape[0]
    with cols[1]:
        st.metric("❌ Goles en contra", goles_contra)

    acciones_of = df[df['Equipo'] == 'Cavalry FC'].shape[0]
    eficacia_of = (goles_favor / acciones_of * 100) if acciones_of > 0 else 0
    with cols[2]:
        st.metric("🎯 Efectividad Ofensiva", f"{eficacia_of:.1f}%")

    acciones_def = df[df['Equipo'] == 'Rival'].shape[0]
    eficacia_def = (100 - (goles_contra / acciones_def * 100)) if acciones_def > 0 else 0
    with cols[3]:
        st.metric("🛡️ Efectividad Defensiva", f"{eficacia_def:.1f}%")

# Mapa de calor
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

def generar_seccion_espacial(df):
    st.header("🌍 Mapeo Táctico")
    col1, col2 = st.columns(2)
    with col1:
        generar_mapa_calor(df, tipo='saque')
    with col2:
        generar_mapa_calor(df, tipo='remate')

# Temporal
def generar_seccion_temporal(df):
    st.header("⏳ Evolución Temporal")
    col1, col2 = st.columns(2)

    with col1:
        fig = px.histogram(
            df, x='Jornada', color='Periodo',
            title="Acciones por Jornada"
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

# Efectividad por jugador
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

# Efectividad primer contacto
def generar_efectividad_contacto(df):
    st.header("🧠 Efectividad del Primer Contacto por Tipo de Jugada")

    df_filtrado = df[df['Equipo'] == 'Cavalry FC']
    resumen = df_filtrado.groupby(['Acción', 'Primer Contacto']).agg(
        Acciones=('Primer Contacto', 'count'),
        Goles=('Gol', lambda x: (x.astype(str).str.lower().isin(['sí', 'si', '1', 'true'])).sum())
    ).reset_index()
    resumen['Efectividad (%)'] = resumen['Goles'] / resumen['Acciones'] * 100

    fig = px.bar(
        resumen,
        x='Primer Contacto',
        y='Efectividad (%)',
        color='Acción',
        barmode='group',
        text=resumen['Efectividad (%)'].apply(lambda x: f"{x:.1f}%"),
        title="Efectividad del Primer Contacto por Tipo de Jugada",
        labels={'Primer Contacto': 'Tipo de Contacto'},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_traces(textposition='outside')
    fig.update_layout(xaxis_title="Primer Contacto", yaxis_title="Efectividad (%)")
    st.plotly_chart(fig, use_container_width=True)

# Descarga
def configurar_descarga(df):
    st.divider()
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📤 Exportar Dataset Filtrado",
        data=csv,
        file_name="analisis_tactico_cavalry.csv",
        mime="text/csv"
    )

# Página principal
def analitica_page():
    st.title("⚽ Panel de Análisis Táctico - Cavalry FC")

    df = cargar_datos()
    if df.empty:
        st.warning("⚠️ No hay datos disponibles.")
        return

    df_filtrado = configurar_filtros(df)
    if df_filtrado.empty:
        st.warning("🔍 No hay datos con los filtros seleccionados")
        return

    mostrar_kpis(df_filtrado)
    generar_seccion_espacial(df_filtrado)
    generar_seccion_temporal(df_filtrado)
    generar_seccion_efectividad_mejorada(df_filtrado)
    generar_efectividad_contacto(df_filtrado)
    configurar_descarga(df_filtrado)
