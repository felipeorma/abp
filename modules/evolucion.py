import streamlit as st
import pandas as pd

def evolucion_page(lang):
    st.title("📈 Metrics Evolution by Round")

    st.markdown(
        "Compare metrics between matches from different rounds using benchmarks from previous seasons."
    )

    # Load data
    try:
        df_2023 = pd.read_excel("Cavalry2023stats.xlsx")
        df_2024 = pd.read_excel("Cavalry2024stats.xlsx")
    except Exception as e:
        st.error(f"Error loading files: {str(e)}")
        return

    # Validate required columns
    if 'Round' not in df_2024.columns or 'Match' not in df_2024.columns:
        st.error("The 2024 file must contain both 'Round' and 'Match' columns.")
        return

    # --- KPI Benchmarks from 2023 ---
    st.subheader("📊 2023 Season Benchmarks")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Avg xG", round(df_2023['xG'].mean(), 2) if 'xG' in df_2023.columns else "N/A")
    with col2:
        st.metric("Avg PPDA", round(df_2023['PPDA'].mean(), 2) if 'PPDA' in df_2023.columns else "N/A")
    with col3:
        st.metric("Avg Possession", f"{round(df_2023['Possession'].mean(), 1)}%" if 'Possession' in df_2023.columns else "N/A")

    # --- Round & Match Selection ---
    rounds = sorted(df_2024['Round'].unique())
    round_1 = st.selectbox("📅 Select First Round", rounds, index=0)
    round_2 = st.selectbox("📅 Select Second Round", rounds, index=1 if len(rounds) > 1 else 0)

    matches_r1 = df_2024[df_2024['Round'] == round_1]
    matches_r2 = df_2024[df_2024['Round'] == round_2]

    match_1 = st.selectbox(f"🆚 Match from Round {round_1}", matches_r1["Match"].tolist())
    match_2 = st.selectbox(f"🆚 Match from Round {round_2}", matches_r2["Match"].tolist())

    # Select metric to compare
    metric_columns = [col for col in df_2023.columns if col in df_2024.columns and df_2023[col].dtype != 'O']
    selected_metric = st.selectbox("📈 Select metric to compare", metric_columns)

    # Extract values
    val_1 = matches_r1[matches_r1["Match"] == match_1][selected_metric].values[0]
    val_2 = matches_r2[matches_r2["Match"] == match_2][selected_metric].values[0]
    avg_2023 = df_2023[selected_metric].mean()

    # Display metrics
    st.subheader(f"🔍 Comparison: {selected_metric}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(match_1, round(val_1, 2))
    with col2:
        st.metric(match_2, round(val_2, 2))
    with col3:
        st.metric("Difference", f"{(val_2 - val_1):+.2f}")

    # Bar chart
    df_chart = pd.DataFrame({
        match_1: [val_1],
        match_2: [val_2],
        "2023 Avg": [avg_2023]
    }, index=[selected_metric])

    st.bar_chart(df_chart.T)
