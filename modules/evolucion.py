import streamlit as st
import pandas as pd
import plotly.graph_objects as go

def evolucion_page(lang):
    st.title("📈 PPDA Evolution by Round")

    st.markdown(
        "Compare PPDA between a match from 2023 and one from the current season, selecting by round and match."
    )

    # Load data
    try:
        df_2023 = pd.read_excel("Cavalry2023stats.xlsx")
        df_2024 = pd.read_excel("Cavalry2024stats.xlsx")
    except Exception as e:
        st.error(f"Error loading files: {str(e)}")
        return

    # Validate columns
    for df, year in [(df_2023, "2023"), (df_2024, "2024")]:
        for col in ["Round", "Match", "PPDA"]:
            if col not in df.columns:
                st.error(f"The {year} file must contain a '{col}' column.")
                return

    # --- KPI Benchmarks ---
    st.subheader("📊 2023 Season Averages")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("xG", round(df_2023['xG'].mean(), 2) if 'xG' in df_2023.columns else "N/A")
    with col2:
        st.metric("PPDA", round(df_2023['PPDA'].mean(), 2))
    with col3:
        st.metric("Possession", f"{round(df_2023['Possession'].mean(), 1)}%" if 'Possession' in df_2023.columns else "N/A")

    # --- Select match from 2023 ---
    round_2023 = st.selectbox("📅 Select round from **2023 season**", sorted(df_2023["Round"].unique()))
    matches_2023 = df_2023[df_2023["Round"] == round_2023]
    match_2023 = st.selectbox("🆚 Select match", matches_2023["Match"].tolist())

    # --- Select match from 2024 ---
    round_2024 = st.selectbox("📅 Select round from **2024 season**", sorted(df_2024["Round"].unique()))
    matches_2024 = df_2024[df_2024["Round"] == round_2024]
    match_2024 = st.selectbox("🆚 Select match", matches_2024["Match"].tolist())

    # --- Extract values ---
    val_2023 = matches_2023[matches_2023["Match"] == match_2023]["PPDA"].values[0]
    val_2024 = matches_2024[matches_2024["Match"] == match_2024]["PPDA"].values[0]
    avg_2023 = df_2023["PPDA"].mean()

    # --- Show comparison ---
    st.subheader("🔍 Comparison of **PPDA**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(f"{match_2023} (2023)", round(val_2023, 2))
    with col2:
        st.metric(f"{match_2024} (2024)", round(val_2024, 2))
    with col3:
        st.metric("Difference", f"{(val_2024 - val_2023):+.2f}")

    # --- Plotly bar chart with Cavalry FC colors ---
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=["PPDA"],
        y=[val_2023],
        name=f"{match_2023} (2023)",
        text=[f"<b>{val_2023:.2f}</b>"],
        textposition='outside',
        marker_color="#C8102E"  # Rojo
    ))

    fig.add_trace(go.Bar(
        x=["PPDA"],
        y=[val_2024],
        name=f"{match_2024} (2024)",
        text=[f"<b>{val_2024:.2f}</b>"],
        textposition='outside',
        marker_color="#00843D"  # Verde
    ))

    fig.add_trace(go.Bar(
        x=["PPDA"],
        y=[avg_2023],
        name="2023 Season Avg",
        text=[f"<b>{avg_2023:.2f}</b>"],
        textposition='outside',
        marker_color="#000000"  # Negro
    ))

    fig.update_layout(
        barmode='group',
        title=dict(
            text="<b>PPDA Comparison by Round</b>",
            x=0.5,
            xanchor='center',
            font=dict(size=20)
        ),
        yaxis_title="<b>PPDA</b>",
        template="simple_white",
        height=500,
        margin=dict(t=80, b=60),
        legend=dict(orientation="h", y=-0.25, x=0.5, xanchor='center'),
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- Footer signature ---
    st.markdown(
        """
        <hr style='margin-top: 40px; margin-bottom: 10px'>
        <div style='text-align: center; font-size: 14px; color: gray;'>
            <strong>Felipe Ormazabal</strong> &nbsp;|&nbsp; Soccer Scout & Data Analyst
        </div>
        """,
        unsafe_allow_html=True
    )

