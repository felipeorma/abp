import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def evolucion_page(lang):
    st.title("📈 Metrics Evolution")

    st.markdown(
        "Compare a match from the current season with a match from last season to analyze tactical trends and performance evolution."
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
    st.subheader("📊 2023 Season Benchmarks")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔹 Avg xG", round(df_2023['xG'].mean(), 2) if 'xG' in df_2023.columns else "N/A")
    with col2:
        st.metric("🔸 Avg PPDA", round(df_2023['PPDA'].mean(), 2) if 'PPDA' in df_2023.columns else "N/A")
    with col3:
        st.metric("🔻 Avg Possession", f"{round(df_2023['Possession'].mean(), 1)}%" if 'Possession' in df_2023.columns else "N/A")

    # --- Match selection ---
    match_2023 = st.selectbox("📅 Select a match from **2023 season**", df_2023["Match"].tolist())
    match_2024 = st.selectbox("📅 Select a match from **current season (2024)**", df_2024["Match"].tolist())

    # --- Metric selection ---
    metric_columns = [col for col in df_2023.columns if col in df_2024.columns and df_2023[col].dtype != 'O']
    selected_metric = st.selectbox("📈 Select a metric to compare", metric_columns)

    # --- Extract values ---
    val_2023 = df_2023[df_2023["Match"] == match_2023][selected_metric].values[0]
    val_2024 = df_2024[df_2024["Match"] == match_2024][selected_metric].values[0]
    avg_2023 = df_2023[selected_metric].mean()

    # --- Metric Summary ---
    st.subheader(f"🔍 Comparison of **{selected_metric}**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"2023: {match_2023}", round(val_2023, 2))
    with col2:
        st.metric(f"2024: {match_2024}", round(val_2024, 2))
    with col3:
        st.metric("📉 Difference", f"{(val_2024 - val_2023):+.2f}")

    # --- Plotly bar chart ---
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=[selected_metric],
        y=[val_2023],
        name=f"{match_2023} (2023)",
        text=[f"<b>{val_2023:.2f}</b>"],
        textposition='outside',
        marker_color="#1f77b4"  # azul
    ))

    fig.add_trace(go.Bar(
        x=[selected_metric],
        y=[val_2024],
        name=f"{match_2024} (2024)",
        text=[f"<b>{val_2024:.2f}</b>"],
        textposition='outside',
        marker_color="#ff7f0e"  # naranja
    ))

    fig.add_trace(go.Bar(
        x=[selected_metric],
        y=[avg_2023],
        name="2023 Season Avg",
        text=[f"<b>{avg_2023:.2f}</b>"],
        textposition='outside',
        marker_color="#7f7f7f"  # gris
    ))

    fig.update_layout(
        barmode='group',
        title=dict(
            text=f"<b>Metric Comparison: {selected_metric}</b>",
            x=0.5,
            xanchor='center',
            font=dict(size=20)
        ),
        yaxis_title=f"<b>{selected_metric}</b>",
        template="simple_white",
        height=500,
        margin=dict(t=80, b=60),
        legend=dict(orientation="h", y=-0.25, x=0.5, xanchor='center'),
    )

    st.plotly_chart(fig, use_container_width=True)
