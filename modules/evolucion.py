import streamlit as st
import pandas as pd

def evolucion_page(lang):
    st.title("📈 Evolución de Métricas" if lang == "es" else "📈 Metrics Evolution")
    st.markdown("Compara métricas clave entre dos partidos y las temporadas anteriores." if lang == "es" else "Compare key metrics between matches and past seasons.")

    # Cargar datos
    try:
        df_2023 = pd.read_excel("Cavalry2023stats.xlsx")
        df_2024 = pd.read_excel("Cavalry2024stats.xlsx")
    except Exception as e:
        st.error(f"Error cargando archivos: {str(e)}")
        return

    # Detectar columnas numéricas comunes
    columnas_metricas = [col for col in df_2023.columns if col in df_2024.columns and df_2023[col].dtype != 'O']

    if not columnas_metricas:
        st.error("No hay métricas numéricas comunes entre ambos archivos.")
        return

    # Selección de partidos (suponiendo que hay una columna identificadora)
    columnas_identificadoras = [col for col in df_2024.columns if df_2024[col].dtype == 'O']
    partido_id_col = st.selectbox("Columna para identificar partidos", columnas_identificadoras)
    
    partidos_disponibles = df_2024[partido_id_col].tolist()
    partido_1 = st.selectbox("📊 Partido 1", partidos_disponibles, index=0)
    partido_2 = st.selectbox("📊 Partido 2", partidos_disponibles, index=1 if len(partidos_disponibles) > 1 else 0)

    # Selección de métrica a comparar
    metrica = st.selectbox("Selecciona una métrica a comparar", columnas_metricas)

    # KPIs Generales (encabezado)
    col1, col2, col3 = st.columns(3)
    with col1:
        if 'xG' in df_2023.columns:
            st.metric("Promedio xG temporadas", round(df_2023['xG'].mean(), 2))
    with col2:
        if 'PPDA' in df_2023.columns:
            st.metric("PPDA promedio", round(df_2023['PPDA'].mean(), 2))
    with col3:
        if 'Posesión' in df_2023.columns:
            st.metric("Posesión promedio", f"{round(df_2023['Posesión'].mean(), 1)}%")

    # Extraer valores de los partidos seleccionados
    val_1 = df_2024[df_2024[partido_id_col] == partido_1][metrica].values[0]
    val_2 = df_2024[df_2024[partido_id_col] == partido_2][metrica].values[0]
    val_avg_2023 = df_2023[metrica].mean()

    # Mostrar métricas comparativas
    st.subheader(f"{metrica}")
    st.metric(f"{partido_1}", round(val_1, 2))
    st.metric(f"{partido_2}", round(val_2, 2))
    st.metric("Cambio", f"{(val_2 - val_1):+.2f}")

    # Gráfico comparativo
    df_chart = pd.DataFrame({
        partido_1: [val_1],
        partido_2: [val_2],
        "Promedio 2023": [val_avg_2023]
    }, index=[metrica])

    st.bar_chart(df_chart.T)
