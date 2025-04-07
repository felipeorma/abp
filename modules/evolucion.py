import streamlit as st
import pandas as pd

def evolucion_page(lang):
    st.title("📈 Metrics Evolution")

    st.markdown(
        "Compare a match from the current season with a past season benchmark to analyze tactical evolution."
    )

    # Load data
    try:
        df_2023 = pd.read_excel("Cavalry2023stats.xlsx")
        df_2024 = pd.read_excel("Cavalry2024stats.xlsx")
    except Exception as e:
        st.error(f"Error loading files: {str(e)}")
        return

    # Validate required columns
    if 'Match' not in df_2023.columns or 'Match' not in df_2024.columns:
        st.error("Both files must contain a 'Match' column.")
        return

    # --- KPI Benchmarks from 2023 ---
    st.subheader("📊 2023 Season Averages")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Avg xG", round(df_2023['xG'].mean(), 2) if 'xG' in df_2023.columns else "N/A")
    with col2:
        st.metric("Avg PPDA", round(df_2023['PPDA'].mean(), 2) if 'PPDA' in df_2023.columns else "N/A")
    with col3:
        st.metric("Avg Possession", f"{round(df_2023['Possession'].mean(), 1)}%" if 'Possession' in df_2023.columns else "N/A")

    # --- Match selection ---
    match_2023 = st.selectbox("📅 Select a match from 2023 season", df_2023["Match"].tolist())
    match_2024 = st.selectbox("📅 Select a match from current season (2024)", df_2024["Match"].tolist())

    # Select metric
    metric_columns = [col for col in df_2023.columns if col in df_2024.columns and df_2023[col].dtype != 'O']
    selected_metric = st.selectbox("📈 Select metric to compare", metric_columns)

    # Extract values
    val_2023 = df_2023[df_2023["Match"] == match_2023][selected_metric].values[0]
    val_2024 = df_2024[df_2024["Match"] == match_2024][selected_metric].values[0]
    avg_2023 = df_2023[selected_metric].mean()

    # Display comparison
    st.subheader(f"🔍 Metric: {selected_metric}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(match_2023, round(val_2023, 2))
    with col2:
        st.metric(match_2024, round(val_2024, 2))
    with col3:
        st.metric("Difference", f"{(val_2024 - val_2023):+.2f}")

    # Bar chart
    df_chart = pd.DataFrame({
        match_2023: [val_2023],
        match_2024: [val_2024],
        "2023 Avg": [avg_2023]
    }, index=[selected_metric])

    st.bar_chart(df_chart.T)

