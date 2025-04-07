import streamlit as st
import pandas as pd
import os

def evolucion_page(lang):
    st.title("📈 Evolución de Métricas" if lang == "es" else "📈 Metrics Evolution")

    st.markdown("Compara métricas clave entre temporadas." if lang == "es" else "Compare key metrics across seasons.")

    # Cargar datos
    try:
        df_2023 = pd.read_excel("Cavalry2023stats.xlsx")
        df_2024 = pd.read_excel("Cavalry2024stats.xlsx")
    except Exception as e:
        st.error(f"Error cargando archivos: {str(e)}")
        return

    # Selección de métrica
    metrica = st.selectbox(
        "Selecciona una métrica" if lang == "es" else "Select a metric",
        [col for col in df_2023.columns if col in df_2024.columns and col not in ["Jugador", "Nombre", "Name"]]
    )

    # Selección de jugador
    jugador = st.selectbox(
        "Selecciona un jugador" if lang == "es" else "Select a player",
        df_2023["Jugador"] if "Jugador" in df_2023.columns else df_2023["Name"]
    )

    col_jugador = "Jugador" if "Jugador" in df_2023.columns else "Name"

    # Extraer valores
    valor_2023 = df_2023[df_2023[col_jugador] == jugador][metrica].values[0]
    valor_2024 = df_2024[df_2024[col_jugador] == jugador][metrica].values[0]

    # Mostrar comparación
    st.subheader(f"{metrica} - {jugador}")
    st.metric("2023", round(valor_2023, 2))
    st.metric("2024", round(valor_2024, 2))
    diff = valor_2024 - valor_2023
    st.metric("Cambio", f"{diff:+.2f}")

    # Gráfico simple de barras
    st.bar_chart(pd.DataFrame({
        "Temporada 2023": [valor_2023],
        "Temporada 2024": [valor_2024]
    }, index=[metrica]))

