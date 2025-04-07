import streamlit as st
import pandas as pd

def evolucion_page(lang):
    st.title("📈 Evolución de Métricas" if lang == "es" else "📈 Metrics Evolution")
    st.markdown("Compara métricas de partidos entre temporadas." if lang == "es" else "Compare match metrics across seasons.")

    # Cargar datos
    try:
        df_2023 = pd.read_excel("Cavalry2023stats.xlsx")
        df_2024 = pd.read_excel("Cavalry2024stats.xlsx")
    except Exception as e:
        st.error(f"Error cargando archivos: {str(e)}")
        return

    # Mostrar columnas para debug
    with st.expander("🧪 Ver columnas de ambos archivos"):
        st.write("2023:", df_2023.columns.tolist())
        st.write("2024:", df_2024.columns.tolist())

    # Identificar columnas comparables (comunes)
    columnas_metricas = [col for col in df_2023.columns if col in df_2024.columns and df_2023[col].dtype != 'O']

    if not columnas_metricas:
        st.error("No hay métricas numéricas comunes entre ambos archivos.")
        return

    metrica = st.selectbox(
        "Selecciona una métrica a comparar" if lang == "es" else "Select a metric to compare",
        columnas_metricas
    )

    # Mostrar valor promedio 2023 y última fila 2024 (supongamos que es el partido reciente)
    valor_2023 = df_2023[metrica].mean()
    valor_2024 = df_2024[metrica].iloc[-1]

    st.subheader(f"{metrica}")
    st.metric("Promedio 2023", round(valor_2023, 2))
    st.metric("Último partido 2024", round(valor_2024, 2))
    st.metric("Cambio", f"{(valor_2024 - valor_2023):+.2f}")

    # Gráfico de barras comparativo
    st.bar_chart(pd.DataFrame({
        "Promedio 2023": [valor_2023],
        "Último 2024": [valor_2024]
    }, index=[metrica]))
