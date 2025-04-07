import streamlit as st
import pandas as pd

def evolucion_page(lang):
    st.title("📈 Evolución de Métricas por Jornada" if lang == "es" else "📈 Match Metrics Evolution by Round")

    st.markdown(
        "Compara partidos de diferentes jornadas con referencia a las temporadas anteriores." 
        if lang == "es" 
        else "Compare matches from different rounds using historical season benchmarks."
    )

    # Cargar archivos
    try:
        df_2023 = pd.read_excel("Cavalry2023stats.xlsx")
        df_2024 = pd.read_excel("Cavalry2024stats.xlsx")
    except Exception as e:
        st.error(f"Error cargando archivos: {str(e)}")
        return

    # Verificar que exista la columna 'Jornada'
    if 'Jornada' not in df_2024.columns:
        st.error("El archivo 2024 necesita una columna llamada 'Jornada' para esta funcionalidad.")
        return

    # Mostrar KPIs generales de referencia (encabezado)
    st.subheader("📊 KPIs Temporada 2023")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("xG Promedio", round(df_2023['xG'].mean(), 2) if 'xG' in df_2023.columns else "N/A")
    with col2:
        st.metric("PPDA Promedio", round(df_2023['PPDA'].mean(), 2) if 'PPDA' in df_2023.columns else "N/A")
    with col3:
        st.metric("Posesión Promedio", f"{round(df_2023['Posesión'].mean(), 1)}%" if 'Posesión' in df_2023.columns else "N/A")

    # Selección de dos jornadas y partidos
    jornadas = sorted(df_2024['Jornada'].unique())
    jornada_1 = st.selectbox("📅 Selecciona la primera jornada", jornadas, index=0)
    jornada_2 = st.selectbox("📅 Selecciona la segunda jornada", jornadas, index=1 if len(jornadas) > 1 else 0)

    partidos_j1 = df_2024[df_2024['Jornada'] == jornada_1]
    partidos_j2 = df_2024[df_2024['Jornada'] == jornada_2]

    # Identificar columnas de referencia para identificar el partido (fecha, rival, etc.)
    cols_identificadoras = [col for col in ['Fecha', 'Rival', 'Local'] if col in df_2024.columns]
    col_ref = cols_identificadoras[0] if cols_identificadoras else df_2024.columns[0]

    partido_1 = st.selectbox(f"🆚 Partido de Jornada {jornada_1}", partidos_j1[col_ref].tolist())
    partido_2 = st.selectbox(f"🆚 Partido de Jornada {jornada_2}", partidos_j2[col_ref].tolist())

    # Selección de métrica
    columnas_metricas = [col for col in df_2023.columns if col in df_2024.columns and df_2023[col].dtype != 'O']
    metrica = st.selectbox("📈 Métrica a comparar", columnas_metricas)

    # Obtener valores de cada partido
    val_1 = partidos_j1[partidos_j1[col_ref] == partido_1][metrica].values[0]
    val_2 = partidos_j2[partidos_j2[col_ref] == partido_2][metrica].values[0]
    promedio_2023 = df_2023[metrica].mean()

    # Mostrar métricas comparadas
    st.subheader(f"🔍 Comparativa de {metrica}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(partido_1, round(val_1, 2))
    with col2:
        st.metric(partido_2, round(val_2, 2))
    with col3:
        diferencia = val_2 - val_1
        st.metric("Diferencia", f"{diferencia:+.2f}")

    # Gráfico comparativo
    df_chart = pd.DataFrame({
        f"{partido_1}": [val_1],
        f"{partido_2}": [val_2],
        "Promedio 2023": [promedio_2023]
    }, index=[metrica])

    st.bar_chart(df_chart.T)
